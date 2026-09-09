# Project schema

## Canonical root

Every project instance exposes five human entry points:

- 00_PROJECT.md: goal, scientific questions, scope, hypotheses, deliverables.
- 01_PLAN.md: Q/task plan, eligible models, data, software, commands, gates.
- 02_SOFTWARE.md: model/software versions, environments, checkpoints, smoke.
- 03_DATA.md: source, version, download, path, hash, QC, split, leakage.
- 04_STATUS.md: generated status, failures, blockers, next action.

## Identifiers

- Q00, Q01: scientific question.
- Q01.01: executable task under a question.
- Q01.01.R001: one execution/run.
- registry/tasks.tsv: one row per task, with one result_path.
- registry/supervisor.json: dependency DAG, run/validate/interpret phase contracts, resource requests/limits, approved hashes and bounded retry policy. Child paths remain below the parent task's result_path. See continuous_execution.md.

Do not create a second stage/final/new-results numbering system.

## Result package

A completed task directory contains README.md, REPORT.docx, tables/, figures/, and _evidence/. Its README must state the question, plan version, data source/version/hash/call, software/version/environment/usage, actual command/host/resources/seed/run ID, QC/coverage/failures/exclusions, result tables/figures, conclusions, anomalies, limitations, and next action.

## Event contract

Use the project's registered event hook (this benchmark: scripts/hooks/project_event.py) to record immutable events in provenance/events.jsonl; discover its actual path rather than assuming a template location. Required event families are data.download.completed, data.standardization.completed, software.download.completed, software.smoke.passed, run.started, run.progress, run.completed, run.failed, qc.passed, qc.failed, and plan.amendment.approved.

Completion events require verification. qc.passed additionally requires the human result package. qc.failed creates a visible amendment draft without silently changing frozen scientific scope.

## State machine

draft -> approved -> ready -> running -> validating -> reviewing -> complete -> frozen

Failure paths are failed or blocked; an explicit exclusion is excluded. A process exit alone cannot advance a task to complete.
