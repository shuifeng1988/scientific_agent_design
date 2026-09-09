# Continuous execution contract (v0.5)

## What persists

The Python daemon is a lightweight orchestrator. The research worker is an explicitly configured Codex/Claude/API program or domain script. The daemon cannot conduct literature searches or scientific reasoning on its own. Give the `interpret` phase a real research-worker command; absent commands or credentials remain visible blockers. Do not describe a single `inspect` invocation as an autonomous agent.

Use `scripts/supervisor_daemon.py daemon --root PROJECT --interval 30`. Run it as a systemd user service with `Restart=on-failure`. Completed jobs are reconciled on the next scan (default 30 s), and all independent eligible nodes are dispatched. Resource waits do not end the daemon. Artifact dependencies are satisfied after run-bound hashed validation; scientific/report dependencies require actual interpretation and final publication acknowledgement. Lightweight planner or repair workers can be ordinary DAG nodes; every node must have its own registered parent Q/task and result path.

## Files and dependencies

- `registry/supervisor.json`: DAG, approved execution contracts, host limits; version-controlled project input.
- `provenance/supervisor/state.json`: durable attempts, phase, deterministic scheduler IDs, reservations, heartbeat and pending hook outbox.
- `provenance/supervisor/status.md`: dependency/status table, also rendered into 01_PLAN.md and 04_STATUS.md.
- `provenance/supervisor/events.jsonl`: local event history after successful project-hook delivery.
- `provenance/supervisor/PAUSE`: pause new submissions; reconcile existing work and preserve reservations.

Each node has `id`, `task_id`, `depends_on` (all-of edges), `result_path`, `scientific_result`, `finalizes_task`, `contract`, and `approved_contract_sha256`. A preparatory node lives below its registered task's result directory. Do not create circular parent/child readiness dependencies. Missing dependencies, duplicate IDs/paths and cycles fail configuration validation. An excluded task does not silently satisfy a dependency. Granular model/shard nodes allow independent completion and retries; a final all-panel QC node must depend on every required model/shard or explicit reviewed exclusion record.

`approved_contract_sha256` is the SHA-256 of sorted-key JSON serialization of `contract` (Python json defaults). It records the agent's concrete contract under the user's standing scope authorization; do not ask again for every already-approved implementation step. Scientific scope changes still require the plan amendment process. Never auto-approve arbitrary downloaded commands.

## Contract schema

```json
{
  "execution_policy": "v2",
  "paused": false,
  "hosts": {
    "H100": {
      "driver": ["python3", "/absolute/source/scripts/systemd_driver.py", "--host", "user@server"],
      "limits": {"max_jobs": 2, "cpus": 16, "memory_gb": 64, "max_gpu_utilization": 10}
    }
  },
  "nodes": [{
    "id": "Q01.02.materialize", "task_id": "Q01.02", "depends_on": [],
    "result_path": "results/Q01_question/Q01.02_task/_evidence/materialize",
    "scientific_result": false, "finalizes_task": false,
    "contract": null
  }]
}
```

An executable contract contains `gates: [{path, sha256}]`, `max_attempts` (default 3), and phase specs `run`, `validate`, plus `interpret` for report/scientific nodes. Artifact nodes explicitly set `completion_policy: artifact`, `scientific_result: false`, `finalizes_task: false`; they cannot publish a scientific conclusion. Each phase has `host`, `cwd` (on that host), `argv` (list, no implicit shell), `env`, `timeout_seconds`, and `resources: {cpus, memory_gb, gpus, gpu_memory_gb}`. Local phases additionally declare `lightweight: true`. Gate files must cover the scientific contract, model/data manifest, source/checkpoint versions and all phase scripts. Gates are checked at submission. A changed hash blocks new work.

## Durable driver protocol

The daemon invokes `driver argv + action`, feeding one JSON object on stdin and expecting exactly one JSON object on stdout. Each call times out after 20 s. This timeout concerns the control connection, not the scientific job.

| Action | Request | Response |
|---|---|---|
| resources | `{}` | `timestamp, free_cpus, free_memory_gb, gpus:[{id,free_gb,utilization}]` |
| launch | `job_id, run_id, spec, gpu_ids, root` | `job_id` (idempotent on supplied ID) |
| status | `job_id, run_id` | `state: queued/running/succeeded/failed/not_found/unknown`, optional `progress`, `reason`, `retryable` |

Bundled systemd driver supports local or SSH user services. It requires systemd user manager on the compute server. Slurm/tmux or another scheduler needs a conforming adapter; do not falsely claim native support. Credentials use existing SSH auth, with host-key checking intact. Resource probes include CPU load, available RAM, per-GPU free memory and utilization. The daemon enforces concurrent reservations and exclusive GPU IDs; a zero utilization reading alone is insufficient. Reservations coordinate one project daemon; other schedulers can still race, so use a cluster scheduler or dedicated resource partition where global exclusivity is required.

A running or unknown-state planner consumes one local job slot plus its reserved CPU/RAM. If the configured local limits permit a second lightweight job, transport/QC can proceed concurrently; this does not permit heavy local analysis. With max_jobs=1 it still waits. Set limits explicitly instead of ignoring the planner's resource usage.

## Recovery, progression and boundaries

Optional `progress_worker` (INSTALL.md) runs a bounded, project-scoped Codex call for a dependency-ready node with a missing contract or a confirmed terminal job failure with remaining repair budget. It uses isolated request/proposal directories, independent task/phase failure-repair limits (default 3 calls plus 3 verified retries in v2), timeout and failure backoff. The daemon adopts requested contracts or a complete, explicitly preauthorized model/stage expansion (see execution_first_architecture.md); technical repairs save the previous attempt and cannot increase the retry budget. Scientific QC anomalies and unknown job states are not eligible for automatic contract replacement. Scientific scope remains fixed; approved operational expansion must inherit the scope gates and pass full DAG validation. LLM calls consume the configured account quota; authentication failure is visible.

1. Save deterministic run/job ID and reservation before submit. On restart reconcile existing IDs; never create another job after an uncertain SSH result. Unknown jobs keep their leases and block only their affected branch.
2. Every confirmed terminal failure first creates a run/job/phase-bound diagnosis record, including available bounded logs. All failure categories require a cause-specific remedy and a passing minimal validation before replay; an infrastructure retryable flag alone is insufficient. See [failure_recovery.md](failure_recovery.md).
3. The repair worker returns a machine-checked recovery record and fresh tested code hashes. Resume only the failed phase; verify reused outputs and preserve prior phase specs. Later-phase repair retains SCI_RUN_ID but increments SCI_ATTEMPT and assigns a new SCI_JOB_ID. Exhaustion and unavailable diagnosis are visible blockers. No blind full-run reset.
4. Idle time must produce a specific reason: dependencies, resources, credentials, execution contract, QC, scientific hold or exhausted repair budget. A planner should create missing contracts under the existing plan and add low-cost evidence nodes. If no planner command is configured, report that limitation explicitly; do not claim unattended planning.
   Repairs rank ahead of new planning. `priority_nodes` selects the active mainline; within each priority use fewest-visits fairness and bounded cooldown. Normal planning and initial execution do not spend failure quotas in v2; two nonproductive proposals expose planning_stalled. No project-wide call cap blocks independent execution. Explicit targeted human intervention resets only that node via `intervene`, preserving historical attempts and evidence; progress queries and restarts do not reset counts. See failure_recovery.md.
5. Deliver project events via a durable outbox. In v2, hook failure retries durable delivery and holds final scientific publication, but does not stop independent artifact jobs; running jobs remain tracked. Legacy configurations retain the global hold. Hooks must be idempotent. Keep one writer per project document set or use transactional locking.
6. Successful artifact computation proceeds to hashed validation and releases its independent compute dependents. Report nodes proceed through validation and real interpretation; final publication waits for hook acknowledgement. Literature/API failure may be retried by the interpretation worker, but must not be called scientific completion. Strong contradictions hold dependent branches for discussion; unrelated tasks continue.
7. Respect project/session isolation. No `resume --last` across projects. Agent workers create their own session logs; job attempt logs are separate from conversation journals.
8. Service restarts and login persistence differ: `systemctl --user enable` starts at login; continuing while logged out requires user lingering (`loginctl show-user USER -p Linger`) or an administrator-managed service. Machine shutdown stops local orchestration; remote jobs retain their own lifecycle.

## Result validation and interpretation JSON

All phase output evidence must be synchronized to the project's canonical local result directory before interpret exits successfully. `_evidence/qc.json` contains `run_id`, `passed: true`, `artifacts: [{path,sha256}]`. `_evidence/reflection.json` contains the same `run_id`, `expected`, `observed`, `uncertainty`, `reasoning`, `alternative_explanations`, `evidence_strength`, `limitations`, `next_step_impact`, `decision` (`continue`, `supplement`, `needs_user`) and `literature_search`.

`literature_search` records `queries`, `searched_at`, `status` (`searched`, `no_relevant_results`), and `sources: [{url,title,relevance,supports_or_conflicts}]`. `no_relevant_results` requires a documented actual search, not fabricated citations. A reviewer must verify sources and statistics; the daemon validates structure and hashes and cannot certify truth. Preserve the preregistered expectation and classify results as support/contradict/inconclusive. Do not retrofit the hypothesis to observed rankings. For each affected dependent task explain whether its scientific premise still holds, whether the expected information gain is reduced, and whether the next action is continue/extra evidence/pause/amendment.

Use `supplement` only for nonblocking evidence improvements; represent any required precondition as an explicit dependency. Never alter an existing frozen endpoint in a supplementary node.
