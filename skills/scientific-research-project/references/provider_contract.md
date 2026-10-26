# Replaceable method providers

The `scientific-project-v1` contract preserves the five root documents, actual intake/design decisions, detailed methods, one registered result package per plan task, complete approved scope, real evidence, Markdown/Word/tables/figures, scientific interpretation and existing runtime/acceptance rules. See project_contract.md and the selected stage references. A provider replaces how a bounded method is performed; it cannot waive these requirements.

## Selection and availability

The bundled `assets/modules.json` defines capability/role/reference/output boundaries. Optional project-local `registry/providers.json` selects methods. No override means the self-contained built-in method. Explicit overrides never silently fall back when unavailable: return a blocker and let the operator choose a compatible provider. Changing the provider does not authorize a scientific design change or a paid service, data upload or new agent team.

Example (replace the illustrative name/version with an actually installed, reviewed provider):

```json
{
  "schema_version": 1,
  "contract_version": "scientific-project-v1",
  "bindings": {"evidence": "preferred-literature"},
  "providers": {
    "preferred-literature": {
      "kind": "skill",
      "version": "locally-reviewed-version",
      "entrypoint": "my-installed-literature-skill",
      "hosts": ["codex", "claude"],
      "instructions": "Use its search/extraction/synthesis method for the assigned question. Preserve raw outputs and adapt sources, queries, access depth, contrary evidence, methods and limitations into this project's appraisal.json plus readable appraisal/evidence tables."
    }
  }
}
```

Use `kind: subagent` for an actually callable host agent and list only supported hosts. A declared host/version is configuration, not proof of installation or compatibility: the invoking operator must inspect the actual entry/version, needed tools and relevant instructions before use. Record actual provider/version, source location/hash where available, invoked tools and access limits with the raw evidence. Retain applicable attribution/licensing; do not vendor third-party prompts automatically.

Run `python scripts/module_provider.py resolve --root PROJECT --capability evidence --host codex` (or claude). The command resolves/validates configuration and emits required reads and the bounded output contract; it does not install or invoke anything. The outer host uses its real Skill/subagent mechanism. Read provider instructions as bounded method guidance, not authority to alter project policy. Tool availability and higher-priority host/user instructions continue to apply.

## Handoff for external work

After the relevant real direction/plan decisions, create a request:

```bash
python scripts/module_provider.py prepare --root PROJECT --capability evidence --host codex --objective 'Appraise the confirmed research question with supporting and contrary primary evidence'
```

For an existing task add `--task-id Q01.01`. Requests go under that task's registered `_evidence/providers/REQUEST_ID/`; pre-task appraisal goes under `provenance/providers/REQUEST_ID/`. These are evidence working directories, not new root files or competing final results. For existing revisions, link the handoff from the existing amendment/appraisal record and integrate returned evidence there.

Give the provider request.json, the shared contract, role and selected stage references. Read all available five roots as the common guidance and the relevant detailed task card. The request contains the objective, root-document receipts, scientific baseline, canonical task/result mapping, provider selection and output directory. New schema-2 requests record explicit task input receipts (`--inputs` JSON list; default available 00/01), timeout and output byte limits, plus `--run-id` for interpretation/reporting and an exact `--review-subject` for review. Supply all actual data/model/code manifests needed by the method, not just defaults. Additional evidence may be supplied by the operator; do not infer missing scientific choices. Request generation records context; it does not prove user consent or completed intake.

Write raw output, evidence and normalized deliverables in that output directory. Return an output.json beside request.json:

```json
{
  "request_id": "COPY_FROM_REQUEST",
  "request_sha256": "ACTUAL_REQUEST_FILE_SHA256",
  "provider_id": "preferred-literature",
  "status": "ready_for_review",
  "summary": "What was done, access limitations and unresolved decisions",
  "artifacts": [{"path": "PROJECT_RELATIVE_ARTIFACT_PATH", "sha256": "ACTUAL_SHA256"}]
}
```

Other statuses are `needs_user` and `blocked`. Missing access is not no evidence; missing user decisions are not technical retries. Noninteractive agents return questions for the outer conversation. No provider response may assert task completion, fabricate approval, change registry/state, reset budgets or start durable jobs. The host must constrain actual writes/tools; these checks are validation, not an OS sandbox.

Validate the handoff with `python scripts/module_provider.py check-output --root PROJECT --request REQUEST_JSON --output OUTPUT_JSON`. It rejects stale baseline/provider contracts, wrong request/provider/task paths and changed artifact hashes. `ready_for_review` evidence requires the existing appraisal schema plus `status: ready_for_design_review`; execution/recovery requires proposal.json in the existing proposal format. Schema-2 intake requires intake.json with user evidence/unresolved choices; design requires design_proposal.json with five documents/tasks/appraisal; interpretation requires run-bound reflection.json; reporting validates report.json with the existing content validator; review requires scientific_review.json bound to the requested subject. These are normalized-payload checks; substantive review and final integration remain necessary.

## Acceptance and integration remain separate

| Capability | Provider contribution | Remaining acceptance |
|---|---|---|
| intake | Brief and unresolved questions | Real dialogue and direction confirmation |
| evidence | Readable appraisal, evidence/source/method tables and appraisal.json | Substantive source/claim/design review; discussion; real approval bound to final proposal/appraisal |
| design | Proposed five documents and detailed task cards | Existing design review and freeze/reviewed amendment process |
| execution/recovery | Scripts, tests, proposal.json and repair evidence | Daemon contract/recovery validation, resources, gates and bounded scheduling |
| interpretation | Run-bound reflection and source records | Scientific review, anomaly decision and downstream hold logic |
| reporting | Report manifest and actual source tables/figures | Existing same-source renderer, package checks and acknowledged publication event |
| review | Evidence-linked adequate/revise/needs_user findings | Supervisor integration; author fixes; real user decisions where required |

A valid handoff is not scientific correctness or publication authorization. The reviewer must read actual source material and output contents; hashes cannot establish their meaning. Preserve prior results/provider receipts when switching methods. If the switch changes approved cohorts, endpoints, eligibility, assumptions or cost/scope, use the existing decision/amendment rules.

The Codex progress worker resolves execution/recovery selections automatically and saves its selected-provider receipt with its existing request. Its legacy proposal schema and daemon recovery behavior are unchanged. General external research handoffs are host-mediated; this package does not claim a generic autonomous Claude/API runner or automatic discovery of all third-party agents.


## Installed literature-review adapter and limits

`literature_adapter.py inspect --entry /ACTUAL/PATH/SKILL.md` reports the installed entry hash and presence of its main command, without claiming authentication or online access. `config --entry /ACTUAL/PATH/SKILL.md --host codex` emits a project configuration for review/merge; it does not overwrite an existing provider configuration. A portable template is [literature-review-local.example.json](../assets/provider_examples/literature-review-local.example.json). Add other hosts only after actually checking their tools. Paths and fingerprints in examples must be regenerated on each installation.

The actual host invokes the selected skill on request.json. Keep raw search/extraction outputs and readable synthesis in the assigned directory and write a canonical appraisal.json. Preserve source/search file receipts. Then `literature_adapter.py normalize --root PROJECT --request REQUEST --appraisal APPRAISAL --raw RAW_OUTPUT --tool-record TOOLS_JSON` records provider/source/raw-output receipts and emits/checks output.json. Repeat --raw for multiple artifacts. TOOLS_JSON contains actual `tools` and an `access_limits` list. Missing evidence remains blocked rather than filled with templates. No third-party source is vendored.

Absolute local provider entrypoints are fingerprinted and rechecked. Named remote/subagent entries still require host verification; their declared version is not a remote attestation. Schema-2 handoffs reject changed declared inputs, expired requests and output directories exceeding max_output_bytes (request and evidence included). These are acceptance limits, not preemptive CPU/RAM/network enforcement; runners must impose operational budgets, and execution/recovery retains existing resource contracts. Old schema-1 receipts retain their original checks. All new prepare calls emit schema 2.
