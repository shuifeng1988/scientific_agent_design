#!/usr/bin/env python3
"""Real local systemd smoke: tiny artifacts only, not scientific/model results."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import supervisor_daemon as sd


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--fixture-phase');ap.add_argument('--result');a=ap.parse_args()
    if a.fixture_phase:
        d=a.root/a.result;d.mkdir(parents=True,exist_ok=True)
        if a.fixture_phase=='report_failure':raise RuntimeError('injected literature access failure')
        if a.fixture_phase=='run':
            sd.atomic(d/'value.json',dict(real_process=True,fixture=True))
            sd.atomic(d/'README.md','# Real scheduler fixture\nNot scientific evidence.\n')
        else:
            sd.atomic(d/'_evidence/qc.json',dict(run_id=os.environ['SCI_RUN_ID'],passed=True,
                    artifacts=[dict(path='value.json',sha256=sd.file_hash(d/'value.json'))]))
        return
    root=a.root.resolve()
    if (root/'registry/supervisor.json').exists():raise ValueError('new isolated fixture root required')
    for name in ('00_PROJECT.md','01_PLAN.md','02_SOFTWARE.md','03_DATA.md','04_STATUS.md'):
        sd.atomic(root/name,'# Isolated real scheduling fixture\n')
    sd.atomic(root/'registry/tasks.tsv','task_id\tresult_path\nQ00.02\tresults/Q00.02\n')
    source=Path(__file__).resolve();gate=dict(path='fixture.py',sha256=sd.file_hash(source))
    sd.atomic(root/'fixture.py',source.read_text())
    host=dict(driver=[sys.executable,'-B',str(source.with_name('systemd_driver.py'))],limits=dict(max_jobs=3,cpus=2,memory_gb=2))
    nodes=[]
    for name,deps,failure in [('prepare',[],False),('compute',['prepare'],False),('report',['prepare'],True)]:
        path='results/Q00.02/'+name;contract={'gates':[gate]}
        for phase in ('run','validate'):
            argv=[sys.executable,'-B',str(source),'--root',str(root),'--result',path,
                   '--fixture-phase','report_failure' if failure and phase=='run' else phase]
            contract[phase]=dict(host='local',lightweight=True,cwd=str(root),argv=argv,timeout_seconds=30,
                                resources=dict(cpus=0.2,memory_gb=0.25,gpus=0,gpu_memory_gb=0))
        nodes.append(dict(id=name,task_id='Q00.02',result_path=path,depends_on=deps,completion_policy='artifact',
                          scientific_result=False,contract=contract,approved_contract_sha256=sd.digest(contract)))
    sd.atomic(root/'registry/supervisor.json',dict(execution_policy='v2',hosts={'local':host},nodes=nodes))
    for _ in range(16):
        s=sd.Supervisor(root)  # reload every cycle to exercise restart reconciliation
        s.tick()
        if s.state['nodes']['compute']['status']=='complete' and s.state['nodes']['report']['status']=='needs_attention':break
        time.sleep(1)
    s=sd.Supervisor(root);s.tick()
    assert s.state['nodes']['prepare']['attempt']==1
    assert s.state['nodes']['compute']['attempt']==1
    assert s.state['nodes']['compute']['status']=='complete'
    assert s.state['nodes']['report']['status']=='needs_attention'
    result=dict(passed=True,real_systemd=True,restart_no_duplicate=True,report_failure_isolated=True,
                downstream_artifact_verified=True,scientific_result=False,
                jobs={i:{k:n.get(k) for k in ('job_id','status','attempt')} for i,n in s.state['nodes'].items()})
    sd.atomic(root/'acceptance.json',result);print(json.dumps(result))


if __name__=='__main__':main()
