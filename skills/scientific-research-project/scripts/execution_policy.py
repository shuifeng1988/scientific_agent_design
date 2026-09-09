"""Execution-first DAG policy. Scientific scope is an operator-owned input."""
import copy
import hashlib
import json
import time
from pathlib import Path


def phases(node):
    if node.get('completion_policy') == 'artifact':
        if node.get('scientific_result', True) or node.get('finalizes_task'):
            raise ValueError('artifact completion cannot finalize a scientific task')
        return ('run', 'validate')
    return ('run', 'validate', 'interpret')


def verify_artifact(root, node, state):
    result = (root/node['result_path']).resolve()
    qc = json.loads((result/'_evidence/qc.json').read_text())
    if qc.get('run_id') != state['run_id'] or qc.get('passed') is not True or not qc.get('artifacts'):
        raise ValueError('artifact QC requires matching run ID, passed and hashes')
    for a in qc['artifacts']:
        p = (result/a['path']).resolve()
        if not p.is_relative_to(result) or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != a['sha256']:
            raise ValueError('artifact QC hash mismatch')
    if not (result/'README.md').is_file():
        raise ValueError('artifact README required: methods, input and reuse limits')
    return qc


def incident(state, node_state, phase=None):
    # Phase-scoped identity survives new code, process IDs and exception wording.
    key = node_state['recovery_key'] + ':' + (phase or node_state['phase'])
    return state.setdefault('recovery_incidents', {}).setdefault(
        key, dict(worker_calls=0, retries=0, round=1, history=[]))


def apply_expansions(config, states, requested, expansions):
    """Only an explicitly preauthorized model/stage matrix may be expanded."""
    result = copy.deepcopy(config)
    lookup = {n['id']: n for n in result['nodes']}
    added = []
    for e in expansions:
        parent_id = e['parent_id']
        if parent_id not in requested:
            raise ValueError('unrequested expansion')
        parent = lookup[parent_id]
        ps = states[parent_id]
        policy = parent.get('expansion_policy', {})
        if not policy or ps.get('attempt', 0) or ps['status'] != 'pending' or parent.get('contract'):
            raise ValueError('expansion requires unattempted authorized parent')
        if len(e['nodes']) > policy.get('max_new_nodes', 0):
            raise ValueError('expansion size exceeds authorized matrix')
        local_ids = set()
        required = {(m,s) for m in policy['models'] for s in policy['stages']}
        if {(n.get('model_id'),n.get('stage')) for n in e['nodes']} != required:
            raise ValueError('expansion must retain the complete authorized model/stage matrix')
        for n in e['nodes']:
            if set(n) - {'id','task_id','depends_on','result_path','scientific_result','finalizes_task',
                         'completion_policy','model_id','stage','contract'}:
                raise ValueError('unknown expansion node fields')
            model, stage = n['model_id'], n['stage']
            if model not in policy['models'] or stage not in policy['stages']:
                raise ValueError('expansion outside approved model/stage scope')
            expected = parent_id+'.'+model+'.'+stage
            if n['id'] != expected or expected in lookup or expected in local_ids:
                raise ValueError('duplicate or renamed semantic task')
            if n['task_id'] != parent['task_id'] or n.get('finalizes_task') or n.get('scientific_result', True):
                raise ValueError('expansion cannot change scientific scope/finalize parent')
            expected_path = str(Path(parent['result_path'])/'models'/model/stage)
            if n['result_path'] != expected_path:
                raise ValueError('expansion result path must match model and stage')
            phases(n)
            local_ids.add(expected)
        allowed = set(parent['depends_on']) | local_ids
        if any(set(n['depends_on']) - allowed for n in e['nodes']):
            raise ValueError('expansion dependency outside approved branch')
        for n in e['nodes']:
            # New tasks cannot drop prerequisites that guard the parent scope.
            n = copy.deepcopy(n)
            required_deps = [parent_id+'.'+n['model_id']+'.'+s
                             for s in policy.get('stage_dependencies',{}).get(n['stage'], [])]
            if not set(required_deps) <= set(n['depends_on']):
                raise ValueError('missing model-stage prerequisite')
            n['depends_on'] = list(dict.fromkeys(parent['depends_on'] + n['depends_on']))
            n['recovery_key'] = parent_id+'.'+n['model_id']+'.'+n['stage']
            n['execution_context'] = copy.deepcopy(parent.get('execution_context',{}))
            if n.get('contract'):
                previous = {(g['path'],g['sha256']) for g in policy.get('scope_gates',[])}
                current = {(g['path'],g['sha256']) for g in n['contract'].get('gates',[])}
                if not previous <= current:
                    raise ValueError('expanded contract removed scope gates')
                n['approved_contract_sha256'] = hashlib.sha256(json.dumps(n['contract'], sort_keys=True).encode()).hexdigest()
            n['required_scope_gates'] = copy.deepcopy(policy.get('scope_gates',[]))
            result['nodes'].append(n); lookup[n['id']] = n; added.append(n['id'])
        parent['depends_on'] = list(dict.fromkeys(parent['depends_on'] + sorted(local_ids)))
    return result, added


def progression(state, config):
    nodes = state['nodes']
    active = [i for i,s in nodes.items() if s['status'] in ('running','submitting','unknown')]
    worker = state.get('worker', {}).get('status') in ('running','submitting','unknown')
    unfinished = [s for s in nodes.values() if s['status'] != 'complete']
    if active:
        status = 'running'
    elif worker:
        status = 'planning_or_repairing'
    elif not unfinished:
        status = 'complete'
    elif any(s.get('reason','').startswith('waiting_resources') for s in unfinished):
        status = 'waiting_resources'
    else:
        status = 'stalled'
    return dict(status=status, active_jobs=len(active), completed_nodes=len(nodes)-len(unfinished),
                last_verified_progress=state.get('last_verified_progress'),
                note='service health is separate; artifact completion is not scientific release')
