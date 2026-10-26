"""Host-neutral method routing and handoff checks; never launch or publish work.

External providers supply methods/artifacts. Existing design, execution and report
validators retain authority. Provider configuration is not a permission grant.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import uuid
import time

from structured_output import decode_object, proposal_object
from research_workflow import (ROOT_DOCS, descriptor, inside, receipt, require,
                               task, validate_appraisal, verify_design)

PACKAGE = Path(__file__).resolve().parents[1]
CONFIG = 'registry/providers.json'
CONTRACT = 'scientific-project-v1'


def read_object(path):
    return decode_object(Path(path).read_text(encoding='utf-8'))[0]


def same_selection(previous, current):
    """Unrelated provider configuration edits must not invalidate this capability."""
    return ({k: v for k, v in previous.items() if k != 'config_sha256'}
            == {k: v for k, v in current.items() if k != 'config_sha256'})


def catalog():
    return read_object(PACKAGE / 'assets/modules.json')['capabilities']


def resolve(root, capability, host):
    """Return a bounded method selection. Unknown/incompatible selections fail closed."""
    root = Path(root).resolve()
    modules = catalog()
    require(isinstance(capability, str) and capability in modules, 'unknown/missing capability: ' + str(capability))
    require(isinstance(host, str) and bool(host.strip()), 'host name required')
    module = modules[capability]
    provider = dict(id='builtin.' + capability, kind='builtin', version='1',
                    entrypoint=module['skill'], hosts=['*'], instructions='Use the bundled stage references.')
    config_path = inside(root, CONFIG)
    config_hash = None
    if config_path.exists():
        cfg = read_object(config_path)
        require(set(cfg) == {'schema_version', 'contract_version', 'bindings', 'providers'},
                'provider config requires schema_version, contract_version, bindings, providers only')
        require(type(cfg['schema_version']) is int and cfg['schema_version'] == 1
                and cfg['contract_version'] == CONTRACT, 'unsupported provider contract version')
        bindings, providers = cfg['bindings'], cfg['providers']
        require(isinstance(bindings, dict) and isinstance(providers, dict), 'bindings/providers must be objects')
        require(not set(bindings) - set(modules), 'unknown capability in bindings')
        for name, spec in providers.items():
            require(isinstance(name, str) and re.fullmatch(r'[a-z0-9][a-z0-9.-]*', name)
                    and not name.startswith('builtin.'), 'invalid/reserved provider id')
            require(isinstance(spec, dict) and set(spec) == {'kind', 'version', 'entrypoint', 'hosts', 'instructions'},
                    'provider fields: kind, version, entrypoint, hosts, instructions')
            require(spec['kind'] in ('skill', 'subagent'), 'provider kind must be skill or subagent')
            for key in ('version', 'entrypoint', 'instructions'):
                require(isinstance(spec[key], str) and bool(spec[key].strip()), 'provider ' + key + ' required')
            require(isinstance(spec['hosts'], list) and bool(spec['hosts'])
                    and all(isinstance(h, str) and bool(h.strip()) for h in spec['hosts']), 'provider hosts required')
            require(spec['entrypoint'] not in {m['skill'] for m in modules.values()} | {'scientific-research-project'},
                    'provider cannot recursively select a bundled stage/router')
        for selected in bindings.values():
            require(isinstance(selected, str) and selected in providers, 'binding references unknown provider')
        if capability in bindings:
            name = bindings[capability]
            provider = dict(id=name, **providers[name])
        config_hash = descriptor(config_path, root)['sha256']
    require(host in provider['hosts'] or '*' in provider['hosts'], 'provider unavailable for host: ' + host)
    refs = ['references/project_contract.md', 'references/roles/' + module['role'] + '.md'] + module['references']
    if provider['kind'] != 'builtin':
        refs.append('references/provider_contract.md')
    entry = Path(provider['entrypoint']).expanduser()
    source = None
    if entry.is_absolute():
        require(entry.is_file(), 'provider entrypoint is unavailable')
        source = dict(path=str(entry.resolve()), sha256=hashlib.sha256(entry.read_bytes()).hexdigest())
    return dict(contract_version=CONTRACT, capability=capability, host=host, source=source,
                role=module['role'], provider=provider, config_sha256=config_hash,
                required_reads=[dict(path=str(PACKAGE / p), sha256=hashlib.sha256((PACKAGE / p).read_bytes()).hexdigest())
                                for p in dict.fromkeys(refs)], output_contract=module['output'])


def prepare(root, capability, host, objective, task_id=None, inputs=None, run_id=None,
            timeout_seconds=1800, max_output_bytes=52428800, review_subject=None):
    """Create a unique handoff under existing provenance/result layout, no other mutation."""
    root = Path(root).resolve()
    require(isinstance(objective, str) and bool(objective.strip()), 'objective required')
    route = resolve(root, capability, host)
    registered = task(root, task_id) if task_id else None
    if registered:
        result = inside(root, registered['result_path'])
        require(result.is_relative_to(root / 'results') and result != root / 'results',
                'registered task must have its own results path')
    if capability in ('execution', 'recovery', 'interpretation', 'reporting'):
        require(registered is not None, 'this capability requires a registered task')
    # Verify existing approved designs; early intake/evidence/design may precede freeze.
    if (root / 'registry/design.json').exists():
        verify_design(root)
    require(type(timeout_seconds) is int and 1 <= timeout_seconds <= 86400, 'invalid handoff timeout')
    require(type(max_output_bytes) is int and max_output_bytes > 0, 'invalid output byte limit')
    inputs = inputs if inputs is not None else [descriptor(root / n, root) for n in ROOT_DOCS[:2] if (root / n).is_file()]
    require(isinstance(inputs, list), 'inputs must be receipts')
    for ref in inputs: receipt(root, ref)
    if capability in ('interpretation', 'reporting'):
        require(isinstance(run_id, str) and bool(run_id.strip()), 'run_id required for result stages')
    if capability == 'review':
        require(isinstance(review_subject, dict), 'review_subject required')
        for ref in review_subject['targets']: receipt(root, ref)
    request_id = uuid.uuid4().hex
    parent = Path(registered['result_path']) / '_evidence/providers' if registered else Path('provenance/providers')
    directory = inside(root, str(parent / request_id))
    directory.mkdir(parents=True, exist_ok=False)
    protected = list(ROOT_DOCS) + ['registry/design.json', 'registry/tasks.tsv', 'registry/supervisor.json']
    # 02/03/04 and task status may legitimately advance during a provider call;
    # reject stale scientific identity/mapping without rejecting unrelated progress.
    baseline = {name: descriptor(inside(root, name), root) if inside(root, name).is_file() else None
                for name in ('00_PROJECT.md', '01_PLAN.md', 'registry/design.json')}
    roots = {name: descriptor(inside(root, name), root) if inside(root, name).is_file() else None for name in ROOT_DOCS}
    request = dict(schema_version=2, request_id=request_id, project_root=str(root), route=route,
                   inputs=inputs, run_id=run_id, review_subject=review_subject,
                   created_at=time.time(), limits=dict(timeout_seconds=timeout_seconds, max_output_bytes=max_output_bytes),
                   objective=objective, task_id=task_id,
                   result_path=registered['result_path'] if registered else None,
                   task_identity={k: v for k, v in registered.items() if k not in ('status', 'next_action')}
                   if registered else None,
                   root_documents=roots, baseline=baseline,
                   output_directory=str(directory.relative_to(root)), protected_paths=protected,
                   instruction='Read all available five root documents as project guidance; use the assigned task card. '
                   'Preserve real direction/design decisions. Write provider artifacts only in output_directory; '
                   'return to the operator for integration, existing gates and scientific review.')
    path = directory / 'request.json'
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


def check_output(root, request_path, output_path):
    """Check a provider handoff, not scientific truth, permission or task completion."""
    root = Path(root).resolve()
    request_path, output_path = Path(request_path).resolve(), Path(output_path).resolve()
    require(request_path.is_relative_to(root) and output_path.is_relative_to(root), 'handoff outside project')
    request, output = read_object(request_path), read_object(output_path)
    require(request['schema_version'] in (1, 2) and request['project_root'] == str(root), 'wrong project/schema')
    directory = inside(root, request['output_directory'])
    require(request_path == directory / 'request.json' and output_path.parent == directory
            and output_path != request_path, 'wrong handoff directory')
    require(set(output) == {'request_id', 'request_sha256', 'provider_id', 'status', 'summary', 'artifacts'},
            'output requires request identity, provider_id, status, summary and artifacts')
    require(output['request_id'] == request['request_id']
            and output['request_sha256'] == descriptor(request_path, root)['sha256'], 'stale/wrong request')
    route = request['route']
    require(output['provider_id'] == route['provider']['id'], 'wrong provider')
    require(same_selection(route, resolve(root, route['capability'], route['host'])),
            'provider or contract changed; prepare a new handoff')
    for name, ref in request['baseline'].items():
        if ref is None:
            require(not inside(root, name).exists(), 'project stage changed; prepare a new handoff')
        else:
            receipt(root, ref)
    if request['task_id']:
        current = task(root, request['task_id'])
        require({k: v for k, v in current.items() if k not in ('status', 'next_action')} == request['task_identity'],
                'task identity/scope/result mapping changed')
    if (root / 'registry/design.json').exists():
        verify_design(root)
    require(output['status'] in ('ready_for_review', 'needs_user', 'blocked'), 'provider cannot approve/complete a task')
    require(isinstance(output['summary'], str) and bool(output['summary'].strip()), 'summary required')
    require(isinstance(output['artifacts'], list), 'artifacts must be a list')
    if request['schema_version'] == 2:
        require(0 <= time.time() - request['created_at'] <= request['limits']['timeout_seconds'], 'handoff expired')
        for ref in request['inputs']: receipt(root, ref)
        require(sum(p.stat().st_size for p in directory.rglob('*') if p.is_file()) <= request['limits']['max_output_bytes'],
                'handoff output byte limit exceeded')
    seen = set()
    for ref in output['artifacts']:
        require(isinstance(ref, dict) and set(ref) == {'path', 'sha256'}, 'artifact receipt required')
        path = receipt(root, ref)
        require(path.is_relative_to(directory) and path not in (request_path, output_path), 'artifact outside assigned output')
        require(path not in seen, 'duplicate artifact'); seen.add(path)
    if output['status'] == 'ready_for_review':
        require(bool(seen), 'ready output needs real artifact evidence')
        capability = route['capability']
        if capability == 'evidence':
            refs = [r for r in output['artifacts'] if Path(r['path']).name == 'appraisal.json']
            require(len(refs) == 1, 'evidence provider must adapt to appraisal.json')
            appraisal = validate_appraisal(root, refs[0])
            require(appraisal.get('status') == 'ready_for_design_review', 'appraisal not ready for review')
            if request['schema_version'] == 2 and route['provider']['kind'] != 'builtin':
                runs = [r for r in output['artifacts'] if Path(r['path']).name == 'provider_run.json']
                require(len(runs) == 1, 'external evidence requires provider_run.json')
                run = read_object(receipt(root, runs[0]))
                require(run.get('provider') == route['provider'] and run.get('source') == route.get('source'),
                        'actual provider record mismatch')
                require(run.get('tools') and isinstance(run.get('access_limits'), list) and run.get('raw'),
                        'external evidence requires actual tools, access limits and raw outputs')
                for ref in run['raw']:
                    require(ref in output['artifacts'], 'raw provider output must be retained as an artifact')
                    receipt(root, ref)
        elif capability in ('execution', 'recovery'):
            refs = [r for r in output['artifacts'] if Path(r['path']).name == 'proposal.json']
            require(len(refs) == 1, 'execution provider must adapt to proposal.json')
            proposal_object(receipt(root, refs[0]).read_text())
        if request['schema_version'] == 2:
            check_stage(root, request, output)
    return dict(handoff_valid=True, status=output['status'], task_complete=False,
                scientific_review_required=True, publication_authorized=False,
                next_action='Operator reviews artifacts and applies the existing stage-specific gates.')



def check_stage(root, request, output):
    """Validate normalized payloads; integration/publication remains a separate gate."""
    from research_workflow import validate_tasks, report_content, ROOT_DOCS, text
    capability = request['route']['capability']
    def payload(name):
        refs = [r for r in output['artifacts'] if Path(r['path']).name == name]
        require(len(refs) == 1, capability + ' provider requires ' + name)
        path = receipt(root, refs[0]); return path, read_object(path)
    if capability == 'intake':
        _, value = payload('intake.json')
        text(value.get('question'), 'intake question')
        require(isinstance(value.get('unresolved'), list), 'intake unresolved questions required')
        require(value.get('user_evidence'), 'actual user direction evidence required')
        for ref in value['user_evidence']: receipt(root, ref)
    elif capability == 'design':
        _, value = payload('design_proposal.json')
        require(set(value.get('documents', {})) == set(ROOT_DOCS), 'design requires five documents')
        validate_tasks(root, value['tasks'], value['documents']['00_PROJECT.md'], value['documents']['01_PLAN.md'])
        validate_appraisal(root, value['appraisal'])
        text(value.get('version'), 'design version'); text(value.get('author_invocation_id'), 'design author')
    elif capability == 'interpretation':
        _, value = payload('reflection.json')
        require(value.get('run_id') == request['run_id'], 'reflection run mismatch')
        for key in ('expected','observed','uncertainty','reasoning','alternative_explanations',
                    'evidence_strength','limitations','next_step_impact'):
            text(value.get(key), 'reflection.' + key)
        require(value.get('decision') in ('continue','supplement','needs_user'), 'reflection decision missing')
        lit = value.get('literature_search', {})
        require(lit.get('queries') and lit.get('searched_at') and lit.get('status') in ('searched','no_relevant_results'),
                'actual reflection literature search required')
        require(lit['status'] != 'searched' or lit.get('sources'), 'reflection sources missing')
    elif capability == 'reporting':
        path, _ = payload('report.json')
        report_content(root, request['task_id'], path, request['run_id'])
    elif capability == 'review':
        from scientific_review import verify
        path, _ = payload('scientific_review.json')
        verify(root, path, request['review_subject'], accepted=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=('resolve', 'prepare', 'check-output'))
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--capability', choices=sorted(catalog()))
    ap.add_argument('--host', default='codex')
    ap.add_argument('--objective')
    ap.add_argument('--task-id')
    ap.add_argument('--inputs', type=Path, help='JSON list of actual project-relative input receipts')
    ap.add_argument('--run-id'); ap.add_argument('--review-subject', type=Path)
    ap.add_argument('--timeout-seconds', type=int, default=1800)
    ap.add_argument('--max-output-bytes', type=int, default=52428800)
    ap.add_argument('--request', type=Path)
    ap.add_argument('--output', type=Path)
    a = ap.parse_args()
    if a.mode == 'resolve':
        out = resolve(a.root, a.capability, a.host)
    elif a.mode == 'prepare':
        path = prepare(a.root, a.capability, a.host, a.objective, a.task_id,
                       inputs=json.loads(a.inputs.read_text()) if a.inputs else None, run_id=a.run_id,
                       timeout_seconds=a.timeout_seconds, max_output_bytes=a.max_output_bytes,
                       review_subject=read_object(a.review_subject)['subject'] if a.review_subject else None)
        out = dict(request=str(path), sha256=descriptor(path, a.root.resolve())['sha256'])
    else:
        require(a.request is not None and a.output is not None, '--request and --output required')
        out = check_output(a.root, a.request, a.output)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
