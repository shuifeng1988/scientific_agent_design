#!/usr/bin/env python3
"""Guarded Supervisor Agent for the scientific-research-project skill."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path


ROOT_DOCS = (
    "00_PROJECT.md",
    "01_PLAN.md",
    "02_SOFTWARE.md",
    "03_DATA.md",
    "04_STATUS.md",
)
READY_STATES = {"pending", "ready", "partial"}
TERMINAL_STATES = {"complete", "frozen", "excluded"}


def root_path(value: str | None) -> Path:
    return Path(value).resolve() if value else Path.cwd().resolve()


def load_tasks(root: Path) -> list[dict[str, str]]:
    path = root / "registry/tasks.tsv"
    if not path.exists():
        raise RuntimeError(f"missing registry: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise RuntimeError("empty task registry")
    fields = lines[0].split("\t")
    return [dict(zip(fields, line.split("\t"))) for line in lines[1:] if line.strip()]


def package_check(root: Path, result_path: str) -> dict:
    directory = root / result_path
    checks = {
        "directory": directory.is_dir(),
        "README.md": (directory / "README.md").is_file(),
        "REPORT.docx": (directory / "REPORT.docx").is_file(),
        "tables": (directory / "tables").is_dir()
        and any(item.is_file() for item in (directory / "tables").iterdir()),
        "figures": (directory / "figures").is_dir()
        and any(item.is_file() for item in (directory / "figures").iterdir()),
        "_evidence": (directory / "_evidence").is_dir(),
    }
    return checks


def inspect(root: Path) -> dict:
    missing_docs = [name for name in ROOT_DOCS if not (root / name).is_file()]
    tasks = load_tasks(root)
    task_checks = []
    for task in tasks:
        task_checks.append(
            {
                "task_id": task["task_id"],
                "question_id": task["question_id"],
                "status": task["status"],
                "result_path": task["result_path"],
                "result_path_exists": (root / task["result_path"]).is_dir(),
                "package": package_check(root, task["result_path"]),
            }
        )
    return {
        "root": str(root),
        "root_documents": {"missing": missing_docs, "complete": not missing_docs},
        "task_count": len(tasks),
        "tasks": task_checks,
        "blocking_tasks": [
            item["task_id"]
            for item in task_checks
            if item["status"] == "blocked"
        ],
    }


def choose_next(root: Path) -> dict:
    tasks = load_tasks(root)
    for task in tasks:
        if task["status"] in READY_STATES:
            contract = {
                "task_id": task["task_id"],
                "question_id": task["question_id"],
                "title": task["title"],
                "status": task["status"],
                "required_models": task["required_models"],
                "required_data": task["required_data"],
                "result_path": task["result_path"],
                "next_action": task["next_action"],
                "guard": (
                    "Before execute: verify model/data readiness, exact command, "
                    "server, environment, input hash, endpoints and QC."
                ),
            }
            return contract
    return {
        "task_id": None,
        "message": "No pending or partial task is eligible; inspect blockers or await plan amendment.",
    }


def hook(root: Path, event_type: str, task_id: str, **kwargs) -> None:
    hook_path = root / "scripts/hooks/project_event.py"
    if not hook_path.exists():
        raise RuntimeError(f"project event hook not found: {hook_path}")
    command = [sys.executable, "-B", str(hook_path), event_type, "--task-id", task_id]
    for key, value in kwargs.items():
        if value is None:
            continue
        flag = "--" + key.replace("_", "-")
        if isinstance(value, bool):
            if value:
                command.append(flag)
        else:
            command.extend([flag, str(value)])
    result = subprocess.run(command, cwd=root, check=False)
    if result.returncode:
        raise RuntimeError(f"event hook failed with exit code {result.returncode}")


def execute(args: argparse.Namespace, root: Path) -> int:
    if not args.authorize_execute:
        raise RuntimeError("execute requires --authorize-execute")
    if not args.command:
        raise RuntimeError("execute requires an explicit --command")
    if not args.host:
        raise RuntimeError("execute requires --host h100 or v100")
    if args.host.lower() not in {"h100", "v100"} and not args.lightweight:
        raise RuntimeError("heavy execution is restricted to H100/V100; use --lightweight only for local orchestration")
    task = next((row for row in load_tasks(root) if row["task_id"] == args.task_id), None)
    if task is None:
        raise RuntimeError(f"unknown task: {args.task_id}")
    if task["status"] in TERMINAL_STATES and not args.allow_rerun:
        raise RuntimeError(f"task {args.task_id} is {task['status']}; use --allow-rerun only for an approved rerun")

    job_id = f"supervisor-{os.getpid()}"
    hook(
        root,
        "run.started",
        args.task_id,
        host=args.host,
        job_id=job_id,
        message="Supervisor authorized explicit command",
    )
    started = time.time()
    completed = subprocess.run(args.command, shell=True, cwd=root, check=False)
    elapsed = round(time.time() - started, 3)
    if completed.returncode:
        hook(
            root,
            "run.failed",
            args.task_id,
            host=args.host,
            job_id=job_id,
            message=f"exit_code={completed.returncode}; elapsed_seconds={elapsed}",
            next_action="inspect evidence and decide retry or amendment",
        )
        return completed.returncode
    hook(
        root,
        "run.completed",
        args.task_id,
        host=args.host,
        job_id=job_id,
        path=task["result_path"],
        verified=True,
        message=f"exit_code=0; elapsed_seconds={elapsed}",
    )
    return 0


def review(args: argparse.Namespace, root: Path) -> int:
    task = next((row for row in load_tasks(root) if row["task_id"] == args.task_id), None)
    if task is None:
        raise RuntimeError(f"unknown task: {args.task_id}")
    checks = package_check(root, task["result_path"])
    payload = {"task_id": args.task_id, "result_path": task["result_path"], "package": checks}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not all(checks.values()):
        return 2
    if args.emit_qc:
        hook(
            root,
            "qc.passed",
            args.task_id,
            status=args.status,
            path=task["result_path"],
            verified=True,
            message="Supervisor package review passed",
        )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("inspect", "plan", "execute", "review"))
    parser.add_argument("--root", default=None)
    parser.add_argument("--task-id")
    parser.add_argument("--host")
    parser.add_argument("--command")
    parser.add_argument("--authorize-execute", action="store_true")
    parser.add_argument("--allow-rerun", action="store_true")
    parser.add_argument("--lightweight", action="store_true")
    parser.add_argument("--emit-qc", action="store_true")
    parser.add_argument("--status", default="complete")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = root_path(args.root)
    if args.mode == "inspect":
        print(json.dumps(inspect(root), ensure_ascii=False, indent=2))
        return 0
    if args.mode == "plan":
        print(json.dumps(choose_next(root), ensure_ascii=False, indent=2))
        return 0
    if args.mode == "execute":
        if not args.task_id:
            raise RuntimeError("execute requires --task-id")
        return execute(args, root)
    if not args.task_id:
        raise RuntimeError("review requires --task-id")
    return review(args, root)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
