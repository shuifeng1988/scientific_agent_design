#!/usr/bin/env python3
"""Create a DAG skeleton from explicit dependency TSV; never invent runnable jobs."""
import argparse
import csv
import json
from pathlib import Path
import sys

from supervisor_daemon import atomic, file_hash


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--dependencies',type=Path,required=True)
    ap.add_argument('--hosts',type=Path,required=True,help='Reviewed JSON host/driver/resource configuration')
    ap.add_argument('--progress-worker',action='store_true')
    a=ap.parse_args(); root=a.root.resolve()
    target=root/'registry/supervisor.json'
    if target.exists(): raise RuntimeError('configuration already exists; inspect and patch it explicitly')
    with (root/'registry/tasks.tsv').open() as f:
        tasks={r['task_id']:r for r in csv.DictReader(f,delimiter='\t')}
    with a.dependencies.open() as f:
        dependencies=list(csv.DictReader(f,delimiter='\t'))
    nodes=[]
    for d in dependencies:
        t=tasks[d['task_id']]
        n=dict(id=t['task_id'],task_id=t['task_id'],depends_on=[x for x in d['depends_on'].split(';') if x],
               result_path=t['result_path'],scientific_result=True,finalizes_task=True,contract=None)
        if d.get('frozen_evidence'):
            if t['status'] not in ('frozen','complete'): raise ValueError('cannot import unfrozen task')
            n['imported_evidence']=[dict(path=p,sha256=file_hash(root/p)) for p in d['frozen_evidence'].split(';')]
        nodes.append(n)
    if set(tasks)!=set(n['id'] for n in nodes): raise ValueError('dependency table must cover all registered tasks')
    scripts=Path(__file__).resolve().parent
    host=json.loads(a.hosts.read_text())
    if not isinstance(host,dict) or not host: raise ValueError('reviewed hosts required')
    if a.progress_worker and 'local' not in host: raise ValueError('progress worker requires local host')
    from research_workflow import verify_design
    verify_design(root)
    c=dict(execution_policy='v2',workflow_policy='plan_results_v1',paused=False,hosts=host,nodes=nodes,progress_worker=dict(enabled=a.progress_worker,
        argv=[sys.executable,str(scripts/'progress_worker.py')],batch_size=1,budget_scope='per_node',max_worker_calls_per_round=3,
        cooldown_seconds=600,failure_backoff_seconds=1800,timeout_seconds=1800))
    atomic(target,c)
    print(json.dumps(dict(config=str(target),nodes=len(nodes),imported=sum('imported_evidence' in n for n in nodes))))


if __name__=='__main__': main()
