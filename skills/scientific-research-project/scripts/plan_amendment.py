"""Apply an approved, reviewed plan version without rewriting completed evidence.

The daemon must be paused and have no live/unknown or unfinished attempted jobs.
A durable journal permits rollback before commit, or event retry after commit.
"""
import argparse
import copy
import fcntl
import hashlib
import json
from pathlib import Path
from contextlib import contextmanager
from research_workflow import (ROOT_DOCS, TASK_FIELDS, atomic, read, sha, receipt, descriptor,
                               require, text, inside, registry, tasks_table, validate_tasks,
                               validate_appraisal, verify_design)
from scientific_review import POLICY, design_subject, verify

JOURNAL = 'provenance/amendment_transaction.json'


@contextmanager
def daemon_lock(root):
    p = root / 'provenance/supervisor/daemon.lock'; p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


@contextmanager
def event_lock(root):
    p = root / 'provenance/event.lock'; p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def restore(root, journal):
    for name, contents in journal['before'].items():
        p = inside(root, name)
        if contents is None:
            if p.exists(): p.unlink()
        else: atomic(p, contents)


def finish(root, journal):
    from project_events import emit
    emit(root, dict(event_type='plan.amendment.approved', verified=True,
         **journal['approval'], message=journal['reason'],
         meta={'supervisor_event': 'amendment-' + journal['proposal_sha256']}))
    atomic(root / journal['receipt_path'], dict(stage='applied', version=journal['version'],
           proposal_sha256=journal['proposal_sha256'], approval=journal['approval'],
           previous_design=journal['previous_design'], reason=journal['reason']))
    (root / JOURNAL).unlink()
    return dict(applied=True, version=journal['version'], service_restarted=False)


def recover(root):
    root = Path(root).resolve()
    with daemon_lock(root):
        journal = read(root / JOURNAL)
        if journal['stage'] == 'committed':
            verify_design(root)
            return finish(root, journal)
        require(journal['stage'] == 'prepared', 'unknown amendment transaction state')
        with event_lock(root):
            restore(root, journal)
            (root / JOURNAL).unlink()
        return dict(rolled_back=True, service_restarted=False)


def apply(root, proposal_path, approval_path, review_path):
    root = Path(root).resolve()
    proposal_path, approval_path, review_path = [Path(p).resolve() for p in (proposal_path, approval_path, review_path)]
    require(all(p.is_relative_to(root) for p in (proposal_path, approval_path, review_path)), 'amendment inputs outside project')
    with daemon_lock(root):
        require(not (root / JOURNAL).exists(), 'recover previous amendment transaction first')
        with event_lock(root):
            verify_design(root)
            dpath = root / 'registry/design.json'; old = read(dpath)
            p, approval = read(proposal_path), read(approval_path)
            versions = {old['version']} | {h['version'] for h in old.get('history', [])}
            require(text(p.get('version'), 'plan version') not in versions, 'plan version must be new')
            amend = p.get('amendment', {})
            require(amend.get('base_design_sha256') == sha(dpath), 'stale amendment base')
            text(amend.get('reason'), 'amendment reason')
            require(p.get('review_policy') == POLICY, 'amendments require independent scientific review')
            require(set(p.get('documents', {})) == set(ROOT_DOCS), 'exactly five proposed documents required')
            for value in p['documents'].values(): text(value, 'proposed document')
            validate_tasks(root, p['tasks'], p['documents']['00_PROJECT.md'], p['documents']['01_PLAN.md'])
            appraisal = validate_appraisal(root, p['appraisal'])
            require(appraisal.get('status') == 'ready_for_design_review', 'amendment appraisal not ready')
            require(approval.get('decision') == 'approved' and approval.get('proposal_sha256') == sha(proposal_path)
                    and approval.get('appraisal_sha256') == p['appraisal']['sha256'], 'approval does not cover amendment')
            for k in ('actor', 'recorded_at', 'message'): text(approval.get(k), 'approval.' + k)
            receipt(root, approval['evidence'])
            verify(root, review_path, design_subject(root, proposal_path))
            previous_rows = registry(root); previous = {t['task_id']: t for t in previous_rows}
            proposed = {t['task_id']: t for t in p['tasks']}
            require(set(previous) <= set(proposed), 'amendment must preserve existing task IDs')
            for i, row in previous.items():
                require(all(proposed[i][k] == row[k] for k in TASK_FIELDS),
                        'existing task identity/mapping is immutable; use a new task for replacement science')
            affected = amend.get('affected_task_ids')
            require(isinstance(affected, list) and len(affected) == len(set(affected))
                    and set(affected) <= set(proposed), 'explicit affected_task_ids required')
            require(set(proposed) - set(previous) <= set(affected), 'new tasks must be declared affected')
            completed = {i for i, t in previous.items() if t['status'] in ('complete', 'frozen')}
            require(not completed.intersection(affected), 'completed tasks are preserved; add a new task for new science')
            cpath = root / 'registry/supervisor.json'
            c = read(cpath) if cpath.exists() else None
            spath = root / 'provenance/supervisor/state.json'
            state = read(spath) if spath.exists() else {'nodes': {}}
            require(state.get('worker', {}).get('status') not in ('running', 'submitting', 'unknown'), 'worker must be reconciled first')
            for s in state.get('nodes', {}).values():
                require(s.get('status') not in ('running', 'submitting', 'unknown', 'publishing', 'reviewing'),
                        'jobs/reviews must be reconciled before amendment')
                require(not s.get('attempt') or s.get('status') == 'complete',
                        'unfinished attempted job requires deliberate recovery before amendment')
            candidate = copy.deepcopy(c)
            if c:
                require(c.get('paused') is True, 'pause supervisor configuration before amendment')
                # A completed node under an unfinished task cannot be silently reinterpreted.
                require(not any(n['task_id'] in affected and state.get('nodes', {}).get(n['id'], {}).get('attempt')
                                for n in c['nodes']), 'affected task already has execution evidence; use a new task')
                for n in candidate['nodes']:
                    if not state.get('nodes', {}).get(n['id'], {}).get('attempt') and not n.get('imported_evidence'):
                        n['contract'] = None
                        n.pop('approved_contract_sha256', None)
                for i in sorted(set(proposed) - set(previous)):
                    candidate['nodes'].append(dict(id=i, task_id=i, result_path=proposed[i]['result_path'],
                         depends_on=[], scientific_result=True, finalizes_task=True, contract=None))
                # New task dependencies are explicit input, never inferred from ordering.
                dependencies = amend.get('new_dependencies', {})
                require(set(dependencies) == set(proposed) - set(previous), 'new task dependencies must be explicit')
                for n in candidate['nodes']:
                    if n['id'] in dependencies: n['depends_on'] = dependencies[n['id']]
                from supervisor_daemon import load_config
                import tempfile
                with tempfile.TemporaryDirectory() as tmp:
                    trial=Path(tmp);atomic(trial/'registry/supervisor.json',candidate);load_config(trial)
            # Store complete old state/document evidence; never overwrite results or job state.
            archive = root / 'provenance/design' / ('history-' + sha(dpath))
            archive.mkdir(parents=True, exist_ok=True)
            atomic(archive / 'original_design.json', old)
            historical = copy.deepcopy(old)
            atomic(archive / 'plan_tasks.json', read(receipt(root, old['task_manifest'])))
            historical['task_manifest'] = descriptor(archive / 'plan_tasks.json', root)
            atomic(archive / 'design.json', historical)
            for name in ROOT_DOCS: atomic(archive / ('active_' + name), (root/name).read_text())
            if c: atomic(archive / 'supervisor.json', c)
            if spath.exists(): atomic(archive / 'state.json', state)
            baseline = root / 'provenance/design' / sha(proposal_path)
            if baseline.exists():
                for name, contents in p['documents'].items():
                    require(not (baseline/name).exists() or (baseline/name).read_text() == contents,
                            'conflicting amendment baseline')
            canonical = [{k:t[k] for k in TASK_FIELDS} for t in p['tasks']]
            for name, contents in p['documents'].items(): atomic(baseline / name, contents)
            atomic(baseline / 'plan_tasks.json', canonical)
            new = dict(policy='plan_results_v1', version=p['version'], proposal=descriptor(proposal_path, root),
                approval=descriptor(approval_path, root), appraisal=p['appraisal'], approval_evidence=approval['evidence'],
                intake=old['intake'], review_policy=POLICY, design_review=descriptor(review_path, root),
                documents={name:descriptor(baseline/name,root) for name in ROOT_DOCS},
                active_scope={name:sha(baseline/name) for name in ROOT_DOCS[:2]},
                task_manifest=descriptor(baseline/'plan_tasks.json',root),
                history=old.get('history', []) + [dict(version=old['version'], design=descriptor(archive/'design.json',root),
                                                    preserved_tasks=sorted(completed))])
            if candidate:
                replacements = {name: new['active_scope'][name] for name in ROOT_DOCS[:2]}
                replacements['registry/design.json'] = hashlib.sha256(
                    (json.dumps(new, ensure_ascii=False, indent=2) + '\n').encode()).hexdigest()
                for node in candidate['nodes']:
                    if state.get('nodes', {}).get(node['id'], {}).get('attempt') or node.get('imported_evidence'):
                        continue
                    gates = node.setdefault('required_scope_gates', [])
                    for gate in gates:
                        if gate['path'] in replacements: gate['sha256'] = replacements[gate['path']]
                    if not any(g['path'] == '01_PLAN.md' for g in gates):
                        gates.append(dict(path='01_PLAN.md', sha256=new['active_scope']['01_PLAN.md']))
                    for gate in node.get('expansion_policy', {}).get('scope_gates', []):
                        if gate['path'] in replacements: gate['sha256'] = replacements[gate['path']]
            names = list(ROOT_DOCS) + ['registry/design.json','registry/tasks.tsv','registry/plan_tasks.json','results/README.md']
            if c: names.append('registry/supervisor.json')
            journal = dict(stage='prepared', before={name:(root/name).read_text() if (root/name).exists() else None for name in names},
                 version=p['version'], proposal_sha256=sha(proposal_path), approval=descriptor(approval_path,root),
                 previous_design=descriptor(archive/'original_design.json',root), reason=amend['reason'],
                 receipt_path=str((baseline/'amendment_receipt.json').relative_to(root)))
            atomic(root / JOURNAL, journal)
            try:
                for name, contents in p['documents'].items(): atomic(root/name, contents)
                atomic(root/'registry/plan_tasks.json',canonical)
                atomic(root/'registry/tasks.tsv', tasks_table([{**t, 'status':previous.get(t['task_id'],{}).get('status','pending'),
                    'next_action':previous.get(t['task_id'],{}).get('next_action','')} for t in p['tasks']]))
                if c: atomic(cpath,candidate)
                atomic(dpath,new)
                from project_events import rebuild
                ep=root/'provenance/events.jsonl'
                events=[json.loads(l) for l in ep.read_text().splitlines()] if ep.exists() else []
                rebuild(root,events)
                journal['stage']='committed';atomic(root/JOURNAL,journal)
                verify_design(root)
            except Exception:
                restore(root,journal);(root/JOURNAL).unlink()
                raise
        # Keep daemon lock; event hook gets its own event lock and is idempotent.
        return finish(root,journal)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=('apply','recover'));ap.add_argument('--root',type=Path,required=True)
    for name in ('proposal','approval','review'):ap.add_argument('--'+name,type=Path)
    a=ap.parse_args()
    out=recover(a.root) if a.mode=='recover' else apply(a.root,a.proposal,a.approval,a.review)
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
