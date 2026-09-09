# Event-hook specification

_Synchronizes downloads, environments, runs, results, plans, status, and reports._

---

## ⚡ Event contract

Every event contains `event_id`, `event_type`, `timestamp`, `project_id`, `question_id`, optional `task_id`/`run_id`, actor, payload, artifact paths, hashes, and idempotency key. Append events to `provenance/events.jsonl` before rendering documents.

## 🔄 Update transaction

```mermaid
flowchart LR
    accTitle: Research Documentation Hook
    accDescr: A verified event updates registries, checks consistency, and only then renders human-facing project and result documents.

    emit_event([⚡ Emit event]) --> validate_event[🔍 Validate event]
    validate_event --> update_registry[💾 Update registries]
    update_registry --> check_consistency{🔍 Consistent?}
    check_consistency -->|Yes| render_docs[📝 Render documents]
    render_docs --> save_snapshot([✅ Save snapshot])
    check_consistency -->|No| keep_previous[⚠️ Keep previous docs]
    keep_previous --> raise_alert([❌ Raise sync alert])

    classDef action fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef decision fill:#fef9c3,stroke:#ca8a04,stroke-width:2px,color:#713f12
    classDef outcome fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d

    class validate_event,update_registry,render_docs action
    class check_consistency decision
    class emit_event,save_snapshot,keep_previous,raise_alert outcome
```

## 📋 Mandatory hooks

| Event | Required updates |
|---|---|
| Data downloaded/verified/standardized | `03_DATA.md`, `04_STATUS.md`, data registry |
| Software downloaded/installed/smoked | `02_SOFTWARE.md`, `04_STATUS.md`, software registry |
| Run started/progressed/failed | `04_STATUS.md`, run registry, task evidence |
| Run and QC completed | `01_PLAN.md`, `04_STATUS.md`, task README, tables/figures, Word report |
| Evidence gap or contradiction | `04_STATUS.md`, result reflection, amendment draft |
| Plan amendment approved | `01_PLAN.md`, task registry, decision ledger, affected result README |

No hook may silently alter a frozen objective, primary endpoint, cohort, method, or exclusion rule.

