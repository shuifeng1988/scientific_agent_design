# Project schema

For new projects, [workflow_contract.md](workflow_contract.md) specifies the implemented plan_results_v1 gate, JSON records, same-source report generation and event-hook installation. The narrative requirements below remain scientific review criteria; a schema pass does not prove that the analysis or literature interpretation is correct.

## Canonical root

Every project instance exposes five human entry points:

- 00_PROJECT.md: goal, scientific questions, scope, hypotheses, deliverables.
- 01_PLAN.md: Q/task plan, eligible models, data, software, commands, gates.
- 02_SOFTWARE.md: model/software versions, environments, checkpoints, smoke.
- 03_DATA.md: source, version, download, path, hash, QC, split, leakage.
- 04_STATUS.md: generated status, failures, blockers, next action.

## Identifiers

00/01 must satisfy [research_depth.md](research_depth.md). A goal paragraph and Q/task inventory are navigation, not an adequate scientific design. Keep the sourced significance/gap argument in 00 and detailed purpose–input–method–output–evidence cards for every task and substep in 01. The source project_template documents are drafting aids; unresolved placeholders cannot be treated as a ready protocol.

- Q00, Q01: scientific question.
- Q01.01: executable task under a question.
- Q01.01.R001: one execution/run.
- registry/tasks.tsv: one row per task, with one result_path.
- registry/supervisor.json: dependency DAG, run/validate/interpret phase contracts, resource requests/limits, approved hashes and bounded retry policy. Child paths remain below the parent task's result_path. See continuous_execution.md.

Do not create a second stage/final/new-results numbering system.

## Result package

A completed task directory contains README.md, REPORT.docx, tables/, figures/, and _evidence/. Its README must state the question, plan version, data source/version/hash/call, software/version/environment/usage, actual command/host/resources/seed/run ID, QC/coverage/failures/exclusions, result tables/figures, conclusions, anomalies, limitations, and next action.

The central mapping is 00_PROJECT scientific question → 01_PLAN executable step → registry/tasks.tsv task_id/result_path → one canonical results package. Run IDs, model/seed children and retries stay inside that task path and feed its task-level report. Do not create a separate, unlinked results tree.

At each step, read the approved inputs/methods/commands and write their actual provenance with the outputs. As validated results arrive, update corresponding tables, figures and report drafts. At formal completion, README.md and REPORT.docx must agree on values, denominators, figures, conclusions and limitations. Cite raw-data paths/hashes rather than duplicating large data. Figures must trace to source tables and generation methods; literature interpretation must preserve support, conflict, alternatives and downstream implications.

Intermediate artifact nodes may release computation after their own hashed QC without a standalone Word report; they do not finalize the parent scientific analysis. The parent remains incomplete until its formal report package and event acceptance are finished. File presence alone is not a scientific validity check.

## Event contract

Use the project's registered event hook (this benchmark: scripts/hooks/project_event.py) to record immutable events in provenance/events.jsonl; discover its actual path rather than assuming a template location. Required event families are data.download.completed, data.standardization.completed, software.download.completed, software.smoke.passed, run.started, run.progress, run.completed, run.failed, qc.passed, qc.failed, and plan.amendment.approved.

Completion events require verification. qc.passed additionally requires the human result package. qc.failed creates a visible amendment draft without silently changing frozen scientific scope.

## State machine

draft -> approved -> ready -> running -> validating -> reviewing -> complete -> frozen

Failure paths are failed or blocked; an explicit exclusion is excluded. A process exit alone cannot advance a task to complete.
