# Supervisor Agent protocol

The Supervisor is a guarded control loop, not an unrestricted shell agent.

## Loop

Entry condition: for a new/unclear study, perform [conversational intake](intake_protocol.md) first. Ask 1–3 questions and return control to the user, rather than running this loop in the same turn. Continue only after direction confirmation, appraisal, and final design approval as applicable. In a noninteractive worker, expose needs_user to the outer conversation. Existing approved tasks do not repeat intake, and a scoped hold must not stop unrelated authorized branches.

1. Inspect the five root files and registry/tasks.tsv.
2. Select the next task only if its dependencies are satisfied and its data/software gates are ready.
3. Produce an execution contract containing question, task ID, eligible models, data IDs, software/environment, host, command, resources, seed, endpoints, QC, failure strategy, and result path.
4. Reuse standing user authorization for in-scope commands and bounded technical retries; obtain new direction only for scientific changes or actions outside that authority.
5. Run only the supplied approved command on an authorized configured host, respecting project compute rules and the runtime's actual resource limitations.
6. Emit run.started, periodic run.progress, and run.completed/run.failed events.
7. Validate outputs and result package; emit qc.passed or qc.failed.
8. Reflect on expected versus observed results. Propose an amendment for evidence gaps; never overwrite a frozen conclusion.
9. Update the five human documents and immediately rescan all dependency-ready tasks. Dispatch every resource-fitting task; keep the daemon resident while waiting. Do not require a new user message for each next task.

At every step, failure invokes [failure_recovery.md](failure_recovery.md): preserve
evidence, diagnose, apply a cause-specific remedy, verify it, then resume only the
failed phase. Prioritize repair over new planning, use independent task/phase incident budgets (3 repair calls and 3 retries under execution_policy=v2), reset only explicitly human-intervened
tasks via `intervene`, retain lifetime history, and preserve successful outputs. Unknown job status and scientific QC
anomalies must not trigger blind retries or changed scientific conclusions.

Artifact nodes end at verified run → validate and release computation; report/scientific nodes also require interpretation and publication QC. Never force literature search on a purely technical artifact prerequisite. See [execution-first architecture](execution_first_architecture.md).

## Selection rules

Before final-plan approval, read research_depth.md and conduct its substantive review against the actual 00/01, appraisal and source evidence. Return specific section/task defects, not a blanket approval based on files being present. During execution, the requested node must have an identifiable purpose, inputs, method, output schema and evidence use in its approved parent task. Missing scientifically consequential choices become needs_user; missing routine implementation becomes a scoped preparation task. This is a worker/reviewer obligation, not a claim that the deterministic scheduler can evaluate scientific significance.

- Scan in plan order but allow every independent ready task that fits resources; a blocked early task must not starve another branch.
- Include every eligible model and dataset in the task contract.
- A pilot can open a readiness gate but cannot close a formal benchmark.
- Keep full audit denominators and explicit exclusions.
- Do not hardcode personal GPU servers. Declare reviewed host/driver/resource settings. The current local scheduler permits explicitly lightweight work; use validated SSH hosts for heavy jobs. No new backend support is implied.
- If root documents disagree with registry or evidence, report a blocker and stop before launching computation.

## Modes

For plan_results_v1, verify the approved design before new dispatch; reconcile already-running jobs even when the design gate fails. Keep runtime status in 04_STATUS.md and registry/task_dependencies.tsv, not inside the hashed 00_PROJECT.md/01_PLAN.md baseline. Require same-source package validation before publication; preserve artifact-first release for technical child nodes. See [workflow_contract.md](workflow_contract.md). Existing legacy configurations are not silently migrated.

inspect and plan are read-only. Durable daemon/tick replaces legacy execute. review is an inventory-only check; completion requires run-bound QC, actual literature/interpretation evidence and the project hook. See continuous_execution.md for driver, dependency and state contracts.
