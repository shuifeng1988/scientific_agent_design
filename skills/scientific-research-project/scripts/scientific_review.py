"""Version-bound scientific review receipts. Checks accountability, not scientific truth."""
from pathlib import Path
import argparse
import hashlib
import json
from research_workflow import read, receipt, descriptor, require, text, inside

POLICY = 'independent_review_v1'
CRITERIA = {
    'design': ('question_method', 'primary_evidence', 'contrary_evidence', 'analysis_units',
               'controls_statistics', 'feasibility', 'task_outputs'),
    'result': ('methods_validity', 'data_denominators', 'statistics_uncertainty',
               'claim_evidence', 'contrary_explanations', 'figures_tables', 'downstream_impact'),
}


class ReviewPending(ValueError):
    """Human/scientific work is pending; do not spend technical repair budgets."""


def subject_hash(subject):
    return hashlib.sha256(json.dumps(subject, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def design_subject(root, proposal_path):
    root, proposal_path = Path(root).resolve(), Path(proposal_path).resolve()
    p = read(proposal_path)
    appraisal = read(receipt(root, p['appraisal']))
    targets = [descriptor(proposal_path, root), p['appraisal']]
    targets += [s['evidence'] for s in appraisal['searches']]
    return dict(stage='design', plan_version=p['version'], author_invocation_id=text(p.get('author_invocation_id'),
                'proposal.author_invocation_id'), targets=targets)


def result_subject(root, task_id, result_path, run_id):
    root = Path(root).resolve(); result = inside(root, result_path)
    r = read(result / '_evidence/report_receipt.json')
    m = read(receipt(result, r['manifest']))
    require(m['task_id'] == task_id and m['run_id'] == run_id, 'review task/run mismatch')
    targets = [descriptor(receipt(result, a), root) for a in r['artifacts']]
    targets += [descriptor(result / p, root) for p in
                (r['manifest']['path'], '_evidence/report_receipt.json', '_evidence/reflection.json')]
    targets += [{k: a[k] for k in ('path', 'sha256')} for a in m['inputs']]
    return dict(stage='result', plan_version=m['plan_version'], task_id=task_id, run_id=run_id,
                author_invocation_id=text(m.get('author_invocation_id'), 'report.author_invocation_id'), targets=targets)


def verify(root, review_path, subject, accepted=True):
    root = Path(root).resolve(); review_path = Path(review_path).resolve()
    require(review_path.is_relative_to(root), 'review outside project')
    require(review_path.is_file(), 'scientific review receipt missing')
    r = read(review_path)
    require(r.get('schema_version') == 1 and r.get('subject') == subject, 'stale/wrong scientific review subject')
    for a in subject['targets']:
        receipt(root, a)
    reviewer = text(r.get('reviewer_invocation_id'), 'reviewer invocation')
    require(reviewer != subject['author_invocation_id'], 'independent review cannot use author invocation')
    invocation = read(receipt(root, r['invocation']))
    require(invocation.get('invocation_id') == reviewer and invocation.get('role') == 'reviewer'
            and invocation.get('subject_sha256') == subject_hash(subject), 'review invocation/subject mismatch')
    for k in ('provider', 'started_at', 'completed_at'):
        text(invocation.get(k), 'review invocation.' + k)
    receipt(root, invocation['transcript'])
    criteria = r.get('criteria', {})
    require(set(criteria) == set(CRITERIA[subject['stage']]), 'scientific review criteria incomplete')
    for name, c in criteria.items():
        require(c.get('verdict') in ('adequate', 'revise', 'needs_user'), 'invalid criterion verdict')
        text(c.get('rationale'), 'criterion rationale')
        require(c.get('evidence'), 'criterion evidence required')
        for a in c['evidence']:
            receipt(root, a)
    findings = r.get('findings')
    require(isinstance(findings, list), 'findings list required; empty is allowed')
    seen = set()
    for f in findings:
        identifier = text(f.get('id'), 'finding id')
        require(identifier not in seen, 'duplicate finding'); seen.add(identifier)
        require(f.get('severity') in ('critical', 'major', 'minor') and f.get('status') in ('open', 'resolved'),
                'invalid finding severity/status')
        text(f.get('rationale'), 'finding rationale')
        require(f.get('evidence'), 'finding evidence required')
        for a in f['evidence']: receipt(root, a)
        if f['status'] == 'resolved':
            text(f.get('resolution', {}).get('rationale'), 'resolution rationale')
            require(f['resolution'].get('evidence'), 'resolution evidence required')
            for a in f['resolution']['evidence']: receipt(root, a)
    require(r.get('verdict') in ('adequate', 'revise', 'needs_user'), 'invalid review verdict')
    if accepted:
        require(r['verdict'] == 'adequate' and all(c['verdict'] == 'adequate' for c in criteria.values()),
                'scientific review requests revision/user decision')
        require(not any(f['severity'] in ('critical', 'major') and f['status'] == 'open' for f in findings),
                'unresolved major scientific finding')
    return r


def result_gate(root, task_id, result_path, run_id):
    from research_workflow import design_for_version
    root = Path(root).resolve(); result = inside(root, result_path)
    m = read(result / '_evidence/report.json')
    design = design_for_version(root, m['plan_version'], task_id)
    if design.get('review_policy') != POLICY:
        return  # Existing baselines keep their explicit legacy behavior.
    try:
        require(read(result / '_evidence/reflection.json').get('decision') != 'needs_user',
                'scientific hold prevents publication')
        subject = result_subject(root, task_id, result_path, run_id)
        verify(root, result / '_evidence/scientific_review.json', subject)
        from supplementary_tasks import verify_supplements
        verify_supplements(root, task_id, read(result / '_evidence/reflection.json'))
    except (ValueError, KeyError, OSError, TypeError) as exc:
        raise ReviewPending(str(exc)) from exc


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=('subject', 'check'))
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--stage', choices=('design', 'result'), required=True)
    ap.add_argument('--proposal', type=Path)
    ap.add_argument('--task-id'); ap.add_argument('--run-id'); ap.add_argument('--review', type=Path)
    a = ap.parse_args()
    if a.stage == 'design':
        s = design_subject(a.root, a.proposal)
    else:
        from research_workflow import task
        s = result_subject(a.root, a.task_id, task(a.root, a.task_id)['result_path'], a.run_id)
    out = dict(subject=s, subject_sha256=subject_hash(s))
    if a.mode == 'check': out = verify(a.root, a.review, s)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
