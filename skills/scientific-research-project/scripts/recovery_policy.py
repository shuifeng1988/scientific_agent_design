"""Diagnose and verify recovery evidence before the dispatcher allows a retry."""
import hashlib
import json
from pathlib import Path
from budget_policy import execution_used


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify_failure(probe):
    text = str(probe.get('reason', '')) + '\n' + probe.get('log_tail', '')
    category = 'unclassified'
    for name, signatures in (
        ('serialization', ('JSONDecodeError', 'duplicate JSON key', 'Invalid worker proposal')),
        ('environment', ('ModuleNotFoundError', 'ImportError', 'command not found')),
        ('resources', ('oom-kill', 'CUDA out of memory', 'std::bad_alloc')),
        ('credentials', ('Permission denied', 'Authentication failed', 'Unauthorized')),
        ('timeout', ('Result=timeout', "'Result': 'timeout'", 'TimeoutExpired')),
        ('network', ('Connection reset', 'Temporary failure in name resolution', 'Connection refused')),
        ('code', ('SyntaxError', 'NameError', 'TypeError', 'Traceback')),
    ):
        if any(term in text for term in signatures):
            category = name
            break
    return {'category': category, 'root_cause_confirmed': False,
            'note': 'Classifier is a lead; worker must inspect evidence and validate a targeted remedy.',
            'terminal': probe.get('state') == 'failed', 'evidence': probe}


def verified_file(root, record, within=None):
    p = (root / record['path']).resolve()
    if not p.is_relative_to(root.resolve()) or (within and not p.is_relative_to(within.resolve())):
        raise ValueError('repair evidence outside allowed path')
    if not p.is_file() or sha(p) != record['sha256']:
        raise ValueError('repair evidence hash mismatch: ' + record['path'])
    return p


def verify_recovery(root, node, state, item):
    """Return a validated proposal; no scheduler mutation on rejection."""
    r = item.get('recovery', {})
    result = root / node['result_path']
    failure = state.get('failure_record')
    if not failure or r.get('failure_record_sha256') != failure['sha256']:
        raise ValueError('repair must reference the exact diagnosed failure')
    verified_file(root, failure, result)
    if not r.get('diagnosis') or not r.get('action'):
        raise ValueError('diagnosis and targeted remedy required')
    if r.get('resume_phase') != state['phase']:
        raise ValueError('repair must resume the failed phase; no blind full reset or skipped phase')
    if (state.get('execution_policy') == 'v2' and state.get('repair_budget_remaining', 0) <= 0) or (state.get('execution_policy') != 'v2' and execution_used(state) >= node['contract'].get('max_attempts', 3)):
        raise ValueError('repair attempt budget exhausted')
    old, new = node['contract'], item['contract']
    if new.get('max_attempts', 3) > old.get('max_attempts', 3):
        raise ValueError('repair may not increase attempt budget')
    phases = ('run', 'validate', 'interpret')
    for phase in phases[:phases.index(state['phase'])]:
        if old[phase] != new[phase]:
            raise ValueError('repair changed an already successful phase')
    previous = {g['path']: g['sha256'] for g in old['gates']}
    current = {g['path']: g['sha256'] for g in new['gates']}
    if not previous.keys() <= current.keys():
        raise ValueError('repair removed an original input gate')
    changed_code = []
    for path, value in current.items():
        verified_file(root, {'path': path, 'sha256': value})
        if previous.get(path) != value:
            if path in previous and Path(path).suffix not in ('.py', '.sh'):
                raise ValueError('repair changed a frozen non-code gate')
            if Path(path).suffix in ('.py', '.sh'):
                changed_code.append((path, value))
    validation_path = verified_file(root, r['validation'], result)
    v = json.loads(validation_path.read_text())
    if v.get('passed') is not True or type(v.get('exit_code')) is not int or v['exit_code'] != 0:
        raise ValueError('minimal verification did not pass')
    if not isinstance(v.get('command'), list) or not v['command'] or not all(isinstance(a, str) for a in v['command']):
        raise ValueError('minimal verification command required')
    verified_file(root, v['log'], result)
    tested = {(g['path'], g['sha256']) for g in v.get('tested_gates', [])}
    if not tested or not set(changed_code) <= tested:
        raise ValueError('changed executable code lacks tested hashes')
    for p, h in tested:
        verified_file(root, {'path': p, 'sha256': h})
    reused = r.get('preserved_artifacts', [])
    if state['phase'] != 'run' and (not reused or not r.get('reuse_justification')):
        raise ValueError('later-phase repair must verify reusable prior outputs')
    for g in reused:
        verified_file(root, g, result)
    return r
