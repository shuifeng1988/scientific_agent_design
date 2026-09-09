#!/usr/bin/env python3
"""Install a project-scoped resident service and register its child DAG monitor."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys

from supervisor_daemon import atomic, load_config


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--start',action='store_true')
    a=ap.parse_args(); root=a.root.resolve(); config=load_config(root)
    source=Path(__file__).resolve().parent
    name='scientific-supervisor-'+hashlib.sha256(str(root).encode()).hexdigest()[:12]
    unit=Path.home()/'.config/systemd/user'/f'{name}.service'
    def quote(v): return '"'+str(v).replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'
    text='\n'.join(['[Unit]','Description=Scientific Supervisor for '+str(root),
       'After=network-online.target','Wants=network-online.target','StartLimitIntervalSec=0','',
       '[Service]','Type=simple',
       'ExecStart='+ ' '.join(map(quote,[sys.executable,'-B',source/'supervisor_daemon.py','daemon','--root',root,'--interval','30'])),
       'WorkingDirectory='+str(root).replace('%','%%'),'Restart=on-failure','RestartSec=30','TimeoutStopSec=30',
       'Environment=PYTHONDONTWRITEBYTECODE=1','MemoryMax=256M','CPUQuota=20%','',
       '[Install]','WantedBy=default.target',''])
    if unit.exists() and unit.read_text()!=text:
        atomic(unit.with_suffix('.service.previous'),unit.read_text())
    atomic(unit,text)
    monitor=Path.home()/'.codex/monitor'; monitor.mkdir(parents=True,exist_ok=True)
    cmd=shlex.join([sys.executable,'-B',str(source/'supervisor_daemon.py'),'status','--root',str(root)])
    entry=dict(name=name,project=str(root),host=None,state='active',total_units=len(config['nodes']),
        progress_command=cmd,health_command=shlex.join(['systemctl','--user','is-active',name])+ ' && '+cmd,
        note='Resident dependency/resource scheduler; all child states and planner calls: provenance/supervisor/status.md')
    with (monitor/'registry.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        path=monitor/'tasks.json'; tasks=json.loads(path.read_text()) if path.exists() else []
        tasks=[t for t in tasks if t['name']!=name]; tasks.append(entry); atomic(path,tasks)
    subprocess.run(['systemctl','--user','daemon-reload'],check=True)
    subprocess.run(['systemd-analyze','--user','verify',str(unit)],check=True)
    if a.start:
        subprocess.run(['systemctl','--user','enable','--now','codex-background-monitor.service'],check=True)
        subprocess.run(['systemctl','--user','enable','--now',name],check=True)
        subprocess.run(['systemctl','--user','is-active','--quiet',name],check=True)
    print(json.dumps({'service':name,'unit':str(unit),'monitor':'tail -f ~/.codex/monitor/status.md',
                      'project_status':str(root/'provenance/supervisor/status.md')},indent=2))


if __name__=='__main__': main()
