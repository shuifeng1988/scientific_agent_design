#!/usr/bin/env python3
"""Refresh only this Supervisor's tasks without waiting for unrelated SSH probes."""
import argparse
import importlib.util
import json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,required=True)
    a=ap.parse_args(); root=str(a.root.resolve())
    directory=Path.home()/'.codex/monitor'
    spec=importlib.util.spec_from_file_location('codex_monitor',directory/'background_task_monitor.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    tasks=json.loads((directory/'tasks.json').read_text())
    owned=[t for t in tasks if t.get('project')==root and t['name'].startswith(('scientific-supervisor-','scientific-job-'))]
    rows=module.snapshot(owned)
    previous=json.loads((directory/'status.json').read_text()).get('tasks',[]) if (directory/'status.json').exists() else []
    names={t['name'] for t in owned}
    # Preserve other tasks and their individual checked_at_utc timestamps.
    module.write([r for r in previous if r['name'] not in names]+rows)
    print(json.dumps([dict(name=r['name'],status=r['status'],checked_at_utc=r['checked_at_utc']) for r in rows],indent=2))


if __name__=='__main__': main()
