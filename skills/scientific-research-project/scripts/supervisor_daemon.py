#!/usr/bin/env python3
"""Persistent, dependency-aware dispatcher. Drivers speak JSON, never inferred shell.

Local process only orchestrates. Each driver call must be short and idempotent;
actual jobs live in a durable scheduler (systemd/Slurm) on the declared host.
"""
from __future__ import annotations

import argparse
import copy
import csv
import fcntl
import hashlib
import io
import json
import os
import signal
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from recovery_policy import classify_failure, verify_recovery, verified_file
from structured_output import proposal_object
from budget_policy import budget, execution_used, worker_limit
from execution_policy import phases, verify_artifact, incident, apply_expansions, progression

PHASES = ("run", "validate", "interpret")
LIVE = {"submitting", "running", "unknown"}
STOP = False


def atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".supervisor-")
    with os.fdopen(fd, "w") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(name, path)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def load_config(root):
    c = json.loads((root / "registry/supervisor.json").read_text())
    nodes = c["nodes"]
    worker_config = c.get("progress_worker", {})
    if worker_config.get("budget_scope", "per_node") not in ("per_node", "legacy_project"):
        raise ValueError("invalid worker budget_scope")
    for node in nodes:
        worker_limit(worker_config, node)
        maximum = (node.get("contract") or {}).get("max_attempts", 3)
        if type(maximum) is not int or maximum < 1:
            raise ValueError("max_attempts must be a positive integer")
    if len({n["id"] for n in nodes}) != len(nodes):
        raise ValueError("duplicate node IDs")
    ids = {n["id"] for n in nodes}
    paths = [n["result_path"] for n in nodes]
    if len(paths) != len(set(paths)):
        raise ValueError("nodes must have distinct result paths")
    visited, visiting = set(), set()
    lookup = {n["id"]: n for n in nodes}
    def visit(i):
        if i in visiting:
            raise ValueError("dependency cycle: " + i)
        if i in visited:
            return
        visiting.add(i)
        for dep in lookup[i]["depends_on"]:
            if dep not in ids:
                raise ValueError("unknown dependency: " + dep)
            visit(dep)
        visiting.remove(i)
        visited.add(i)
    for n in nodes:
        visit(n["id"])
        phases(n)
        p = (root / n["result_path"]).resolve()
        if not p.is_relative_to((root / "results").resolve()):
            raise ValueError("result path outside results")
        if n.get("contract"):
            contract = n["contract"]
            required = {(g['path'],g['sha256']) for g in n.get('required_scope_gates',[])}
            if not required <= {(g['path'],g['sha256']) for g in contract.get('gates',[])}:
                raise ValueError('execution contract removed required scientific scope gates')
            for phase in phases(n):
                spec = contract[phase]
                if not spec.get("argv") or not all(isinstance(x, str) for x in spec["argv"]):
                    raise ValueError("argv required for " + phase)
                if spec["host"] not in c["hosts"]:
                    raise ValueError("unknown host")
                req = spec["resources"]
                if any(req.get(k, -1) < 0 for k in ("cpus", "memory_gb", "gpus", "gpu_memory_gb")):
                    raise ValueError("resources must be explicit nonnegative numbers")
                if req['cpus']<=0 or req['memory_gb']<=0 or not isinstance(req['gpus'],int):
                    raise ValueError('CPU/RAM must be positive; GPU count must be an integer')
                if spec["host"] == "local" and not spec.get("lightweight"):
                    raise ValueError("local computation must be explicitly lightweight")
                if spec.get("timeout_seconds", 0) <= 0:
                    raise ValueError("positive phase timeout required")
    return c


def driver(host, action, payload):
    p = subprocess.run(host["driver"] + [action], input=json.dumps(payload),
                       text=True, capture_output=True, timeout=20)
    if p.returncode:
        raise RuntimeError("driver failed: " + p.stderr[-1500:])
    return json.loads(p.stdout)


def verify_review(root, node, state):
    """Evidence belongs to this attempt; a 'passed' flag alone is insufficient."""
    result = root / node["result_path"]
    qc = json.loads((result / "_evidence/qc.json").read_text())
    rev = json.loads((result / "_evidence/reflection.json").read_text())
    if qc.get("run_id") != state["run_id"] or rev.get("run_id") != state["run_id"]:
        raise ValueError("QC/reflection run_id mismatch")
    if qc.get("passed") is not True or not qc.get("artifacts"):
        raise ValueError("QC failed or artifact hashes missing")
    for a in qc["artifacts"]:
        p = (result / a["path"]).resolve()
        if not p.is_relative_to(result.resolve()) or file_hash(p) != a["sha256"]:
            raise ValueError("output hash mismatch: " + a["path"])
    for key in ("expected", "observed", "uncertainty", "reasoning", "alternative_explanations",
                "evidence_strength", "limitations", "next_step_impact", "literature_search"):
        if not rev.get(key):
            raise ValueError("missing reflection: " + key)
    lit = rev["literature_search"]
    if not lit.get("queries") or not lit.get("searched_at") or lit.get("status") not in ("searched", "no_relevant_results"):
        raise ValueError("literature search absent/unavailable; interpretation remains pending")
    if lit["status"] == "searched" and not lit.get("sources"):
        raise ValueError("literature sources required")
    for s in lit.get("sources", []):
        if not all(s.get(k) for k in ("url", "title", "relevance", "supports_or_conflicts")):
            raise ValueError("incomplete source evidence")
    if rev.get("decision") not in ("continue", "supplement", "needs_user"):
        raise ValueError("invalid downstream decision")
    required = ["README.md", "REPORT.docx", "tables", "figures"] if node.get("scientific_result", True) else ["README.md"]
    for name in required:
        p = result / name
        if not p.exists() or (p.is_dir() and not any(x.is_file() for x in p.iterdir())):
            raise ValueError("incomplete result package: " + name)
    return rev


class Supervisor:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.directory = self.root / "provenance/supervisor"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "state.json"
        self.state = json.loads(self.path.read_text()) if self.path.exists() else {"nodes": {}, "outbox": []}

    def save(self):
        atomic(self.path, self.state)

    def sync_monitor(self):
        """Register owned child jobs without touching other projects' entries."""
        directory = Path.home()/".codex/monitor"
        if not (directory/"tasks.json").exists():
            return
        base = "scientific-job-" + digest(str(self.root))[:12] + "-"
        updates = []
        for i, s in self.state["nodes"].items():
            if not s.get("job_id"):
                continue
            active = s["status"] in LIVE or s["status"] in ("pending", "retry_wait")
            command = shlex.join([sys.executable, "-B", str(Path(__file__).resolve()), "status", "--root", str(self.root), "--node", i])
            updates.append(dict(name=base+i, project=str(self.root), host=None,
                state="active" if active else "completed" if s["status"]=="complete" else "needs_attention",
                total_units=s.get('progress',{}).get('total',3), progress_command=command, health_command=command,
                note="Owned child job on "+s["spec"]["host"]+": "+s["job_id"]))
        w = self.state.get("worker", {})
        if w.get("job_id"):
            command = shlex.join([sys.executable,"-B",str(Path(__file__).resolve()),"status","--root",str(self.root),"--worker"])
            updates.append(dict(name=base+"progress-worker", project=str(self.root), host=None,
                state="active" if w.get("status") in LIVE else "completed" if w.get("status")=="complete" else "needs_attention",
                total_units=1, progress_command=command, health_command=command, note=w["job_id"]))
        with (directory/"registry.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            p=directory/"tasks.json"; old=json.loads(p.read_text()); names={u["name"] for u in updates}
            for entry in old:
                if entry.get('project') == str(self.root) and entry['name'].startswith('scientific-supervisor-'):
                    entry['total_units'] = len(self.state['nodes'])
            atomic(p,[x for x in old if x["name"] not in names]+updates)

    def event(self, node, kind, message, status="partial", persist=True):
        e = {"node": node["id"], "task": node["task_id"], "kind": kind,
             "message": message, "status": status, "time": time.time(), "path": node["result_path"]}
        e["id"] = digest(e)
        self.state["outbox"].append(e)
        ns = self.state['nodes'].get(node['id'], {})
        if ns.get('execution_policy') == 'v2' and node.get('finalizes_task') and status == 'complete':
            ns.update(status='publishing', publication_event=e['id'],
                      reason='awaiting verified publication hook; scientific dependents remain held')
        if persist:
            self.save()

    def flush_events(self):
        hook = self.root / "scripts/hooks/project_event.py"
        if not hook.exists():
            return False
        for e in list(self.state["outbox"]):
            cmd = [sys.executable, "-B", str(hook), e["kind"], "--task-id", e["task"],
                   "--status", e["status"], "--message", e["message"],
                   "--meta-json", json.dumps({"supervisor_event": e["id"], "node": e["node"]})]
            if e["kind"] in ("qc.passed", "run.completed"):
                cmd += ["--verified", "--path", e["path"]]
            p = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, timeout=20)
            if p.returncode:
                self.state["hook_error"] = p.stderr[-1500:]
                self.save()
                return False
            with (self.directory / "events.jsonl").open("a") as f:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
            self.state["outbox"].remove(e)
            node_state = self.state['nodes'].get(e['node'], {})
            if node_state.get('publication_event') == e['id']:
                node_state.update(status='complete', reason='scientific package and publication hook verified')
                node_state.pop('publication_event', None)
                self.state['last_verified_progress'] = time.time()
            self.save()
        self.state.pop("hook_error", None)
        return True

    def fail(self, n, s, why, technical=False, job_failure=False, probe=None):
        maximum = n["contract"].get("max_attempts", 3)
        # A retryable infrastructure flag is not a diagnosis or a validated repair.
        evidence = dict(probe or {}, state='failed' if job_failure else 'evidence_failed', reason=why)
        if job_failure:
            try:
                detail = driver(s['host_config'], 'diagnose', {'job_id': s['job_id'], 'run_id': s['run_id']})
                if detail.get('state') == 'failed':
                    evidence.update(detail)
            except Exception as exc:
                evidence['diagnostic_error'] = str(exc)
        diagnosis = classify_failure(evidence)
        record = self.root/n['result_path']/'_evidence/failures'/(s.get('job_id',s['run_id'])+'.json')
        if not record.exists():
            atomic(record, dict(node=n['id'], run_id=s['run_id'], phase=s['phase'],
                                at=time.time(), failed_state=copy.deepcopy(s), diagnosis=diagnosis))
        s['failure_record'] = dict(path=str(record.relative_to(self.root)), sha256=file_hash(record))
        s['failure_category'] = diagnosis['category']
        s["status"] = "needs_attention"
        s["reason"] = 'diagnosis required ('+diagnosis['category']+'): '+str(why)
        if s.get('execution_policy') == 'v2':
            recovery = incident(self.state, s)
            s['repairable'] = job_failure and recovery['worker_calls'] < 3 and recovery['retries'] < 3
            s['repair_budget_remaining'] = 3-recovery['retries']
        else:
            s["repairable"] = job_failure and execution_used(s) < maximum
        s["retry_after"] = time.time() + min(1800, 30 * 2 ** (s["attempt"] - 1))
        self.event(n, "run.failed", s['reason']+'; evidence: '+s['failure_record']['path'])

    def advance_worker(self, c):
        """Wake a scoped planner on idle blockers; bounded calls and durable ID.

        Worker writes proposals, not scheduler state. It can fill contracts for
        existing nodes only. Frozen scientific scope and dependencies stay fixed.
        """
        w = c.get("progress_worker", {})
        if not w.get("enabled") or c.get("paused") or (self.directory / "PAUSE").exists():
            return
        ws = self.state.setdefault("worker", {"calls": [], "next_at": 0})
        host = c["hosts"]["local"]
        if ws.get("status") in LIVE:
            terminal = False
            try:
                p = driver(host, "status", {"job_id": ws["job_id"]})
                if p["state"] == "not_found" and ws["status"] == "submitting":
                    driver(host, "launch", ws["payload"])
                    return
                if p["state"] in ("queued", "running"):
                    ws["status"] = "running"
                    return
                if p["state"] == "succeeded":
                    terminal = True
                    if digest(c) != ws["config_hash"]:
                        raise ValueError("config changed during worker; proposal retained for reconciliation")
                    proposal, _ = proposal_object(Path(ws["request"]).with_name("proposal.json").read_text())
                    candidate, added = apply_expansions(c, self.state['nodes'], ws['requested'], proposal.get('expansions', []))
                    c = candidate
                    lookup = {n["id"]: n for n in c["nodes"]}
                    repaired=[]
                    for item in proposal["contracts"]:
                        i = item["id"]
                        ns=self.state["nodes"].get(i,{})
                        if i not in ws["requested"] or (ns.get("attempt",0) != 0 and not ns.get("repairable")):
                            raise ValueError("worker cannot replace attempted/unrequested contracts")
                        if ns.get("repairable"):
                            recovery = verify_recovery(self.root, lookup[i], ns, item)
                            repaired.append((i, recovery))
                        lookup[i]["contract"] = item["contract"]
                        lookup[i]["approved_contract_sha256"] = digest(item["contract"])
                        lookup[i]["contract_authority"] = "standing scope; progress worker " + ws["job_id"]
                    # Validate proposals on a separate temporary project skeleton,
                    # so malformed output never replaces the live config.
                    with tempfile.TemporaryDirectory() as tmp:
                        trial = Path(tmp)
                        atomic(trial/"registry/supervisor.json", c)
                        load_config(trial)
                    atomic(self.root / "registry/supervisor.json", c)
                    for i in added:
                        self.state['nodes'][i] = dict(status='pending', attempt=0, phase='run',
                                                     recovery_key=lookup[i]['recovery_key'], execution_policy='v2')
                    supplied={x['id'] for x in proposal['contracts']}
                    expanded={e['parent_id'] for e in proposal.get('expansions', []) if e['nodes']}
                    if supplied or added:
                        self.state['last_verified_progress'] = time.time()
                    for i in ws['requested']:
                        ns=self.state['nodes'][i]
                        ns.pop('worker_failure_record',None)
                        ns['planner_visits']=ns.get('planner_visits',0)+1
                        if i in supplied or i in expanded:
                            ns['no_progress_visits'] = 0
                        elif c.get('execution_policy') == 'v2':
                            ns['no_progress_visits'] = ns.get('no_progress_visits',0)+1
                        if i not in supplied and i not in expanded:
                            ns['planner_next_at']=time.time()+min(21600,600*2**min(ns['planner_visits'],5))
                    for i, recovery in repaired:
                        ns=self.state["nodes"][i]
                        atomic(self.directory/"attempts"/(ns["job_id"]+".json"),ns)
                        ns.update(status="pending", contract_hash=digest(lookup[i]["contract"]),
                                  resume_pending=True, recovery=recovery,
                                  repairable=False, reason="diagnosis + minimal validation passed; resume failed phase")
                        self.event(lookup[i], 'run.progress', 'targeted repair validated; resume '+ns['phase']+' only')
                    for item in proposal["blocked"]:
                        if item["id"] in ws["requested"]:
                            ns = self.state["nodes"][item["id"]]
                            ns["reason"] = item["reason"]
                            ns['worker_blocker']=item['reason']
                            if item.get("needs_user"):
                                ns["status"] = "needs_user"
                    ws.update(status="complete", reason="proposal applied", next_at=time.time()+w.get("cooldown_seconds", 600))
                elif p["state"] == "failed":
                    terminal = True
                    try:
                        detail=driver(host,'diagnose',{'job_id':ws['job_id']})
                    except Exception as exc:
                        detail=dict(p,diagnostic_error=str(exc))
                    failure_path=Path(ws['request']).with_name('failure.json')
                    if not failure_path.exists():
                        artifacts=[]
                        for name in ('request.json','proposal.raw.txt','worker_stdout.log','worker_stderr.log'):
                            source=failure_path.with_name(name)
                            if source.exists():
                                artifacts.append(dict(path=str(source.relative_to(self.root)),sha256=file_hash(source)))
                        atomic(failure_path,dict(job_id=ws['job_id'],requested=ws['requested'],
                                                diagnosis=classify_failure(detail),artifacts=artifacts))
                    ws['failure_record']=dict(path=str(failure_path.relative_to(self.root)),sha256=file_hash(failure_path))
                    ws.update(status="failed", reason=p.get("reason"), next_at=time.time()+w.get("failure_backoff_seconds",1800))
                    for i in ws['requested']:
                        ns=self.state['nodes'][i]
                        ns['planner_visits']=ns.get('planner_visits',0)+1
                        ns['worker_failure_record']=ws['failure_record']
                        if classify_failure(detail)['category']=='credentials':
                            ns.update(status='needs_user',reason='worker credentials failed; restore authentication before retry')
                else:
                    ws.update(status="unknown", reason="worker state unknown; no duplicate launch")
            except Exception as exc:
                ws.update(status="needs_attention" if terminal else "unknown", reason=str(exc), next_at=time.time()+1800)
            self.save()
            return
        if time.time() < ws["next_at"]:
            return
        v2 = c.get('execution_policy') == 'v2'
        per_node = w.get("budget_scope", "per_node") == "per_node"
        if not per_node:
            ws["calls"] = [t for t in ws["calls"] if time.time()-t < 86400]
        if any(s["status"] in LIVE and s["spec"]["host"] == "local" for s in self.state["nodes"].values()):
            ws["reason"] = "waiting local worker resource slot"
            return
        requested = [n for n in c["nodes"] if ((self.state["nodes"][n["id"]]["status"] == "pending"
                     and self.state["nodes"][n["id"]]["attempt"] == 0 and not n.get("contract"))
                     or (self.state["nodes"][n["id"]]["status"] == "needs_attention" and self.state["nodes"][n["id"]].get("repairable")))
                     and time.time()>=self.state['nodes'][n['id']].get('planner_next_at',0)
                     and time.time()>=self.state['nodes'][n['id']].get('retry_after',0)
                     and all(self.state["nodes"][d]["status"] == "complete" for d in n["depends_on"])]
        if per_node:
            eligible = []
            for n in requested:
                ns = self.state['nodes'][n['id']]
                repairing_node = ns.get('repairable') or ns.get('worker_failure_record')
                if v2 and not repairing_node and ns.get('no_progress_visits',0) >= w.get('max_no_progress_visits',2):
                    ns['reason'] = 'planning_stalled: no executable contract or authorized child tasks; targeted implementation required'
                elif v2 and repairing_node and incident(self.state, ns)['worker_calls'] >= 3:
                    ns['reason'] = 'repair budget exhausted for this task/phase; human intervention required'
                elif not v2 and budget(ns)['worker_calls'] >= worker_limit(w, n):
                    ns['reason'] = 'task worker budget exhausted; targeted human intervention required'
                else:
                    eligible.append(n)
            requested = eligible
        priority = w.get('priority_nodes', [])
        requested.sort(key=lambda n:(not self.state['nodes'][n['id']].get('repairable',False),
                                     not bool(self.state['nodes'][n['id']].get('worker_failure_record')),
                                     priority.index(n['id']) if n['id'] in priority else len(priority),
                                     self.state['nodes'][n['id']].get('planner_visits',0)))
        grant = w.get('manual_dispatch', {})
        manual = (not per_node and grant.get('id') and grant.get('authority') and grant.get('expires_at',0)>time.time()
                  and grant['id'] not in ws.get('consumed_dispatches', [])
                  and any(n['id']==grant.get('node_id') for n in requested))
        if manual:
            requested = [n for n in requested if n['id']==grant['node_id']]
        else:
            requested = requested[:w.get("batch_size", 1)]
        if not requested:
            ws['reason'] = 'no dependency-ready planning or repair requests'
            return
        repairing = any(self.state['nodes'][n['id']].get('repairable') or
                        self.state['nodes'][n['id']].get('worker_failure_record') for n in requested)
        cap = w.get('max_calls_per_day',12)
        reserve = min(cap, max(0,w.get('repair_reserved_calls',min(2,max(0,cap-2)))))
        limit = cap if repairing else cap-reserve
        if not per_node and len(ws['calls'])>=limit and not manual:
            ws['reason'] = ('daily worker call budget reached' if len(ws['calls'])>=cap
                            else 'planning budget reached; remaining calls reserved for repair')
            return
        r = driver(host, "resources", {})
        if r["free_cpus"] < 1 or r["free_memory_gb"] < 2 or time.time()-r["timestamp"]>60:
            ws["reason"] = "waiting worker resources"
            return
        stamp = str(time.time_ns())
        request = self.directory / "worker" / stamp / "request.json"
        atomic(request, {"root": str(self.root), "nodes": requested,
                         "source_protocol": str(Path(__file__).resolve().parents[1]/"references/continuous_execution.md"),
                         "recovery_protocol": str(Path(__file__).resolve().parents[1]/"references/failure_recovery.md"),
                         "state": self.state["nodes"]})
        spec = {"host":"local", "lightweight":True, "cwd":str(self.root),
                "argv": w["argv"] + ["--root", str(self.root), "--request", str(request)],
                "timeout_seconds":w.get("timeout_seconds",1800),
                "resources":{"cpus":1,"memory_gb":2,"gpus":0,"gpu_memory_gb":0}}
        job = "sci-" + digest([str(self.root), "planner", stamp])[:24]
        payload = {"job_id":job,"run_id":"planner-"+stamp,"spec":spec,"gpu_ids":[],"root":str(self.root)}
        ws.update(status="submitting", job_id=job, request=str(request), payload=payload,
                  config_hash=digest(c), requested=[n["id"] for n in requested],
                  purpose='repair' if repairing else 'planning',
                  reason='diagnose/repair worker dispatched' if repairing else 'planning worker dispatched')
        if manual:
            ws.setdefault('consumed_dispatches',[]).append(grant['id'])
            ws['dispatch_authority'] = copy.deepcopy(grant)
        for n in requested:
            ns = self.state['nodes'][n['id']]
            budget(ns)['worker_calls'] += 1  # lifetime cost telemetry, not a v2 planning cap
            if v2 and (ns.get('repairable') or ns.get('worker_failure_record')):
                incident(self.state, ns)['worker_calls'] += 1
        ws["calls"].append(time.time())
        self.save()
        self.sync_monitor()
        driver(host, "launch", payload)

    def tick(self):
        c = load_config(self.root)
        for name in ("00_PROJECT.md", "01_PLAN.md", "02_SOFTWARE.md", "03_DATA.md", "04_STATUS.md"):
            if not (self.root / name).is_file():
                raise ValueError("missing core document: " + name)
        with (self.root / "registry/tasks.tsv").open() as f:
            registered = {r["task_id"]: r for r in csv.DictReader(f, delimiter="\t")}
        for n in c["nodes"]:
            if n["task_id"] not in registered:
                raise ValueError("node not linked to registry/tasks.tsv: " + n["id"])
            parent = (self.root / registered[n["task_id"]]["result_path"]).resolve()
            if not (self.root / n["result_path"]).resolve().is_relative_to(parent):
                raise ValueError("node result must be under registered task result")
            if n.get('finalizes_task') and (self.root/n['result_path']).resolve()!=parent:
                raise ValueError('final task QC must refer to the registered parent result package')
        states = self.state["nodes"]
        for n in c["nodes"]:
            states.setdefault(n["id"], {"status": "pending", "attempt": 0, "phase": "run"})
            ns = states[n['id']]
            ns.setdefault('recovery_key', n.get('recovery_key', n['id']))
            if c.get('execution_policy') == 'v2':
                ns['execution_policy'] = 'v2'
            if 'budget' not in ns:
                budget(ns)
                active_worker = self.state.get('worker', {})
                if active_worker.get('status') in LIVE and n['id'] in active_worker.get('requested', []):
                    ns['budget']['worker_calls'] += 1
            if n.get("imported_evidence"):
                if registered[n["task_id"]]["status"] not in ("complete", "frozen"):
                    raise ValueError("imported task lacks frozen registry status")
                for e in n["imported_evidence"]:
                    if file_hash(self.root/e["path"]) != e["sha256"]:
                        raise ValueError("imported frozen evidence hash changed")
                states[n["id"]].update(status="complete", reason="existing frozen evidence verified; no rerun")
        # A removed live node is an error: dropping it would lose its resource lease.
        if any(s["status"] in LIVE for i, s in states.items() if i not in {n["id"] for n in c["nodes"]}):
            raise ValueError("live node removed from DAG")
        hooks_ok = self.flush_events()
        # Keep the planning worker accounted for in the local resource pool.
        for n in c["nodes"]:
            s = states[n["id"]]
            if s["status"] not in LIVE:
                continue
            # Reconcile with the saved launch contract even if config was edited.
            spec, host = s["spec"], s["host_config"]
            try:
                probe = driver(host, "status", {"job_id": s["job_id"], "run_id": s["run_id"],
                                                "progress_path":spec.get('progress_path')})
                ps = probe["state"]
            except Exception as exc:
                s.update(status="unknown", reason=str(exc))
                continue
            if ps in ("running", "queued"):
                s.update(status="running", reason=ps, progress=probe.get("progress", {}))
            elif ps == "not_found" and s["status"] == "submitting":
                try:
                    driver(host, "launch", s["launch_payload"])
                except Exception as exc:
                    s["reason"] = str(exc)
                # Keep submitting: query known id before repeating idempotent launch.
            elif ps == "succeeded":
                sequence = phases(n)
                if s['phase'] == 'validate' and n.get('completion_policy') == 'artifact':
                    try:
                        verify_artifact(self.root, n, s)
                    except Exception as exc:
                        self.fail(n,s,'artifact validation: '+str(exc))
                        continue
                    s.update(status='complete',artifact_verified=True,reason='artifact verified; scientific/report release remains separate')
                    self.state['last_verified_progress'] = time.time()
                    self.event(n,'run.progress','verified artifact complete: '+n['id'])
                elif s["phase"] != sequence[-1]:
                    self.event(n,"run.progress",s['run_id']+'/'+s['phase']+' process exited successfully; downstream evidence checks remain')
                    s.update(status="pending", phase=sequence[sequence.index(s["phase"]) + 1], reason="phase completed")
                    s.pop('progress',None)
                else:
                    try:
                        rev = verify_review(self.root, n, s)
                    except Exception as exc:
                        self.fail(n, s, "evidence validation: " + str(exc))
                        continue
                    s["status"] = "needs_user" if rev["decision"] == "needs_user" else "complete"
                    s["reason"] = str(rev["next_step_impact"])
                    if s["status"] == "complete":
                        self.state["last_verified_progress"] = time.time()
                        self.event(n,"run.completed",'run outputs validated: '+s['run_id'],"validating" if n.get('finalizes_task') else "partial",
                                   persist=not (c.get('execution_policy') == 'v2' and n.get('finalizes_task')))
                        self.event(n, "qc.passed" if n.get("scientific_result", True) and n.get('finalizes_task') else "run.progress",
                                   "verified node complete: " + n["id"],
                                   "complete" if n.get("finalizes_task") else "partial")
                    else:
                        self.event(n, "qc.failed", "downstream scientific hold: " + s["reason"], "blocked")
            elif ps == "failed":
                self.fail(n, s, probe.get("reason", "job failed"), job_failure=True, probe=probe)
            else:
                s.update(status="unknown", reason="cannot confirm remote terminal state")
        self.save()
        hooks_ok = self.flush_events() and hooks_ok
        resources = {}
        for name, host in c["hosts"].items():
            try:
                r = driver(host, "resources", {})
                if time.time() - r["timestamp"] > 60:
                    raise ValueError("stale resource probe")
                resources[name] = r
            except Exception as exc:
                resources[name] = {"error": str(exc)}
        for n in c["nodes"]:
            s = states[n["id"]]
            if s["status"] not in ("pending", "retry_wait"):
                continue
            contract = n.get("contract")
            if not contract or n.get("approved_contract_sha256") != digest(contract):
                s["reason"] = "needs_execution_contract" + (": " + s['worker_blocker'] if s.get('worker_blocker') else '')
                continue
            if s.get("contract_hash") and s["contract_hash"] != digest(contract):
                s["reason"] = "contract_changed_during_attempt; reconcile before resume"
                continue
            if any(states[d]["status"] != "complete" for d in n["depends_on"]):
                s["reason"] = "waiting_dependencies"
                continue
            if (not hooks_ok and (c.get('execution_policy') != 'v2' or n.get('finalizes_task'))) or c.get("paused") or (self.directory / "PAUSE").exists():
                s["reason"] = "paused_or_hook_failure"
                continue
            if s["status"] == "retry_wait":
                s.update(status='needs_attention', reason='legacy retry held: diagnose and verify repair first')
                continue
            try:
                for g in contract["gates"]:
                    if file_hash(self.root / g["path"]) != g["sha256"]:
                        raise ValueError(g["path"])
                if not contract["gates"]:
                    raise ValueError("no input/contract evidence gates")
                if s.get('resume_pending'):
                    verified_file(self.root, s['recovery']['validation'], self.root/n['result_path'])
                    for g in s['recovery'].get('preserved_artifacts',[]):
                        verified_file(self.root, g, self.root/n['result_path'])
            except Exception as exc:
                s["reason"] = "input_gate_failed: " + str(exc)
                continue
            spec = copy.deepcopy(contract[s["phase"]])
            host_name = spec["host"]
            r = resources[host_name]
            live = [x for x in states.values() if x["status"] in LIVE and x["spec"]["host"] == host_name]
            req = spec["resources"]
            limits = c["hosts"][host_name]["limits"]
            busy_gpus = {gpu for x in live for gpu in x.get("gpu_ids", [])}
            free_gpus = [g["id"] for g in r.get("gpus", []) if g["id"] not in busy_gpus
                         and g["free_gb"] >= req["gpu_memory_gb"] and g["utilization"] <= limits.get("max_gpu_utilization", 10)]
            cpu_used = sum(x["spec"]["resources"]["cpus"] for x in live)
            mem_used = sum(x["spec"]["resources"]["memory_gb"] for x in live)
            worker_live = host_name == "local" and self.state.get("worker",{}).get("status") in LIVE
            if worker_live:
                wr = self.state["worker"]["payload"]["spec"]["resources"]
                cpu_used += wr["cpus"]
                mem_used += wr["memory_gb"]
            # A planner is a resource reservation, not an unconditional ban on
            # lightweight transport/QC. Unknown worker state retains its lease.
            if ("error" in r or len(live) + int(worker_live) >= limits["max_jobs"]
                or req["cpus"] > min(r.get("free_cpus", 0), limits["cpus"] - cpu_used)
                or req["memory_gb"] > min(r.get("free_memory_gb", 0), limits["memory_gb"] - mem_used)
                or len(free_gpus) < req["gpus"]):
                s["reason"] = "waiting_resources" + (": " + r["error"] if "error" in r else "")
                continue
            # Reserve before submission; resource observations consumed within tick.
            resumed = s.get('resume_pending',False)
            v2 = c.get('execution_policy') == 'v2'
            if v2 and resumed and incident(self.state,s)['retries'] >= 3:
                s.update(status='needs_attention',reason='phase recovery attempts exhausted')
                continue
            if not v2 and (resumed or s['phase']=='run') and execution_used(s)>=contract.get('max_attempts',3):
                s.update(status='needs_attention',reason='repair attempt budget exhausted')
                continue
            if v2 and resumed:
                incident(self.state,s)['retries'] += 1
            if s["phase"] == "run":
                if s.get("run_id"):
                    atomic(self.directory/"attempts"/(s["run_id"]+".json"),s)
                s["attempt"] += 1
                s["run_id"] = n["id"] + ".R" + str(s["attempt"]).zfill(3)
            elif resumed:
                s['attempt'] += 1
            key = [str(self.root), s['run_id'], s['phase']]
            if resumed or s.get('phase_replay'):
                key.append(s['attempt'])
            s['phase_replay'] = resumed or s.get('phase_replay',False)
            s.pop('resume_pending',None)
            s["job_id"] = "sci-" + digest(key)[:24]
            spec.setdefault('env',{}).update(SCI_ATTEMPT=str(s['attempt']),SCI_JOB_ID=s['job_id'])
            s.update(spec=spec, host_config=c["hosts"][host_name], status="submitting",
                     gpu_ids=free_gpus[:req["gpus"]], contract_hash=digest(contract), started=time.time())
            s["launch_payload"] = {"job_id": s["job_id"], "run_id": s["run_id"], "spec": spec,
                                   "gpu_ids": s["gpu_ids"], "root": str(self.root)}
            self.save()
            self.sync_monitor()
            self.event(n, "run.started", "submitting " + s["run_id"] + "/" + s["phase"])
            if not self.flush_events() and (c.get('execution_policy') != 'v2' or n.get('finalizes_task')):
                s["status"] = "pending"
                continue
            try:
                driver(s["host_config"], "launch", s["launch_payload"])
            except Exception as exc:
                s["reason"] = "submission uncertain: " + str(exc)
            # Never resubmit with another ID after an uncertain SSH response.
            r["free_cpus"] -= req["cpus"]
            r["free_memory_gb"] -= req["memory_gb"]
        self.state["heartbeat"] = time.time()
        self.state["resources"] = resources
        if hooks_ok or c.get('execution_policy') == 'v2':
            self.advance_worker(c)
        c = load_config(self.root)  # worker may have atomically adopted a DAG expansion
        self.state['progression'] = progression(self.state, c)
        self.save()
        self.sync_monitor()
        self.render(c)

    def intervene(self, c, node_id, reason):
        """Explicit operator action, under daemon lock; not a status-query hook."""
        if not reason or not reason.strip():
            raise ValueError('human intervention reason required')
        n = next(n for n in c['nodes'] if n['id'] == node_id)
        s = self.state['nodes'][node_id]
        if n.get('imported_evidence') or s['status'] not in ('pending', 'needs_attention'):
            raise ValueError('cannot reset live, unknown, completed or scientific-hold node')
        w = self.state.get('worker', {})
        if w.get('status') in LIVE and node_id in w.get('requested', []):
            raise ValueError('target worker is live or unknown; reconcile first')
        terminal_failure = False
        if s.get('job_id'):
            failure = s.get('failure_record')
            if not failure:
                raise ValueError('attempted node requires exact terminal failure evidence')
            record = json.loads(verified_file(self.root, failure, self.root/n['result_path']).read_text())
            if record.get('job_id', record.get('failed_state', {}).get('job_id')) != s['job_id']:
                raise ValueError('failure evidence does not match current job')
            if record.get('diagnosis', {}).get('evidence', {}).get('state') != 'failed':
                raise ValueError('QC/scientific hold cannot be reset by budget intervention')
            probe = driver(s['host_config'], 'status', {'job_id': s['job_id']})
            if probe.get('state') != 'failed':
                raise ValueError('terminal job failure not confirmed; no reset')
            terminal_failure = True
        old = copy.deepcopy(budget(s))
        entry = dict(node=node_id, reason=reason.strip(), at=time.time(), previous_budget=old,
                     lifetime_attempt=s.get('attempt', 0), job_id=s.get('job_id'),
                     failure_record=s.get('failure_record'))
        path = self.directory/'interventions'/(str(time.time_ns())+'.json')
        atomic(path, entry)
        s.setdefault('interventions', []).append(dict(path=str(path.relative_to(self.root)), sha256=file_hash(path)))
        s['budget'] = dict(round=old['round']+1, worker_calls=0, execution_base=s.get('attempt', 0))
        if c.get('execution_policy') == 'v2':
            s['recovery_key'] = n.get('recovery_key',node_id)
            for key, value in self.state.get('recovery_incidents', {}).items():
                if key.startswith(s['recovery_key']+':'):
                    value['history'].append({k:v for k,v in value.items() if k!='history'})
                    value.update(worker_calls=0,retries=0,round=value['round']+1)
            s['no_progress_visits'] = 0
        s['planner_next_at'] = s['retry_after'] = 0
        if terminal_failure:
            s['repairable'] = True
        s['reason'] = 'human intervention: task budget reset; diagnosis and validation remain required'
        if w.get('status') not in LIVE:
            w['next_at'] = 0
        self.save()
        self.event(n, 'run.progress', s['reason']+'; '+str(path.relative_to(self.root)))
        return entry

    def render(self, c):
        states = self.state["nodes"]
        if c.get('execution_policy') == 'v2':
            table = self.root/'registry/task_dependencies.tsv'
            archive = self.directory/'task_dependencies.before_v2.tsv'
            if table.exists() and not archive.exists():
                atomic(archive, table.read_text())
            stream = io.StringIO()
            writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
            writer.writerow(['node_id','task_id','model_id','stage','depends_on','result_path',
                             'completion_policy','host','phase','status','job_id'])
            for node in c['nodes']:
                ns = states[node['id']]
                run = (node.get('contract') or {}).get('run', {})
                writer.writerow([node['id'],node['task_id'],node.get('model_id',''),node.get('stage',''),
                                 ';'.join(node['depends_on']),node['result_path'],node.get('completion_policy','report'),
                                 run.get('host','unconfigured'),ns['phase'],ns['status'],ns.get('job_id','')])
            atomic(table,stream.getvalue())
        lines = ["# Supervisor dependencies and live state", "", "Updated UTC epoch: " + str(self.state["heartbeat"]), "",
                 "| Node | Task | Dependencies | Phase | State | Lifetime attempts | Round / AI calls / execution | Reason |", "|---|---|---|---|---|---:|---|---|"]
        for n in c["nodes"]:
            s = states[n["id"]]
            reason = str(s.get("reason", "")).replace("|", "/").replace("\n", " ")
            counts = f"{budget(s)['round']} / {budget(s)['worker_calls']}/{worker_limit(c.get('progress_worker', {}), n)} / {execution_used(s)}/{(n.get('contract') or {}).get('max_attempts',3)}"
            if c.get('execution_policy') == 'v2':
                recovery = incident(self.state,s)
                counts = f"AI total {budget(s)['worker_calls']}; repair {recovery['worker_calls']}/3; replay {recovery['retries']}/3"
            lines.append(f"| {n['id']} | {n['task_id']} | {', '.join(n['depends_on']) or '—'} | {s['phase']} | {s['status']} | {s['attempt']} | {counts} | {reason} |")
        if c.get('execution_policy') == 'v2':
            health = progression(self.state,c)
            lines += ['', 'Project progression: '+health['status']+'; active jobs='+str(health['active_jobs']),
                      'AI calls are cost telemetry; failure recovery is independently bounded per task/phase.']
        lines += ["", "Artifact nodes advance after run → hashed validation; report nodes require interpretation, and scientific publication requires hook acknowledgement. Unknown remote state retains resources.", ""]
        if self.state.get("worker"):
            w = self.state["worker"]
            lines += ["Progress worker: " + w.get("status", "idle") + "; " + str(w.get("reason", "")), ""]
        atomic(self.directory / "status.md", "\n".join(lines))
        for file, marker in (("01_PLAN.md", "SUPERVISOR_DEPENDENCIES"), ("04_STATUS.md", "SUPERVISOR_STATUS")):
            path = self.root / file
            start, end = f"<!-- AUTO:{marker}:START -->", f"<!-- AUTO:{marker}:END -->"
            text = path.read_text()
            block = start + "\n" + "\n".join(lines[2:]) + "\n" + end
            if start in text:
                text = text.split(start)[0] + block + text.split(end, 1)[1]
            else:
                text += "\n" + block + "\n"
            atomic(path, text)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["daemon", "tick", "status", "check", "intervene"])
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--node")
    ap.add_argument("--reason")
    ap.add_argument("--worker", action="store_true")
    a = ap.parse_args()
    root = a.root.resolve()
    if a.mode == "check":
        c = load_config(root)
        print(json.dumps({"nodes": len(c["nodes"]), "contracts": sum(bool(n.get('contract')) for n in c['nodes']), "dag": "acyclic"}))
        return
    if a.mode == "status":
        p = root / "provenance/supervisor/state.json"
        s = json.loads(p.read_text())
        if a.worker:
            item=s.get("worker",{})
            print("completed="+str(int(item.get("status")=="complete")))
        elif a.node:
            item=s['nodes'][a.node]
            progress=item.get('progress',{})
            count=(progress.get('total',3) if item['status']=='complete' else progress.get('completed',PHASES.index(item['phase'])))
            print("completed="+str(count))
        else:
            item={}
            print("completed=" + str(sum(n['status'] == 'complete' for n in s['nodes'].values())))
        if not a.node and not a.worker and s.get('progression',{}).get('status') == 'stalled':
            print('project_stalled: service alive but no runnable jobs; see per-node blockers',file=sys.stderr)
            raise SystemExit(2)
        if time.time() - s.get("heartbeat", 0) > 180:
            raise SystemExit(2)
        if item.get("status") in ("unknown","needs_attention","needs_user","failed"):
            print(str(item.get("reason","")),file=sys.stderr)
            raise SystemExit(2)
        return
    supervisor = Supervisor(root)
    with (supervisor.directory / "daemon.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        supervisor = Supervisor(root)  # read state only after acquiring the writer lock
        if a.mode == 'intervene':
            if not a.node or not a.reason:
                ap.error('intervene requires --node and --reason')
            c = load_config(root)
            print(json.dumps(supervisor.intervene(c, a.node, a.reason), ensure_ascii=False))
            supervisor.flush_events()
            supervisor.render(c)
            supervisor.sync_monitor()
            return
        def stop(*_):
            global STOP
            STOP = True
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        while not STOP:
            supervisor.tick()
            if a.mode == "tick":
                break
            # Sleep in small increments so service stop remains responsive.
            until = time.monotonic() + max(5, a.interval)
            while not STOP and time.monotonic() < until:
                time.sleep(1)


if __name__ == "__main__":
    main()
