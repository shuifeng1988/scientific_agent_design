#!/usr/bin/env python3
"""Guarded Supervisor Agent with intake, planning, execution, review, and reflection."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT_DOCS = ("00_PROJECT.md", "01_PLAN.md", "02_SOFTWARE.md", "03_DATA.md", "04_STATUS.md")
READY_STATES = {"pending", "ready", "partial"}
TERMINAL_STATES = {"complete", "frozen", "excluded"}


def root_path(value: str | None) -> Path:
    return Path(value).resolve() if value else Path.cwd().resolve()


def load_tasks(root: Path) -> list[dict[str, str]]:
    path = root / "registry/tasks.tsv"
    if not path.exists():
        raise RuntimeError(f"missing registry: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    fields = lines[0].split("\t")
    return [dict(zip(fields, line.split("\t"))) for line in lines[1:] if line.strip()]


def package_check(root: Path, result_path: str) -> dict:
    directory = root / result_path
    return {
        "directory": directory.is_dir(),
        "README.md": (directory / "README.md").is_file(),
        "REPORT.docx": (directory / "REPORT.docx").is_file(),
        "tables": (directory / "tables").is_dir()
        and any(p.is_file() for p in (directory / "tables").iterdir()),
        "figures": (directory / "figures").is_dir()
        and any(p.is_file() for p in (directory / "figures").iterdir()),
        "_evidence": (directory / "_evidence").is_dir(),
    }


def inspect(root: Path) -> dict:
    tasks = load_tasks(root)
    return {
        "root": str(root),
        "root_documents": {
            "missing": [name for name in ROOT_DOCS if not (root / name).is_file()]
        },
        "task_count": len(tasks),
        "tasks": [
            {
                "task_id": row["task_id"],
                "question_id": row["question_id"],
                "status": row["status"],
                "result_path": row["result_path"],
                "package": package_check(root, row["result_path"]),
            }
            for row in tasks
        ],
    }


def intake(root: Path) -> dict:
    project = (root / "00_PROJECT.md").read_text(encoding="utf-8") if (root / "00_PROJECT.md").exists() else ""
    plan = (root / "01_PLAN.md").read_text(encoding="utf-8") if (root / "01_PLAN.md").exists() else ""
    combined = (project + "\n" + plan).lower()
    signals = {
        "goal": ("项目目标" in combined or "研究目标" in combined or "objective" in combined),
        "scientific_questions": ("科学问题" in combined or "scientific question" in combined),
        "scope": ("范围" in combined or "scope" in combined),
        "endpoints": ("终点" in combined or "指标" in combined or "metric" in combined),
        "eligibility": ("eligible" in combined or "纳入" in combined or "排除" in combined),
        "deliverables": ("交付" in combined or "deliverable" in combined),
        "hypotheses": ("假设" in combined or "hypothes" in combined),
        "stopping_rules": ("停止" in combined or "stopping" in combined),
    }
    high_impact_questions = []
    if not signals["goal"]:
        high_impact_questions.append("项目最终要支持什么科学或实际决策？")
    if not signals["scientific_questions"]:
        high_impact_questions.append("需要回答哪些可证伪的科学问题？")
    if not signals["endpoints"]:
        high_impact_questions.append("主要终点、次要终点和不能合并的指标是什么？")
    if not signals["eligibility"]:
        high_impact_questions.append("哪些模型/数据必须全部参加，哪些可以排除，排除分母如何保留？")
    if not signals["hypotheses"]:
        high_impact_questions.append("每个问题的预期方向、零结果和竞争解释是什么？")
    if not signals["stopping_rules"]:
        high_impact_questions.append("什么情况应暂停并与你讨论，什么低成本补充实验可自动加入？")
    frozen = "PLAN-v" in plan and "Q00.01" in plan and "frozen" in combined
    return {
        "project": str(root),
        "interpretation_ready": not high_impact_questions or frozen,
        "design_already_frozen": frozen,
        "signals": signals,
        "high_impact_questions": [] if frozen else high_impact_questions,
        "confirmation_message": (
            "计划已有冻结记录；仍应在每个新科学问题开始前复核目标、终点和预期。"
            if frozen
            else "请先回答 high_impact_questions，再冻结 01_PLAN.md。"
        ),
    }


def choose_next(root: Path) -> dict:
    if (root / "registry/supervisor.json").exists():
        from supervisor_daemon import load_config
        config = load_config(root)
        state_path = root / "provenance/supervisor/state.json"
        state = json.loads(state_path.read_text()).get("nodes", {}) if state_path.exists() else {}
        return {"mode": "dependency_dag", "nodes": [
            {"id": n["id"], "depends_on": n["depends_on"],
             "contract_configured": bool(n.get("contract")), "state": state.get(n["id"], {})}
            for n in config["nodes"]], "note": "daemon dispatches all eligible resource-fitting nodes"}
    gate = intake(root)
    if not gate["interpretation_ready"]:
        return {"needs_user_intake": True, "intake": gate}
    for row in load_tasks(root):
        if row["status"] in READY_STATES:
            return {
                "needs_user_intake": False,
                "task_id": row["task_id"],
                "question_id": row["question_id"],
                "title": row["title"],
                "status": row["status"],
                "required_models": row["required_models"],
                "required_data": row["required_data"],
                "result_path": row["result_path"],
                "next_action": row["next_action"],
                "guard": "Verify all inputs, environments, commands, endpoints, QC, and failure policy before execute.",
            }
    return {"task_id": None, "message": "No ready task; inspect blockers or await plan amendment."}


def reflection(root: Path, task_id: str) -> dict:
    row = next((item for item in load_tasks(root) if item["task_id"] == task_id), None)
    if row is None:
        raise RuntimeError(f"unknown task: {task_id}")
    result_dir = root / row["result_path"]
    readme_path = result_dir / "README.md"
    text = readme_path.read_text(encoding="utf-8").lower() if readme_path.exists() else ""
    required = {
        "expected": ("预期" in text or "expected" in text),
        "observed": ("观察" in text or "observed" in text or "结果" in text),
        "anomaly": ("异常" in text or "anomal" in text),
        "alternative_explanations": ("替代解释" in text or "竞争解释" in text or "competing" in text),
        "evidence_strength": ("证据强度" in text or "evidence strength" in text),
        "limitations": ("限制" in text or "外推" in text or "limitation" in text),
        "next_action": ("下一步" in text or "next" in text),
    }
    missing = [name for name, present in required.items() if not present]
    discussion_triggers = []
    for word in ("unexpected", "反常", "不符合预期", "leakage", "不可信"):
        if word in text:
            discussion_triggers.append(word)
    suggestions = [
        "seed sensitivity or paired bootstrap",
        "missingness/failure mechanism audit",
        "calibration or negative-control check",
        "matched baseline or leakage audit",
    ]
    return {
        "task_id": task_id,
        "package": package_check(root, row["result_path"]),
        "reflection_sections": required,
        "missing_reflection_sections": missing,
        "user_discussion_triggers": discussion_triggers,
        "safe_supplementary_candidates": suggestions,
        "decision": (
            "ask_user_before_scope_change"
            if discussion_triggers
            else ("add_or_plan_supplementary_evidence" if missing else "ready_for_evidence_review")
        ),
    }


def hook(root: Path, event_type: str, task_id: str, **kwargs) -> None:
    path = root / "scripts/hooks/project_event.py"
    if not path.exists():
        raise RuntimeError(f"project event hook not found: {path}")
    command = [sys.executable, "-B", str(path), event_type, "--task-id", task_id]
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
        raise RuntimeError(f"event hook failed: exit {result.returncode}")


def execute(args: argparse.Namespace, root: Path) -> int:
    raise RuntimeError("Use supervisor_daemon.py with a reviewed DAG contract: legacy execute lacked persistent monitoring, remote host enforcement and output QC. See references/continuous_execution.md")


def review(root: Path, task_id: str, emit_qc: bool, status: str) -> int:
    row = next((item for item in load_tasks(root) if item["task_id"] == task_id), None)
    if row is None:
        raise RuntimeError(f"unknown task: {task_id}")
    payload = {"task_id": task_id, "package": package_check(root, row["result_path"]), "reflection": reflection(root, task_id)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not all(payload["package"].values()) or payload["reflection"]["missing_reflection_sections"]:
        return 2
    if emit_qc:
        raise RuntimeError("Automatic completion requires run-bound QC hashes and structured literature/reflection evidence; keyword/package presence is only an inventory check")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("intake", "inspect", "plan", "execute", "review", "reflect"))
    parser.add_argument("--root")
    parser.add_argument("--task-id")
    parser.add_argument("--host", default="")
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
    if args.mode == "intake":
        print(json.dumps(intake(root), ensure_ascii=False, indent=2))
        return 0
    if args.mode == "inspect":
        print(json.dumps(inspect(root), ensure_ascii=False, indent=2))
        return 0
    if args.mode == "plan":
        print(json.dumps(choose_next(root), ensure_ascii=False, indent=2))
        return 0
    if not args.task_id:
        raise RuntimeError(f"{args.mode} requires --task-id")
    if args.mode == "reflect":
        print(json.dumps(reflection(root, args.task_id), ensure_ascii=False, indent=2))
        return 0
    if args.mode == "review":
        return review(root, args.task_id, args.emit_qc, args.status)
    return execute(args, root)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
