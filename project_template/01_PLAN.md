# Research plan

_Every task belongs to one scientific question and has one predetermined result directory._

---

## 📋 Task table

| Task ID | Parent | Scientific purpose | Software IDs | Data IDs | Dependencies | Result path | Status |
|---|---|---|---|---|---|---|---|
| `Q01.01` | `Q01` | To be defined | `SW001` | `D001` | None | `results/Q01_question_slug/Q01.01_task_slug/` | `draft` |

## 🔗 Readiness rules

Create `registry/task_dependencies.tsv` with task_id, depends_on (semicolon-separated all-of predecessors), frozen_evidence, rationale. All root task IDs appear once. Create executable child/shard nodes in `registry/supervisor.json`, retaining the parent Q/task and canonical result path. Show the generated dependency/status table here.

Every executable node records run/validate/interpret commands, server/environment, immutable data/software/scientific contract hashes, CPU/RAM/GPU, timeout and bounded retry policy. Model/shard tasks may run independently when resources fit; the final result node waits for all required model outputs or reviewed exclusions.

Every failed step must preserve evidence, diagnose the cause, apply a targeted remedy,
pass a minimal verification, and resume only the failed phase before QC and progression.
Do not blindly resubmit, duplicate unknown remote jobs, or recompute verified prior steps.
Repair has priority and reserved budget inside the total cap; scientific anomalies require
discussion. Follow the scientific-research-project Skill's failure_recovery.md contract.

Continuous authorization covers automatic progression and routine technical recovery. Strong contradictions pause only the affected scientific branch. The resident service's empty queue must show a reason and trigger the configured bounded progress worker when contracts or technical repairs are missing.

A task cannot enter `ready` until data, software, method, outputs, QC, failure policy, and resources are complete.

## ✍️ Plan amendments

Hooks may propose amendments after failures, contradictions, or evidence gaps. Only approved amendments change the frozen plan; record reason, evidence, impact, approver, and diff.
