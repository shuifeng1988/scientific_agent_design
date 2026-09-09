# Implemented plan-to-results contract (v0.6.0)

Read this before using `workflow_policy=plan_results_v1`. This contract implements the README lifecycle; it is not a domain analysis engine, an authentication system, or a substitute for scientific review.

## 1. Intake, appraisal and approval

1. Discuss the user's purpose, hypotheses, success criteria, scope and constraints.
2. Prepare a UTF-8 JSON file with nonempty `project` and `plan` Markdown strings. Run `research_workflow.py draft --root PROJECT --spec FILE`. Only 00_PROJECT.md and 01_PLAN.md are established, with an intake receipt. Existing root documents are never overwritten.
3. Conduct actual searches and appraise the question. Preserve readable appraisal/method options and actual search-output evidence in project provenance.
4. Prepare the proposed five formal documents and complete task list; show the user the actual content, important choices, uncertainties and costs.
5. Capture the real user decision separately, bound to the exact proposal and appraisal. Never let an AI worker fabricate approval, transcribe consent not given, or edit the evidence to fit a new proposal.
6. Run `research_workflow.py freeze --root PROJECT --proposal FILE --approval FILE` after approval. Missing, stale or inconsistent evidence blocks freezing. The command writes five baseline documents, task registry, design receipts, the event hook and appraisal/discussion journal entries. The events record already-completed research/discussion; the command does not perform them.

All receipt objects have `{"path": "project-relative/file", "sha256": "actual SHA-256"}`. Receipt paths resolve inside the project; traversal and external symlinks are rejected. Large remote data need not be duplicated: reference a locally hashed provenance manifest containing the actual remote location, source/version, transfer/access command, and verified remote checksum. This validates the manifest, not remote bytes; the data worker must perform and record remote verification.

### Appraisal JSON

Required nonempty strings: `question`, `searched_at`, `significance`, `novelty`, `feasibility`, `worth_doing`, `information_gain`, `limitations`, `recommendation`.

- `searches`: at least two entries with distinct `route`, each containing `query`, `date`, `recent_window`, `selection_rules`, and an `evidence` receipt. Record actual search outputs, dates and recent-work criteria; do not merely rename one route.
- `sources`: entries containing nonempty `url`, `title`, `year` (string), `evidence_direction`, `relevance`. Record positive, negative, null or conflicting evidence honestly. URLs must use HTTP(S).
- `methods`: nonempty `conventional`, `current_reproducible`, `frontier` comparisons. Explain unavailability instead of inventing an applicable frontier method.

The gate checks these records and hashes. It cannot verify that two records represent genuinely independent searches, that citations support a claim, or that a project is worth doing. Those remain Agent/reviewer responsibilities.

### Proposal JSON

- `version`: nonempty approved plan version.
- `documents`: exactly five keys, 00_PROJECT.md through 04_STATUS.md, containing proposed Markdown.
- `appraisal`: receipt for the appraisal JSON.
- `tasks`: complete list, each with string fields `task_id`, `question_id`, `title`, `result_path`, `required_models`, `required_data`. Use explicit not-applicable explanations when a study has no models.
- IDs such as Q01.01 belong to Q01. Every question appears in 00; task ID and path appear in 01. Paths are unique, nonnested, inside results. Operational model/run children remain under these canonical task paths.
- Put actual scientific methods, expected outcomes, statistics, exclusions, dependencies, software/data and stopping rules in the proposed plan. A path/keyword match alone does not validate methodological adequacy.

### Approval JSON

`decision: "approved"`, `proposal_sha256`, `appraisal_sha256`, nonempty `actor`, `recorded_at`, `message`, and an `evidence` receipt referencing the actual user-decision record. The operator records consent; this is not cryptographic identity authentication. A changed proposal/appraisal requires a new decision bound to the new hashes.

## 2. Baseline, DAG and host configuration

`registry/design.json` binds the proposal, appraisal, approval, immutable baseline copies and task manifest. `research_workflow.py check --root PROJECT` verifies the binding, five root documents, current 00/01 hashes, and task registry correspondence.

Enable both `execution_policy: "v2"` and `workflow_policy: "plan_results_v1"` in registry/supervisor.json. Before new dispatch the daemon verifies the baseline. A missing/deleted design file cannot downgrade a strict configuration. Existing running or unknown jobs continue to be reconciled without losing their IDs or resource reservations.

For new projects, `bootstrap_supervisor.py --root PROJECT --dependencies FILE --hosts FILE` requires reviewed inputs:

- Dependency TSV: `task_id\tdepends_on\tfrozen_evidence`; all tasks exactly once, semicolon-separated predecessor IDs, empty optional frozen evidence. Importing prior results needs a separate evidence review, not an empty success marker.
- Hosts JSON maps host aliases to `driver` argv and `limits`; use the installed systemd_driver.py path, with `--host local` or `--host user@server`. No server address is inferred. Driver contracts are detailed in continuous_execution.md.
- The bootstrap writes a skeleton with missing execution contracts. Missing commands remain blocked until actual, reviewed contracts exist. It never invents a runnable research method.
- Register all approved eligible models/data in the DAG and enforce the full-panel final barrier. Source gates should hash the design/plan, input manifests, software/checkpoints and scripts. Resource snapshots and reservations still govern dispatch.
- The current scheduler permits explicitly lightweight local phases; use validated SSH hosts for heavy jobs. No cloud/API/Slurm/container adapter is added.

Runtime progress is in 04_STATUS.md, registry/task_dependencies.tsv and provenance/supervisor/status.md. It must not mutate the frozen 00_PROJECT.md/01_PLAN.md hashes. Link those state files from the approved plan.

## 3. Actual analysis and same-source reports

The domain worker performs the computation and creates real tables/figures. It then prepares `RESULT/_evidence/report.json`:

- Identity: `task_id`, `plan_version`, `run_id` (the assigned SCI_RUN_ID), `language` (zh or en), `title`, `host`, `environment`, `command` (actual argv list).
- `software`: entries with `name`, `version`, `usage`; include source, checkpoint, environment, resources and seeds in methods/provenance as applicable.
- `inputs`: project-relative receipts, each with `source`, `version`, `access`. See remote-manifest boundary above.
- `sections`: nonempty `data`, `methods`, `results`, `conclusions`, `interpretation`, `limitations`, `qc`, `next_step`. Include denominators, failures, exclusions, effect sizes/uncertainty, expectations and interpretations as scientifically applicable.
- `tables`: result-relative receipts plus `caption`. CSV/TSV, rectangular, header and at least one data row, at most 1000 data rows per report summary. Keep larger raw tables separately referenced and hashed.
- `figures`: result-relative PNG/JPEG receipts, `caption`, `method`, `source_tables` listing at least one of the included tables. Keep the plotting script in run evidence. Lineage does not prove that a plot encodes the values faithfully; review the plotted axes and values.

Run `research_workflow.py render --root PROJECT --task-id Q01.01 --manifest FILE`. It generates canonical README.md, REPORT.docx and _evidence/report_receipt.json from the same supplied sections/tables/figures. It does not use an LLM to invent conclusions. The report environment needs requirements-report.txt (python-docx); Pillow is needed for the test fixture only.

Keep iterative drafts separately until final analysis content is ready. The final renderer refuses silent overwrite if a receipt exists. Revisions require preserving the previous run/receipt and deliberate reviewed replacement at the same canonical task path; no automated revision/migration command is provided. Never delete a failed receipt simply to make a test pass.

## 4. Validation, reflection and publication

Execution uses existing run → validate → interpret contracts. Validation can first establish technical QC; interpretation must conduct actual literature work and write _evidence/reflection.json before publication. Refresh final QC after interpretation changes evidence.

Reflection schema remains in continuous_execution.md: same run ID; expected/observed, uncertainty, reasoning, alternatives, evidence strength, limitations, downstream impact; decision continue/supplement/needs_user; actual literature query/date/status/source records. A no-results statement is not permission to skip searching. Scientific discrepancies require discussion; safe in-scope additions need explicit DAG/evidence mapping. Scope amendments need reviewed migration.

Final _evidence/qc.json must contain `run_id`, `passed: true` and receipts for all final report files, tables, figures, report.json, report_receipt.json and reflection.json. Paths in this QC are result-relative.

`research_workflow.py validate-package --root PROJECT --task-id ID --run-id RUN` validates:
- approved plan/version, canonical task path and run identity;
- input and report evidence hashes;
- required section contents in both Markdown and Word;
- Word tables and Markdown rows against actual source-table contents;
- Word-embedded image bytes and Markdown figure references;
- complete run-bound QC coverage.

The daemon's scientific review additionally checks reflection. A needs_user decision prevents publication/affected dependents. Only the accepted qc.passed event may complete a formal task. Technical artifact nodes remain non-scientific, non-finalizing, with hashed technical QC; they can release computation without pretending the full task report is complete.

## 5. Event-triggered updates and failure handling

Freeze installs scripts/hooks/project_event.py as a thin wrapper pointing to the actual source/installed implementation. Moving that implementation requires a reviewed wrapper update; there is no hidden second source tree.

The portable hook records validated events, then rebuilds managed sections of 02_SOFTWARE.md, 03_DATA.md, 04_STATUS.md, registry/tasks.tsv and results/README.md. Text outside managed sections is preserved. Exact event replay is idempotent; conflicting reuse of a Supervisor event ID fails. If a write is interrupted after event persistence, replay repairs document generation.

Data/software events require hashed verified evidence. Record sources, versions, commands and actual checks in the linked evidence; a table row alone is not full deployment documentation. Run completion is not scientific completion. qc.failed marks the task blocked and creates a provenance/amendment_drafts record without changing the approved plan. plan.amendment.approved records a hashed decision; it does not implement or silently replace the design.

Every failure follows failure_recovery.md: preserve evidence, diagnose, targeted remedy, passing minimal test, retry failed phase within task-local budgets, QC and progression. Unknown jobs retain their identity/lease. A failed report must not block unrelated verified computation.

## 6. Adoption and acceptance boundaries

New projects use the strict workflow. Legacy projects retain their existing behavior until reviewed migration; draft/freeze refuse an existing registry or hook. Back up and reconcile baseline/task IDs/evidence/running jobs, obtain any needed approval, and review hook/config changes. There is deliberately no force-overwrite migration command. Updating a Skill installation alone does not migrate a live project.

Acceptance commands from the source scripts directory:

```bash
python3 -m pip install -r requirements-report.txt
python3 -m pip install Pillow==12.0.0
python3 -B -m unittest discover -p 'test_*.py' -v
```

The tested interpreter is Python 3.13. Tests include draft/freeze, stale approvals, plan drift, wrong paths/runs, missing or tampered Word/tables, event replay, scientific holds, recovery/regression, and a real small subprocess dependency chain with scheduler reconstruction. Fixture data, searches and user decisions are explicitly SYNTHETIC and are never project research evidence. Driver/resource and monitoring interfaces are mocked in that chain; it does not certify actual systemd/SSH hardware, online Codex/Claude, or an entire scientific study. Real deployments need native driver/monitor checks and domain-specific acceptance separately.
