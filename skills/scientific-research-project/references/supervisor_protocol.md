# Supervisor Agent protocol

The Supervisor is a guarded control loop, not an unrestricted shell agent.

## Loop

1. Inspect the five root files and registry/tasks.tsv.
2. Select the next task only if its dependencies are satisfied and its data/software gates are ready.
3. Produce an execution contract containing question, task ID, eligible models, data IDs, software/environment, host, command, resources, seed, endpoints, QC, failure strategy, and result path.
4. Reuse standing user authorization for in-scope commands and bounded technical retries; obtain new direction only for scientific changes or actions outside that authority.
5. Run only the supplied approved command on the declared remote host for heavy work.
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

- Scan in plan order but allow every independent ready task that fits resources; a blocked early task must not starve another branch.
- Include every eligible model and dataset in the task contract.
- A pilot can open a readiness gate but cannot close a formal benchmark.
- Keep full audit denominators and explicit exclusions.
- Heavy computation belongs on H100/V100; local work is orchestration, hashing, aggregation, and report generation.
- If root documents disagree with registry or evidence, report a blocker and stop before launching computation.

## Modes

inspect and plan are read-only. Durable daemon/tick replaces legacy execute. review is an inventory-only check; completion requires run-bound QC, actual literature/interpretation evidence and the project hook. See continuous_execution.md for driver, dependency and state contracts.
