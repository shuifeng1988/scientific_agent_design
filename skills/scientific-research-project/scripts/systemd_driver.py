#!/usr/bin/env python3
"""JSON driver for persistent local/SSH systemd user jobs; no password or shell eval."""
import argparse
import json
import os
import shlex
import subprocess
import sys
import time


def command(args, host=None, check=True):
    if host:
        args = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", host, shlex.join(args)]
    p = subprocess.run(args, text=True, capture_output=True, timeout=15)
    if check and p.returncode:
        raise RuntimeError(p.stderr[-1000:])
    return p


RESOURCE_CODE = '''import json,os,time,subprocess
m={line.split(':')[0]:int(line.split()[1]) for line in open('/proc/meminfo')}
g=[]
try:
 p=subprocess.run(['nvidia-smi','--query-gpu=uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
 if p.returncode==0:
  for line in p.stdout.splitlines():
   uid,mem,util=[x.strip() for x in line.split(',')]
   g.append({'id':uid,'free_gb':float(mem)/1024,'utilization':float(util)})
except (OSError,ValueError,subprocess.TimeoutExpired): pass
print(json.dumps({'timestamp':time.time(),'free_cpus':max(0,(os.cpu_count() or 1)-os.getloadavg()[0]),'free_memory_gb':m['MemAvailable']/1048576,'gpus':g}))
'''


def properties(job, host):
    if not job.startswith("sci-") or not all(x.isalnum() or x == '-' for x in job):
        raise ValueError("invalid owned unit ID")
    p = command(["systemctl", "--user", "show", job + ".service", "--property=LoadState,ActiveState,SubState,Result,ExecMainStatus"], host)
    return dict(line.split("=", 1) for line in p.stdout.splitlines() if "=" in line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host")
    ap.add_argument("action", choices=["resources", "launch", "status", "diagnose"])
    a = ap.parse_args()
    q = json.load(sys.stdin)
    if a.action == "resources":
        print(command(["python3", "-c", RESOURCE_CODE], a.host).stdout.strip())
        return
    prop = properties(q["job_id"], a.host)
    if a.action == 'diagnose':
        # Read only the exact owned job after terminal failure; never inspect unrelated units.
        failed = prop.get('ActiveState') == 'failed'
        result = {'state':'failed' if failed else 'unknown','reason':str(prop)}
        if failed:
            p = command(['journalctl','--user','-u',q['job_id']+'.service','-n','100',
                         '--no-pager','-o','cat'],a.host,check=False)
            result.update(log_tail=p.stdout[-16000:],log_returncode=p.returncode,
                          log_error=p.stderr[-1000:])
        print(json.dumps(result))
        return
    if a.action == "status":
        active = prop.get("ActiveState")
        if prop.get("LoadState") == "not-found":
            state = "not_found"
        elif active in ("activating", "active") and prop.get("SubState") != "exited":
            state = "running"
        elif active == "active" and prop.get("SubState") == "exited" and prop.get("ExecMainStatus") == "0":
            state = "succeeded"
        elif active == "failed":
            state = "failed"
        else:
            state = "unknown"
        # Only classified infrastructure failures auto-retry by default.
        retryable = prop.get("Result") in ("timeout", "oom-kill", "resources")
        result={"state":state,"retryable":retryable,"reason":str(prop)}
        if q.get('progress_path'):
            code="import json,sys; print(json.dumps(json.load(open(sys.argv[1]))))"
            progress=command(['python3','-c',code,q['progress_path']],a.host,check=False)
            if progress.returncode==0:
                value=json.loads(progress.stdout)
                if isinstance(value.get('completed'),int) and isinstance(value.get('total'),int) and 0<=value['completed']<=value['total']:
                    result['progress']=value
        print(json.dumps(result))
        return
    if prop.get("LoadState") != "not-found":
        print(json.dumps({"job_id": q["job_id"], "existing": True}))
        return
    s = q["spec"]
    resources = s["resources"]
    env = dict(s.get("env", {}))
    env.update(SCI_RUN_ID=q["run_id"], CUDA_VISIBLE_DEVICES=",".join(q["gpu_ids"]))
    cmd = ["systemd-run", "--user", "--unit=" + q["job_id"], "--service-type=exec",
           "--property=RemainAfterExit=yes", "--property=RuntimeMaxSec=" + str(s["timeout_seconds"]),
           "--property=WorkingDirectory=" + s["cwd"],
           "--property=MemoryMax=" + str(int(resources["memory_gb"] * 1024**3)),
           "--property=CPUQuota=" + str(int(resources["cpus"] * 100)) + "%"]
    for k, v in env.items():
        if not k.replace('_', '').isalnum():
            raise ValueError("invalid environment key")
        cmd.append("--setenv=" + k + "=" + str(v))
    cmd += ["--"] + s["argv"]
    command(cmd, a.host)
    print(json.dumps({"job_id": q["job_id"]}))


if __name__ == "__main__":
    main()
