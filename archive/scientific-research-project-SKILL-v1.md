---
name: scientific-research-project
description: "Create and operate auditable scientific projects with five canonical documents, Q/task plans, reproducible results, event hooks, and a guarded Supervisor Agent. Use when starting, resuming, auditing, or extending a multi-step computational research project."
---

# Scientific Research Project

Use this skill to turn a scientific project into a disk-backed, restartable research system. It is a project-management and evidence skill: it does not replace domain-specific analysis skills or silently run expensive computation.

## Required operating contract

1. Read the project root files 00_PROJECT.md, 01_PLAN.md, 02_SOFTWARE.md, 03_DATA.md, and 04_STATUS.md before making a decision.
2. Treat Qxx as a scientific question and Qxx.xx as its executable task. Every task must have one pre-registered result path in registry/tasks.tsv.
3. Use all eligible models and datasets specified by the task. A pilot subset is evidence for readiness, never a formal benchmark replacement.
4. Before execution, verify data version/hash, software/checkpoint/version, server/environment, command, resources, split, endpoint, QC, and failure policy. Heavy work belongs on the declared H100/V100 host.
5. Record every download, software/checkpoint, run, QC, failure, and approved plan change with scripts/project_event.py or the project hook adapter.
6. Do not call a process exit a scientific completion. A task is complete only when its result package has README, Word report, tables, figures, QC, and evidence hashes; exclusions remain in the audit denominator.
7. When evidence is insufficient, create a visible qc.failed or amendment draft. Never silently rewrite a frozen goal, endpoint, cohort, split, or exclusion rule.

## Modes

- inspect: read-only inventory and consistency checks.
- plan: identify the next ready task and produce an execution contract.
- execute: run only an explicitly supplied, approved command on its declared server; register start/progress/completion/failure events.
- review: validate outputs, generate tables/figures/reports, and decide complete/frozen/blocked.

Use scripts/supervisor_agent.py for these modes. Read references/project_schema.md for the document, task, result, and event contracts. Read references/supervisor_protocol.md when planning or reviewing a task.

The Supervisor is deliberately guarded: its default mode is read-only, it does not infer permission to download, submit jobs, or overwrite results, and it must surface blockers instead of inventing values.
