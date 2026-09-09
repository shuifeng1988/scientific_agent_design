# Execution-first Supervisor v0.5.0

## Why the architecture changed

A resident process is insufficient when every task requires an LLM to invent a
contract, technical prerequisites require literature interpretation, and ordinary
planning spends the same quota as failure repair. The system can remain alive
without launching scientific work. v0.5 makes those boundaries explicit.

```text
Five root documents + approved scientific scope
                    |
        Complete model × stage DAG compiler
                    |
       Deterministic resident scheduler <---- durable state / known job IDs
          |                      |
   ready contracts         missing contract / confirmed failure
          |                      |
   resource reservation    bounded planning or diagnosis/repair worker
          |                      |
     H100 / V100 <---------- tested, hash-gated contract
          |
      artifact QC ---------> independent next computation
          |
   report + literature + reflection + Word/tables/figures
          |
   full-panel scientific QC + acknowledged publication hook
```

The deterministic scheduler does not reason about scientific truth. The AI worker
does not own the scientific scope or unilaterally reset execution state.

## Contracts and dependency expansion

Set `execution_policy: v2` in `registry/supervisor.json`. Keep legacy mode for
unmigrated projects. `completion_policy: artifact` requires run and validate phases,
`scientific_result: false`, and `finalizes_task: false`. The local canonical result
directory must contain a methods/provenance README and `_evidence/qc.json` with the
matching run ID and nonempty verified artifact hashes. Remote large artifacts may
remain remote if the gated remote validator produces a copied, hash-linked receipt.
An artifact is not a complete scientific result and never supplies a performance
claim without the task's final analysis.

Report nodes retain run/validate/interpret and full result evidence. Only the
registered parent task may finalize its scientific result; it depends on the
complete model/stage matrix. In v2 final publication stays `publishing` until its
durable hook event succeeds. A document-hook outage does not stop independent
artifact jobs. Genuine scientific contradictions still hold affected descendants.

An unattempted, contract-free parent may have operator-owned `expansion_policy`:
`models`, `stages`, `max_new_nodes`, `stage_dependencies`, `scope_gates`.
The worker may return `expansions: [{parent_id, nodes}]` alongside `contracts` and
`blocked`. All authorized model/stage pairs must be included. IDs are
`PARENT.MODEL.STAGE`; paths are `PARENT_RESULT/models/MODEL/STAGE`. Children inherit
the parent's prerequisites, execution context and scope hashes. Missing/duplicate
nodes, changed scope gates, foreign paths, cycles and extra fields are rejected
before the candidate DAG is atomically adopted. No automatic panel reduction.

## Recovery, liveness and operational limits

- Incident identity is stable task + phase, not a new job ID or exception string.
- Each incident round allows 3 repair-worker calls and 3 tested retries. The first
  execution and normal planning do not spend those failure quotas. All calls and
  lifetime attempts remain visible for cost auditing; provider limits still apply.
- Failure requires preserved logs → diagnosis → targeted change → minimal passing
  test → resume only the failed phase. A timeout is not proof of OOM.
- Two consecutive proposals without an adopted contract/authorized expansion expose
  `planning_stalled`. A helper, another inventory or a “fixed” statement is not
  executable progress. The daemon does not grant itself unlimited extra rounds.
- Explicit human intervention resets only the selected incident; status queries,
  service restarts and modified code do not. Unknown remote jobs keep their leases.
- Monitor reports service health separately from project progression: running,
  planning_or_repairing, waiting_resources, stalled, complete. Final completion
  additionally requires scientific package validation and hook acknowledgement.

Resource reservations coordinate this project daemon, not unrelated schedulers.
Use a cluster scheduler/dedicated partition for global exclusivity. Local daemon
availability is required to launch next steps; remote submitted jobs survive a
local daemon restart. Credentials, provider account outages, and unresolved
scientific choices cannot be repaired by an unlimited retry loop.

## Migration and acceptance

Stop only the project's Supervisor, reconcile current jobs, preserve config/state
snapshots, classify artifact versus report nodes, compile the full authorized
matrix, and keep frozen input/protocol hashes unchanged. Run `check`, regression
tests and a real driver acceptance chain before restarting the service. Verify a
fresh monitor snapshot and actual remote process/output; do not report a scheduled
contract as a running model.

`test_execution_policy.py` covers new quota boundaries, expansion, artifact release,
stall reporting and publication acknowledgement. `live_execution_acceptance.py`
uses tiny real local systemd jobs: prepare → compute plus an intentionally failed
report branch, reloading durable state between ticks. This validates scheduling,
not any scientific model. Real model preparation and formal results require their
own remote evidence. The project's explicit matrix compiler and adapters are
project code, not hard-coded into this generic Skill.
