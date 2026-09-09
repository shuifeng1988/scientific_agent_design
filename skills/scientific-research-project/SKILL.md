---
name: scientific-research-project
description: "Create and operate auditable scientific projects with five canonical documents, dependency/resource-aware continuous execution, bounded recovery, and literature-grounded result interpretation. Use when starting, resuming, auditing, or extending a multi-step computational research project."
---

# Scientific Research Project

Use this skill to turn a scientific project into a disk-backed, restartable research system. It manages project intent, evidence, execution state, and reflection; it does not replace domain-specific analysis skills or silently run expensive computation.

## Required operating contract

1. Read 00_PROJECT.md, 01_PLAN.md, 02_SOFTWARE.md, 03_DATA.md, and 04_STATUS.md before making a decision.
2. At project start or when scope is unclear, run intake: clarify the user goal, scientific decision, hypotheses, study population, eligible models/data, primary and secondary endpoints, exclusions, resources, constraints, deliverables, expected patterns, and stopping rules. Ask the user about high-impact gaps before freezing the plan.
3. Treat Qxx as a scientific question and Qxx.xx as its executable task. Every task must have one pre-registered result path in registry/tasks.tsv.
4. Use all eligible models and datasets specified by the task. A pilot subset is evidence for readiness, never a formal benchmark replacement.
5. Before execution, verify data version/hash, software/checkpoint/version, server/environment, command, resources, split, endpoint, QC, and failure policy. Heavy work must run on the execution backend declared by the project (local CPU/GPU, remote server or cluster, container, or online API); never assume a specific accelerator.
6. Record every download, software/checkpoint, run, QC, failure, and approved plan change with the project event hook.
7. Every result must compare preregistered expectations with observations and uncertainty, search supporting and conflicting literature, explain alternatives, and assess how the evidence changes each downstream task's scientific value. A strong unexpected result holds affected dependent branches for discussion; unrelated ready tasks continue. Add low-risk, high-value evidence tasks with explicit dependencies and provenance under the existing scope.
8. Do not call a process exit a scientific completion. A task is complete only when its result package has README, Word report, tables, figures, QC, reflection, and evidence hashes; exclusions remain in the audit denominator.
9. Never silently rewrite a frozen goal, endpoint, cohort, split, eligibility rule, or exclusion rule. Use a visible qc.failed or plan-amendment draft.
10. When continuous execution is authorized, keep the resident Supervisor service active across conversation turns. Generate an acyclic dependency table, dispatch every authorized ready task that fits current resources, reconcile completion, validate, interpret, update docs and dispatch again. Do not ask for repeated authorization already granted.
11. Every Agent step follows: preserve failure evidence → diagnose cause → targeted repair → minimal verification → resume the failed phase → QC → advance. Never blindly rerun a broken command or recompute successful phases. Unknown SSH status must not cause duplicate submission. Bound attempts, time and resources; scientific/design anomalies require discussion, not automatic alteration. Read references/failure_recovery.md for the mandatory recovery evidence and stopping rules.

12. With execution_policy=v2, use stable task/phase incident identities and default 3 repair-worker calls plus 3 verified retries per incident round; the initial execution and normal contract planning do not consume failure-recovery quotas. Track all AI calls as cost telemetry; stop repeated nonproductive planning after 2 proposals and report planning_stalled. Explicit user repair/continue instructions for named tasks trigger `intervene --node ID --reason REASON`, under the daemon lock after reconciling jobs; reset only those tasks. Status queries, service restarts and automated repairs do not reset budgets. Preserve cumulative attempts, job IDs and failure evidence. Do not impose a project-wide call quota in per-node mode or bypass scientific holds. Provider/account limits remain external.

13. Separate artifact readiness from scientific release: completion_policy=artifact permits only run → validate, requires run-bound hashes and a methods/provenance README, and must set scientific_result=false and finalizes_task=false. Downstream computation may consume verified artifacts immediately. Report nodes retain real literature interpretation, Word/tables/figures/reflection; scientific publication additionally waits for the event-hook acknowledgement. A failed report must not invalidate independent verified computation.
14. Compile the entire authorized model × stage matrix into stable independent nodes. Any automatic DAG expansion must match the operator-owned expansion_policy, inherit prerequisite and scope hashes, stay inside the registered result path, and pass cycle/duplicate checks. Keep the complete panel at the final barrier; do not silently omit a difficult model. Read references/execution_first_architecture.md.
15. Report project progression separately from daemon health: running, planning_or_repairing, waiting_resources, stalled, complete. A live daemon with no advancing work is not a running benchmark. Preserve durable event delivery; document outage holds scientific publication, not unrelated verified artifact computation.

## Modes

- intake: produce a structured clarification brief and identify high-impact unanswered questions.
- inspect: read-only inventory and consistency checks.
- plan: identify the next ready task and produce an execution contract only after intake is sufficient.
- daemon/tick: use scripts/supervisor_daemon.py to reconcile durable jobs and dispatch all ready nodes under reviewed contracts. Legacy execute is disabled because it lacked persistent monitoring and host enforcement.
- review: validate outputs, package completeness, and expected-versus-observed reflection.
- reflect: classify discrepancies and separate user-discussion items from safe supplementary evidence tasks.

Use scripts/supervisor_agent.py for these modes. Read references/intake_protocol.md for user-alignment questions, references/project_schema.md for document and event contracts, and references/reflection_protocol.md for result interpretation and supplementary experiments.

For continuous operation, dependencies, resource scheduling, recovery or worker integration, read references/continuous_execution.md and references/supervisor_protocol.md. The source-root INSTALL.md documents service installation. Register the resident service in ~/.codex/monitor/tasks.json and confirm a fresh snapshot; its project status table must expose every child job and blocker.

The user's existing scoped authorization covers routine planning, downloads, submissions and technical retries within that plan. It does not authorize changed scientific endpoints or unrelated actions. An interpretation worker must actually run literature search and reasoning; the daemon or Markdown keyword checks cannot substitute for them. State whether the worker is configured and functioning. Keep the five root documents and their Q/task result paths as the human entry points.
