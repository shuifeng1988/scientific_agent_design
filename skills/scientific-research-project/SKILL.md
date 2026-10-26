---
name: scientific-research-project
description: "Create and coordinate auditable scientific projects using five root documents, detailed approved plans, one result package per task, continuous execution and scientific review. Use when starting, resuming, auditing or extending a multi-step research project; route specialized methods to replaceable skills or agents."
---

# Scientific Research Project

This is the project coordinator and shared contract. Methods are replaceable; the project's scientific workflow, evidence and acceptance requirements remain binding. Read [project_contract.md](references/project_contract.md) on entry and [the supervisor role](references/roles/supervisor.md) when coordinating work. Reference paths in operating contracts are relative to this package root.

## Understand before planning

For a new or materially ambiguous research direction, read [intake_protocol.md](references/intake_protocol.md) **before drafting, broad research, delegation or execution**. Briefly restate your understanding, ask 1–3 focused questions with concise choices and unrestricted free text using the permitted interface, then end the turn and wait. Never infer consent from defaults, silence or automatic Skill selection. Continue the dialogue and confirm the actual purpose, focal question, scope, starting resources and intended outcome.

Only after direction confirmation create preliminary 00_PROJECT.md/01_PLAN.md, conduct deep research, discuss the findings/method choices and obtain the separate final design decision. Existing approved tasks reuse actual prior decisions without repeating intake. Installation, explanation and framework maintenance are not new research intake. A noninteractive worker returns needs_user to the outer conversation and never fabricates answers.

## Project identity that every module preserves

- The five root documents—00_PROJECT.md, 01_PLAN.md, 02_SOFTWARE.md, 03_DATA.md and 04_STATUS.md—remain the common guidance. Read them for an existing project; early intake has only available context, followed by two drafts and then five formal documents.
- Each Q/task in the detailed plan has one registered results path. Keep model/run/retry children under that path. No second master plan, parallel result tree or silent reduction of eligible models/data.
- Each formal result includes detailed data/software provenance, methods and actual commands, numerical results with applicable uncertainty, conclusions, scientific interpretation, tables, figures, README.md, REPORT.docx, QC/reflection and evidence hashes. Explain what the evidence supports and does not support.
- Formal result figures use the project `scientific-visualization` adapter and `figure_quality_contract.md`: publication-size typography, honest uncertainty/denominators, accessible color, vector/raster export, source-table lineage and bounded visual correction before acceptance.
- Preserve real source searches, contrary evidence, design depth, actual approvals, bounded recovery, monitor truthfulness and durable events. Never silently change frozen scientific scope. A technical artifact may release downstream computation after its own QC; formal scientific completion retains all report/review/publication gates.
- Reuse existing scoped authorization for routine implementation and continuation. New scientific decisions go to the user. Host permissions still apply; a provider/configuration is not authorization.

## Route by capability

Use the bundled stage Skill when installed; otherwise read the same references directly from this self-contained core. Resolve project-specific selections using `scripts/module_provider.py resolve --root PROJECT --capability CAPABILITY --host HOST`. The manifest is [assets/modules.json](assets/modules.json). An explicit unavailable provider is a visible blocker, never a silent method substitution.

| Capability / stage Skill | Read when needed |
|---|---|
| intake / scientific-intake | [Intake](references/intake_protocol.md) |
| evidence / scientific-evidence | [Deep research](references/deep_research_gate.md), [core evidence](references/core_evidence.md), [method providers](references/research_skill_bridge.md), [research depth](references/research_depth.md) |
| design / scientific-design | [Design contract](references/design_contract.md), [research depth](references/research_depth.md), [workflow gates](references/workflow_contract.md) |
| execution / scientific-execution | [Execution contract](references/execution_contract.md), [continuous execution](references/continuous_execution.md), [artifact/DAG policy](references/execution_first_architecture.md) |
| recovery / scientific-recovery | [Failure recovery](references/failure_recovery.md), [execution contract](references/execution_contract.md) |
| interpretation / scientific-interpretation | [Reflection](references/reflection_protocol.md), [core evidence](references/core_evidence.md) |
| reporting / scientific-reporting | [Project/result schema](references/project_schema.md), [workflow/report gates](references/workflow_contract.md) |
| visualization / scientific-visualization | [Publication-ready figure contract](references/figure_quality_contract.md), [project/result schema](references/project_schema.md) |
| review / scientific-review | [Substantive review](references/research_depth.md), [core evidence](references/core_evidence.md), [package checks](references/workflow_contract.md) |

External skills/subagents use [provider_contract.md](references/provider_contract.md). They replace a method within a capability, not this project contract. Preserve raw output and normalize it to existing appraisal, contract, reflection or report records. The provider's reputation and exit status do not establish scientific correctness.

## Execution and platform boundary

`scripts/supervisor_agent.py` provides intake/inspect/plan/review/reflect inventories. It does not itself perform research or establish scientific completion. For authorized continuous execution read [supervisor_protocol.md](references/supervisor_protocol.md) and the execution references; use the resident `supervisor_daemon.py`, real workers and configured local/SSH systemd drivers. Legacy execute remains disabled. Register background work in ~/.codex/monitor/tasks.json, ensure its monitor service is active and verify a fresh snapshot before claiming it is running. State actual child jobs, blockers and how to monitor them.

Roles are host-neutral reference contracts: supervisor, researcher, executor, reviewer and reporter under `references/roles/`. They can run sequentially; independent/parallel agents require an actual host invocation and applicable authorization. Claude definitions live in the source adapters directory. Codex can use the stage Skills and role contracts directly. The bundled background CLI adapter remains Codex; no untested Claude daemon or additional execution backend is implied.

Updates must preserve existing task/run/job IDs, successful evidence, frozen baselines and registered hooks. Do not migrate live projects, overwrite final receipts or recompute completed research merely to adopt this modular organization. Keep invocation notes in unique project-local logs/sessions/ files; do not read other session journals without a historical-review request.

## Scientific acceptance and controlled change

Read [scientific_governance.md](references/scientific_governance.md) for new-design/result independent review receipts, read-only reviewer invocation, approved plan amendments, required/optional supplemental nodes and evidence-linked behavioral evaluation. New designs enforce the review policy; existing frozen legacy baselines retain their recorded behavior until deliberately migrated. Scientific review waits do not consume technical recovery budgets.
