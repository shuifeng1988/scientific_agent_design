#!/usr/bin/env python3
"""A bounded Codex planning/repair call. Uses current user's CLI auth and policy."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

from structured_output import proposal_object
from supervisor_daemon import atomic, file_hash


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--request', type=Path, required=True)
    ap.add_argument('--codex', default=shutil.which('codex'))
    a = ap.parse_args()
    request = json.loads(a.request.read_text())
    if not a.codex:
        raise RuntimeError('Codex CLI unavailable; configure another progress worker')
    output = a.request.with_name('proposal.json')
    raw = a.request.with_name('proposal.raw.txt')
    from module_provider import PACKAGE, resolve, same_selection
    nodes = request.get('nodes', [])
    state = request.get('state', {})
    capabilities = sorted({
        'recovery' if state.get(n['id'], {}).get('repairable')
        or state.get(n['id'], {}).get('worker_failure_record') else 'execution'
        for n in nodes
    } or {'execution'})
    routes = [resolve(a.root, capability, 'codex') for capability in capabilities]
    atomic(a.request.with_name('worker_providers.json'), routes)
    required = {ref['path'] for route in routes for ref in route['required_reads']}
    prompt = ('Read the following shared/stage contracts before implementing this request:\n'
              + '\n'.join(sorted(required)) + '\n\n'
              + (PACKAGE / 'references/worker_contract.md').read_text()
              + '\nSelected method providers (bounded by those contracts):\n'
              + json.dumps(routes, ensure_ascii=False)
              + '\nVerify external Skill/subagent availability in this host before invocation. '
              'If unavailable, return a blocked proposal with the actual missing capability; '
              'do not silently substitute a different provider. Keep the existing proposal JSON format.\n'
              'Work request follows:\n')

    # Noninteractive CLI support verified against installed exec --help.
    cmd = [a.codex, 'exec', '--approve-for-me', '--skip-git-repo-check', '-C', str(a.root.resolve()),
           '--output-last-message', str(raw), '-']
    atomic(a.request.with_name('worker_prompt.txt'),prompt + json.dumps(request, ensure_ascii=False))
    with a.request.with_name('worker_stdout.log').open('w') as so, a.request.with_name('worker_stderr.log').open('w') as se:
        result = subprocess.run(cmd, input=prompt + json.dumps(request, ensure_ascii=False),
                                text=True,stdout=so,stderr=se)
    if result.returncode:
        raise SystemExit(result.returncode)
    if not all(same_selection(route, resolve(a.root, route['capability'], 'codex')) for route in routes):
        raise RuntimeError('Provider selection/contract changed during worker; raw output retained for review')
    proposal, normalization = proposal_object(raw.read_text())
    atomic(a.request.with_name('output_validation.json'),dict(raw_sha256=file_hash(raw),
           normalization=normalization, worker_exit_code=result.returncode, schema_valid=True))
    atomic(output, proposal)


if __name__ == '__main__':
    main()
