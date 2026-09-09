# Diagnose before repair and retry (v0.5)

This contract applies to every Agent step: planning, downloads, installation,
preprocessing, smoke, formal computation, validation, interpretation and reporting.

**发现失败 → 保留证据 → 诊断原因 → 针对性修复 → 最小验证 → 断点重试 → QC 验收 → 继续推进。**

1. Confirm terminal state first. Save run/job/phase, command, host/environment,
   input/code hashes, exit status and bounded stderr/traceback. An unknown SSH
   state is not a confirmed failure: retain the lease and reconcile the same ID.
2. Diagnose using evidence. Distinguish code/serialization, dependencies,
   resources, network, credentials, data/QC and scientific/design discrepancies.
   A classifier supplies a lead, not a proven root cause. Do not label all failures OOM.
3. Apply a cause-specific remedy under existing authority. Fix code or dependencies;
   adjust an authorized resource profile; for confirmed transient network errors,
   use bounded backoff plus a connectivity check. Do not resubmit the same known
   broken command. Never change endpoints/exclusions or fabricate values to pass QC.
4. Run a minimal regression/reproducer before retry. Record command, exit code,
   test-log hash and tested code hashes. A textual "fixed" claim is insufficient.
5. Resume only the failed phase with a unique job ID and bounded attempt count.
   For validate/interpret, preserve the original run ID and verify the reused
   artifact hashes; use SCI_ATTEMPT/SCI_JOB_ID for new, non-overwriting outputs.
   Earlier successful phase specs remain unchanged. If earlier evidence is invalid,
   block and propose an explicit scoped recomputation instead of silently resetting run.
6. Recheck output/QC/reflection, emit project events, update the five core documents,
   then dispatch ready dependents. Retry success alone is not scientific completion.

## Scheduling and budget

Repairs take precedence over new planning; preserve mainline priority and fairness.
For `execution_policy=v2`, each stable task/phase incident has 3 repair-worker calls
and 3 verified retries per human-approved round. Initial execution and normal
contract planning do not consume these failure quotas. All AI calls remain cost
telemetry. Two nonproductive proposals stop planning with a visible planning_stalled
reason; validated helper code alone is not an executable contract. New process IDs,
changed exception text, service restarts and edited code do not reset the incident.
Legacy configurations retain their old per-node attempt semantics.
One exhausted node never consumes or blocks another node's budget. Timeout,
resource limits and failure backoff still apply. Provider token/account limits
cannot be reset by this feature.

An explicit user instruction to repair/continue named tasks starts a fresh round
for those tasks using `supervisor_daemon.py intervene --root PROJECT --node ID
--reason REASON`. Stop the project daemon first (writer lock), reconcile terminal
state, invoke once per named task, then restart it. Never reset for status queries,
service restart, automatic retry, or merely because a counter is exhausted.
The command preserves lifetime attempts/IDs, artifacts and failure history and
writes a hashed intervention record. It resets only the target task/phase incident counters and no-progress count in v2
(or the legacy worker/execution baseline); diagnosis, minimal verification and QC still apply.
Running/unknown jobs, live target workers, frozen results and scientific holds
must not be bypassed. The daemon cannot grant itself fresh rounds.

Migration retains all lifetime visits/attempts as evidence; v2 does not treat old
normal planning visits as failure retries. Display lifetime AI usage and current
phase repair/replay counters separately.
`legacy_project` is opt-in backwards compatibility only; new/current installations
must use `per_node`. Old `max_calls_per_day`, `repair_reserved_calls` and one-off
`manual_dispatch` do not constrain or bypass per-node mode.

## Machine-checked repair proposal

Each repaired item in `contracts` additionally supplies `recovery`:

```json
{
  "failure_record_sha256": "hash from node failure_record",
  "diagnosis": "evidence-backed root cause",
  "action": "what changed and why it addresses that cause",
  "resume_phase": "interpret",
  "validation": {"path": "results/.../repair/test_result.json", "sha256": "..."},
  "preserved_artifacts": [{"path": "results/.../original/output.json", "sha256": "..."}],
  "reuse_justification": "why completed phase outputs remain valid"
}
```

The referenced validation JSON contains `passed: true`, `exit_code: 0`, a nonempty
`command` argv list, `log: {path,sha256}`, and `tested_gates: [{path,sha256}]` covering
every new/changed executable source gate. Paths are project-relative; test artifacts
live under that node's result path. Preserve existing non-code gates and all earlier
phase specs. Keep raw failure evidence and retain the same maximum attempt budget.
The supervisor checks evidence linkage/hashes, not the truth of arbitrary claims;
the repair worker must actually execute the tests and explain its diagnosis.

For structured Agent output, preserve raw text and require a single schema-valid
object. A logged repair may remove exactly one extraneous final `}` from an otherwise
complete object. Reject duplicate keys, conflicting documents, prose suffixes,
truncation, nonfinite constants and missing required fields; never invent content.

## Acceptance tests

Inject a failure and verify diagnosis is stored before repair, failed validation
prevents retry, correct repair resumes only the failed phase, artifact hashes and
attempt limits are enforced, restart does not duplicate jobs, and successful QC
releases the dependent task. Include JSON, environment/resource failure routing,
unknown remote status, stale approval/context and exhausted-budget cases. State
whether tests used mocked drivers, real scheduling or a real model worker.
