"""Inspect an installed literature skill and normalize its actual host-produced output.

Does not install a skill, search literature, invoke a model or invent missing evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import research_workflow as rw
import module_provider as mp


def inspect(entry):
    entry = Path(entry).expanduser().resolve()
    rw.require(entry.is_file(), 'installed literature SKILL.md is missing')
    body = entry.read_text(); digest = hashlib.sha256(entry.read_bytes()).hexdigest()
    rw.require('name: literature-review' in body, 'expected the literature-review skill entry')
    return dict(entrypoint=str(entry), sha256=digest, version='sha256:' + digest,
                tools={'parallel-cli': shutil.which('parallel-cli')},
                online_access_verified=False, scientific_quality_evaluated=False,
                limitations=['Executable presence does not prove authentication or search access.',
                             'Read provider dependencies and licensing before invoking it through the host.',
                             'Missing search/figure tools must be reported, never replaced by invented evidence.'])


def config(entry, hosts):
    info = inspect(entry)
    rw.require(hosts and all(h in ('codex','claude') for h in hosts), 'explicit supported host required')
    return dict(schema_version=1, contract_version=mp.CONTRACT, bindings={'evidence':'literature-review-local'},
                providers={'literature-review-local':dict(kind='skill', version=info['version'],
                    entrypoint=info['entrypoint'], hosts=hosts,
                    instructions='Read the installed skill and relevant dependencies. Use the real host search tools. '
                    'Preserve raw search/source output, access limits and tool records. Return a canonical appraisal; '
                    'run literature_adapter.py normalize. Do not replace root documents or scientific approvals.')})


def normalize(root, request_path, appraisal_path, raw_paths, tool_record):
    root = Path(root).resolve(); request_path = Path(request_path).resolve()
    request = rw.read(request_path); directory = request_path.parent
    route = request['route']
    rw.require(route['capability'] == 'evidence' and route['provider']['kind'] != 'builtin', 'external evidence request required')
    rw.require(route.get('source'), 'local provider source fingerprint required')
    source = Path(route['source']['path'])
    rw.require(rw.sha(source) == route['source']['sha256'], 'provider source changed')
    appraisal_path = Path(appraisal_path).resolve()
    rw.require(appraisal_path.parent == directory and appraisal_path.name == 'appraisal.json', 'appraisal must be in assigned output')
    appraisal = rw.validate_appraisal(root, rw.descriptor(appraisal_path, root))
    rw.require(appraisal.get('status') == 'ready_for_design_review', 'appraisal not ready')
    rw.require(raw_paths, 'raw provider outputs required')
    refs = []
    for path in raw_paths:
        path = Path(path).resolve()
        rw.require(path.is_relative_to(directory) and path != appraisal_path and path.is_file(), 'raw output outside handoff')
        refs.append(rw.descriptor(path, root))
    rw.require(isinstance(tool_record, dict) and tool_record.get('tools') and
               isinstance(tool_record.get('access_limits'), list), 'actual tools and access_limits required')
    record = directory / 'provider_run.json'
    rw.atomic(record, dict(provider=route['provider'], source=route['source'], raw=refs, **tool_record))
    output = directory / 'output.json'
    rw.atomic(output, dict(request_id=request['request_id'], request_sha256=rw.sha(request_path),
              provider_id=route['provider']['id'], status='ready_for_review',
              summary='Actual raw outputs normalized; substantive scientific review remains required.',
              artifacts=[rw.descriptor(appraisal_path, root), rw.descriptor(record, root)] + refs))
    return mp.check_output(root, request_path, output)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=('inspect','config','normalize'))
    ap.add_argument('--entry', type=Path); ap.add_argument('--host', action='append', choices=('codex','claude'))
    ap.add_argument('--root', type=Path); ap.add_argument('--request', type=Path); ap.add_argument('--appraisal', type=Path)
    ap.add_argument('--raw', type=Path, action='append'); ap.add_argument('--tool-record', type=Path)
    a=ap.parse_args()
    if a.mode == 'inspect': out=inspect(a.entry)
    elif a.mode == 'config': out=config(a.entry,a.host)
    else: out=normalize(a.root,a.request,a.appraisal,a.raw,rw.read(a.tool_record))
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
