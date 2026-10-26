"""Register scoped evidence jobs and distinguish required from optional supplements."""
import argparse
import copy
import fcntl
import json
from pathlib import Path
import re
import tempfile
from research_workflow import atomic, read, receipt, require, text, task, descriptor, inside, verify_design


def verify_supplements(root, task_id, reflection):
    root = Path(root).resolve()
    items = reflection.get('supplements', [])
    if reflection.get('decision') == 'supplement':
        require(bool(items), 'supplement decision needs registered follow-up tasks')
    require(isinstance(items, list), 'supplements must be a list')
    if not items: return
    config = read(root / 'registry/supervisor.json')
    nodes = {n['id']: n for n in config['nodes']}
    state_path = root / 'provenance/supervisor/state.json'
    states = read(state_path).get('nodes', {}) if state_path.exists() else {}
    seen = set()
    for item in items:
        node_id = text(item.get('node_id'), 'supplement node_id')
        require(node_id not in seen, 'duplicate supplement'); seen.add(node_id)
        require(item.get('necessity') in ('required', 'optional'), 'supplement necessity required/optional')
        text(item.get('rationale'), 'supplement rationale')
        require(node_id in nodes, 'supplement not registered: ' + node_id)
        n = nodes[node_id]
        require(n['task_id'] == task_id and n.get('completion_policy') == 'artifact', 'supplement task/scope mismatch')
        record = read(receipt(root, n['supplement_receipt']))
        receipt(root, record['source'])
        require(record['task_id'] == task_id and record['node_id'] == node_id
                and record['necessity'] == item['necessity'], 'supplement registration mismatch')
        if item['necessity'] == 'required':
            s = states.get(node_id, {})
            require(s.get('status') == 'complete', 'required supplemental evidence pending: ' + node_id)
            from execution_policy import verify_artifact
            verify_artifact(root, n, s)
            # The scientific interpretation must actually refer to the exact new evidence.
            require(item.get('evidence'), 'required supplement must be incorporated into reflection')
            for ref in item['evidence']:
                path = receipt(root, ref)
                require(path.is_relative_to(inside(root, n['result_path'])), 'supplement evidence outside its node')


def register(root, spec_path):
    root = Path(root).resolve(); spec_path = Path(spec_path).resolve()
    require(spec_path.is_relative_to(root), 'supplement spec outside project')
    spec = read(spec_path); verify_design(root)
    task_id = text(spec.get('task_id'), 'supplement task_id'); t = task(root, task_id)
    key = text(spec.get('id'), 'supplement id')
    require(re.fullmatch(r'[A-Za-z0-9_-]+', key), 'invalid supplement id')
    necessity = spec.get('necessity')
    require(necessity in ('required', 'optional'), 'necessity must be required/optional')
    for field in ('rationale', 'scope_justification', 'stopping_rule', 'analysis_label'):
        text(spec.get(field), field)
    require(spec['analysis_label'] in ('prespecified', 'exploratory_post_hoc'), 'analysis label required')
    source = receipt(root, spec['source'])
    require(source.is_relative_to(inside(root, t['result_path'])), 'supplement source outside parent task')
    # The unchanged approved plan is the authority; novel science still requires amendment.
    require(spec['scope']['path'] == '01_PLAN.md', 'supplement scope must bind current approved plan')
    receipt(root, spec['scope'])
    directory = root / 'provenance/supervisor'; directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'daemon.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        c = read(root / 'registry/supervisor.json')
        node_id = task_id + '.supplement.' + key
        existing = next((n for n in c['nodes'] if n['id'] == node_id), None)
        if existing:
            record = read(receipt(root, existing['supplement_receipt']))
            require(record['spec'] == descriptor(spec_path, root), 'conflicting supplement id')
            return dict(node_id=node_id, duplicate=True)
        parent_path = Path(t['result_path']) / '_evidence/supplements' / key
        node = dict(id=node_id, task_id=task_id, result_path=str(parent_path),
                    depends_on=spec.get('depends_on', []), completion_policy='artifact',
                    scientific_result=False, finalizes_task=False, contract=spec.get('contract'),
                    required_scope_gates=[spec['scope']])
        lookup = {n['id']: n for n in c['nodes']}
        require(isinstance(node['depends_on'], list) and all(x in lookup for x in node['depends_on']),
                'unknown supplement dependencies')
        if necessity == 'required':
            def reaches_finalizer(i, seen):
                if i in seen: return False
                seen.add(i); n = lookup[i]
                return ((n['task_id'] == task_id and n.get('finalizes_task'))
                        or any(reaches_finalizer(j, seen) for j in n['depends_on']))
            require(not any(reaches_finalizer(i, set()) for i in node['depends_on']),
                    'required supplement cannot depend on its own scientific completion')
        from supervisor_daemon import digest, load_config
        if node['contract']: node['approved_contract_sha256'] = digest(node['contract'])
        record_path = inside(root, str(parent_path / 'registration.json'))
        # Reflection will change when new evidence is integrated. Retain the exact
        # source that prompted registration rather than a permanently stale link.
        snapshot = record_path.with_name('source_snapshot' + source.suffix)
        require(not snapshot.exists() or snapshot.read_bytes() == source.read_bytes(), 'conflicting source snapshot')
        if not snapshot.exists():
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(source.read_bytes())
        record = dict(task_id=task_id, node_id=node_id, necessity=necessity,
                      spec=descriptor(spec_path, root), source=descriptor(snapshot, root), scope=spec['scope'])
        require(not record_path.exists() or read(record_path) == record, 'conflicting registration receipt')
        atomic(record_path, record)
        node['supplement_receipt'] = descriptor(record_path, root)
        candidate = copy.deepcopy(c); candidate['nodes'].append(node)
        with tempfile.TemporaryDirectory() as tmp:
            trial = Path(tmp); atomic(trial / 'registry/supervisor.json', candidate); load_config(trial)
        atomic(root / 'registry/supervisor.json', candidate)
        return dict(node_id=node_id, duplicate=False, necessity=necessity, result_path=str(parent_path))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True); ap.add_argument('--spec', type=Path, required=True)
    a = ap.parse_args(); print(json.dumps(register(a.root, a.spec), ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
