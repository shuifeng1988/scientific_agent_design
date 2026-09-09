"""Portable project event hook for plan_results_v1 projects.

Persist the event first and deterministically rebuild managed document sections.
No scientific endpoint, approved plan text or conclusion is rewritten here.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import re

from research_workflow import (ROOT_DOCS, atomic, read, registry, tasks_table, require,
                               receipt, descriptor, verify_design, validate_package)

EVENTS = {
    "data.download.completed", "data.standardization.completed", "software.download.completed",
    "software.smoke.passed", "run.started", "run.progress", "run.completed", "run.failed",
    "qc.passed", "qc.failed", "plan.amendment.approved",
    "research.appraisal.completed", "research.appraisal.discussed",
}
STATES = {"pending", "ready", "running", "partial", "validating", "reviewing", "complete",
          "frozen", "failed", "blocked", "excluded", "draft", "approved"}
BEGIN, END = "<!-- WORKFLOW_EVENTS:BEGIN -->", "<!-- WORKFLOW_EVENTS:END -->"


def now():
    return datetime.now(timezone.utc).isoformat()


def managed(path, section):
    original = path.read_text() if path.exists() else "# Project state\n"
    block = BEGIN + "\n" + section + "\n" + END
    require(original.count(BEGIN) == original.count(END) <= 1, "ambiguous document event markers")
    if BEGIN in original:
        start, stop = original.index(BEGIN), original.index(END) + len(END)
        original = original[:start] + block + original[stop:]
    else:
        original = original.rstrip() + "\n\n" + block + "\n"
    atomic(path, original)


def safe(value):
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def rebuild(root, events):
    design = read(root / "registry/design.json")
    proposal = read(receipt(root, design["proposal"]))
    rows = [{**t, "status": t.get("status", "pending"), "next_action": t.get("next_action", "")}
            for t in proposal["tasks"]]
    lookup = {r["task_id"]: r for r in rows}
    for e in events:
        if e.get("task_id") in lookup and e.get("status"):
            lookup[e["task_id"]]["status"] = e["status"]
            lookup[e["task_id"]]["next_action"] = e.get("next_action") or e["message"]
        if e['event_type'] == 'qc.failed':
            # A draft records the problem; it never changes the approved plan.
            draft = root / 'provenance/amendment_drafts' / (e['payload_hash'] + '.json')
            if not draft.exists():
                atomic(draft, dict(state='draft', task_id=e['task_id'],
                    event_id=e['event_id'], reason=e['message'], evidence=e.get('path'),
                    plan_version=design['version'], requires_user_review=True,
                    proposed_change=None))
    atomic(root / "registry/tasks.tsv", tasks_table(rows))
    table = ["| Task | State | Results | Next action |", "|---|---|---|---|"]
    for t in rows:
        table.append("| " + " | ".join(map(safe, [t["task_id"], t["status"],
                     t["result_path"], t["next_action"]])) + " |")
    recent = ["- " + safe(e["timestamp"] + " " + e["event_type"] + ": " + e["message"])
              for e in events[-20:]]
    managed(root / "04_STATUS.md", "\n".join(table + [""] + recent))
    for prefix, name in (("data.", "03_DATA.md"), ("software.", "02_SOFTWARE.md")):
        selected = [e for e in events if e["event_type"].startswith(prefix)]
        lines = ["| Entity | Event | Evidence | SHA-256 |", "|---|---|---|---|"]
        for e in selected:
            lines.append("| " + " | ".join(map(safe, [e.get("entity_id"), e["event_type"],
                          e.get("path"), e.get("sha256")])) + " |")
        managed(root / name, "\n".join(lines))
    # Approved plan stays immutable; its registry and status links show current progress.
    index = ["# Results\n", "| Task | Report | State |", "|---|---|---|"]
    for t in rows:
        rel = str(Path(t["result_path"]).relative_to("results") / "README.md")
        index.append(f'| {safe(t["task_id"])} | [{safe(t["title"])}]({rel}) | {safe(t["status"])} |')
    atomic(root / "results/README.md", "\n".join(index) + "\n")


def emit(root, payload):
    root = Path(root).resolve()
    require(payload["event_type"] in EVENTS, "unknown event")
    require(payload.get("status") is None or payload["status"] in STATES, "invalid task state")
    verify_design(root)
    known = {r["task_id"]: r for r in registry(root)}
    if payload.get("task_id"):
        require(payload["task_id"] in known, "unknown task")
    kind = payload["event_type"]
    if kind == 'qc.failed':
        payload = {**payload, 'status': 'blocked'}
    if kind.startswith('research.appraisal.'):
        d = read(root / 'registry/design.json')
        ref = d['appraisal' if kind == 'research.appraisal.completed' else 'approval']
        require(payload.get('verified') is True and payload.get('path') == ref['path']
                and payload.get('sha256') == ref['sha256'], 'appraisal event must match frozen evidence')
    require(not kind.startswith(("run.", "qc.")) or payload.get("task_id"), "task ID required")
    if kind in {"qc.passed", "run.completed"} or kind.startswith(("data.", "software.")):
        require(payload.get("verified") is True and payload.get("path"), "verified evidence path required")
    if kind.startswith(("data.", "software.")):
        receipt(root, {"path": payload["path"], "sha256": payload.get("sha256")})
    if payload.get("path"):
        from research_workflow import inside
        require(inside(root, payload["path"]).exists(), "event evidence path missing")
    if kind == "qc.passed" or payload.get("status") in ("complete", "frozen"):
        require(kind == "qc.passed", "only qc.passed may complete a task")
        t = known[payload["task_id"]]
        require(payload.get("path") == t["result_path"], "publication path does not match task")
        result = root / t["result_path"]
        qc = read(result / "_evidence/qc.json")
        from supervisor_daemon import verify_review
        verify_review(root, dict(task_id=t["task_id"], result_path=t["result_path"], scientific_result=True),
                      dict(run_id=qc["run_id"]))
        require(read(result / "_evidence/reflection.json")["decision"] != "needs_user",
                "scientific hold prevents publication")
        payload = {**payload, "status": "complete"}
    if kind == "plan.amendment.approved":
        require(payload.get("path") and payload.get("sha256"), "hashed approval record required")
        receipt(root, {"path": payload["path"], "sha256": payload["sha256"]})
        # Recording a decision does not rewrite a frozen design.
    key = payload.get("meta", {}).get("supervisor_event")
    normalized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    event_id = key or hashlib.sha256(normalized.encode()).hexdigest()
    directory = root / "provenance"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "event.lock").open("a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        path = directory / "events.jsonl"
        events = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
        previous = next((e for e in events if e["event_id"] == event_id), None)
        if previous:
            require(previous["payload_hash"] == hashlib.sha256(normalized.encode()).hexdigest(),
                    "conflicting idempotency key")
        else:
            e = {**payload, "timestamp": now(), "event_id": event_id,
                 "payload_hash": hashlib.sha256(normalized.encode()).hexdigest()}
            events.append(e)
            # Event first: a retry repairs interrupted document rendering.
            atomic(path, "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events))
        rebuild(root, events)
    return dict(event_id=event_id, duplicate=previous is not None, documents_updated=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("event_type", choices=sorted(EVENTS))
    ap.add_argument("--root", type=Path, default=Path.cwd())
    for flag in ("task-id", "entity-id", "status", "path", "sha256", "next-action"):
        ap.add_argument("--" + flag)
    ap.add_argument("--message", default="")
    ap.add_argument("--meta-json", default="{}")
    ap.add_argument("--verified", action="store_true")
    a = ap.parse_args()
    payload = {k: v for k, v in vars(a).items() if k not in ("root", "meta_json")}
    payload["meta"] = json.loads(a.meta_json)
    print(json.dumps(emit(a.root, payload), ensure_ascii=False))


if __name__ == "__main__":
    main()
