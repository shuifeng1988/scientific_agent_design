# Scientific review, amendments and supplemental evidence (v0.8.0)

This protocol supplements the existing project/design/execution contracts. Five root documents, detailed plans, actual dialogue and approval, task/result correspondence, evidence, full methods, figures, tables, interpretation and same-source Markdown/Word remain required. It does not add root guidance files. Technical artifacts still do not need a formal Word report.

## Version-bound review

New proposals declare `review_policy: independent_review_v1` and a nonempty `author_invocation_id`. Report manifests also record the actual author invocation ID. Author and reviewer must use different real invocations; do not invent identifiers or transcripts to simulate independence. Existing frozen designs with no review policy remain legacy. Removing the policy from a current strict design is rejected. Upgrading a legacy baseline requires an approved amendment.

Design review covers question/method alignment, primary and contrary evidence, independent analysis units, controls/statistics, feasibility and task/output alignment. Result review covers methods, data/denominators, statistics/uncertainty, claim/evidence support, contrary explanations, figures/tables and downstream consequences. The exact criterion IDs are in `scripts/scientific_review.py:CRITERIA`.

Produce the exact review subject with:

```bash
python scripts/scientific_review.py subject --root PROJECT --stage design --proposal PROJECT/provenance/proposal.json
python scripts/scientific_review.py subject --root PROJECT --stage result --task-id Q01.01 --run-id ACTUAL_RUN_ID
```

Save the emitted subject JSON in the existing provenance/task evidence area. With authorization to invoke a separate reviewer, `review_worker.py --root PROJECT --subject SUBJECT_JSON --timeout 600` starts one **foreground** Codex CLI invocation with `--sandbox read-only`. The outer wrapper records request, process output, transcript and invocation receipts in `provenance/reviews/REVIEW_ID/`. It enforces a timeout and rechecks target/provider hashes after return. It does not run services, publish, approve science or automatically install a returned review at a gate. It does not provide a filesystem sandbox for arbitrary remote services or connectors. The actual Codex host must support/enforce its native sandbox.

The Claude reviewer definition exposes Read/Glob/Grep only; the outer host saves its return and invocation/transcript evidence. Other hosts can implement the same receipt contract. Their truthful invocation identity is the host/operator's responsibility; a JSON ID is not authentication or proof of independent reasoning.

Review JSON fields:

- `schema_version: 1`, `subject` (exact emitted object), `reviewer_invocation_id`.
- `invocation`: a project-relative receipt for JSON containing `invocation_id`, `role: reviewer`, `subject_sha256`, `provider`, `started_at`, `completed_at`, and a `transcript` receipt.
- `verdict`: adequate / revise / needs_user.
- `criteria`: all IDs for the stage, each with verdict, substantive rationale and actual evidence receipts. Cite relevant sections/rows in the rationale; file hashes alone are insufficient scientific explanations.
- `findings`: list of unique IDs, severity critical/major/minor, status open/resolved, rationale and evidence. A resolved finding additionally has `resolution: {rationale, evidence}`. A correction that changes reviewed targets needs a fresh subject and review.

Use `scientific_review.py check` with the same subject-generating arguments plus `--review REVIEW_JSON`. Only adequate overall/all criteria with no open major/critical findings satisfies acceptance. After review and actual user approval, freeze with `research_workflow.py freeze --root PROJECT --proposal PROPOSAL --approval APPROVAL --review REVIEW_JSON`. The default design review path is `provenance/design_review.json`.

For a result, integrate the reviewed JSON as the registered task's `_evidence/scientific_review.json`, retaining the referenced transcript/invocation. The final completion event checks it again. Missing/stale/unaccepted review or necessary supplemental evidence places the node in `reviewing`; it consumes no technical retry budget and releases no dependent scientific completion. The daemon rechecks it each tick without relaunching completed compute. Independent branches can continue. A correctly recorded review still cannot guarantee scientific truth.

## Approved plan amendment

Prepare actual replacement content and show its changes to the user. Reuse the project's amendment area. A proposal retains the normal five-document/task/appraisal fields, adds the strict review policy and actual author invocation, a new `version`, and:

```json
{"amendment":{"base_design_sha256":"ACTUAL_CURRENT_DESIGN_HASH","reason":"scientific reason","affected_task_ids":["Q01.03"],"new_dependencies":{"Q01.03":["EXISTING_NODE_ID"]}}}
```

The approval must cover exact proposal/appraisal hashes and point to the actual user decision; the independent design review covers the new proposal. Then `plan_amendment.py apply --root PROJECT --proposal PROPOSAL --approval APPROVAL --review REVIEW` performs the migration. It archives old design/documents/config/state, writes the new immutable baseline and task mapping, and records an idempotent approval event. It never modifies completed result packages or launches/restarts services.

This first implementation is conservative: preserve all existing task IDs and their identity/mapping fields; add a new task for replacement science. Completed/frozen tasks cannot be marked affected. With a supervisor configuration, require `paused: true`, no running/unknown worker or job, and no unfinished attempted job/review. Quiesce the daemon so its lock is free; do not kill or forget remote work to obtain that lock. Existing unattempted contracts are cleared for explicit replanning; their root scope gates and new tasks bind the new plan. Successfully completed reports keep their preserved historical plan version. Old model/data/other non-root gates are retained and may still need deliberate replanning.

A durable `provenance/amendment_transaction.json` permits `plan_amendment.py recover --root PROJECT`: prepared writes roll back; committed writes retry the event/receipt. Never edit registry hashes manually to hide a partial migration. Inspect recovered state before normal authorized operation resumes. A resume or installation update does not apply a scientific amendment.

## Required and optional supplementary analysis

Within the already approved scope, prepare a spec and run `supplementary_tasks.py --root PROJECT --spec SPEC_JSON` with the daemon lock free. The spec has `task_id`, a safe `id`, `necessity` (required/optional), `rationale`, `scope_justification`, `stopping_rule`, `analysis_label` (prespecified/exploratory_post_hoc), a `source` receipt in the parent result, current `01_PLAN.md` `scope` receipt, explicit `depends_on` node IDs and an optional executable `contract`. A missing contract leaves planning pending; registration does not execute it. Novel endpoints/cohorts or other scope changes still require a scientific amendment.

The tool registers an artifact node under the same task's `_evidence/supplements/ID`, with no new root/result convention. Add `{node_id, necessity, rationale, evidence: [actual receipts]}` to the reflection's `supplements` list. `decision: supplement` requires a nonempty registered list. Required supplements cannot depend on their own finalizer, must finish with verified artifacts, and their exact evidence must be incorporated into the revised reflection before a new review/publication. Optional registered exploration need not hold an otherwise valid conclusion. Explain denominators and multiplicity implications in the spec/reflection; text fields do not automatically establish sound statistics.

## Behavior evaluation and honest claims

`assets/evaluation/` contains six explicitly synthetic cases and separate human rubrics: ambiguous direction, contrary/closest evidence, analysis units/leakage, null findings, recovery/unknown jobs, and provider replacement. `scientific_evaluation.py export --case CASE_ID --destination NEW_DIRECTORY` exports only case input. Keep rubric files and reference answers out of the evaluated agent's accessible workspace; export alone is not a security boundary.

Run the actual configuration on that input and retain its actual response. A run JSON has project-relative `case`/`output` receipts, actual `author_invocation_id`, `configuration`, `comparison_context` with exactly model/tools/budget/environment/input_sha256, and `observed_metrics` with elapsed_seconds/input_tokens/output_tokens/cost (null for unavailable values). `score --root ROOT --run RUN_JSON` stays pending until independent human grading exists.

A human judgment binds the `run` manifest receipt and `output` receipt, declares `human_review: true`, actual `reviewer_id`, and all rubric `grades`, each containing score 0/1/2, rationale and response_locator. Use `score ... --judgment JUDGMENT_JSON`; incomplete/stale grades fail and critical criteria below 2 are not hidden by averages. `compare --a SCORE_A --b SCORE_B` requires identical case/model/tool/budget/environment and both graded responses. It reports observed quality and cost/time fields without imputing missing metrics. Human review declarations remain auditable records, not authenticated identities.

The packaged tests exercise evaluator mechanics with clearly artificial records. No real model comparison, scientific accuracy gain or token saving follows from those tests. Add domain-reviewed real tasks and repeated observations before claiming a benefit.
