# Scientific Research Agent Design (English)

Scientific Research Agent Design is an automation framework for real scientific projects, combining a reusable Skill with a Supervisor Agent. It connects research goals, literature appraisal, protocol design, software and data versions, task dependencies, resource scheduling, execution, QC, interpretation, and next-step planning into an auditable project lifecycle.

## Key strengths

- Deep-research gate: survey foundational and recent work, then discuss and freeze the plan with the user.
- Project contract: `00_PROJECT.md`, `01_PLAN.md`, `02_SOFTWARE.md`, `03_DATA.md`, and `04_STATUS.md` make intent, plan, environments, data, and status explicit.
- Complete execution: model × dataset × stage nodes form a dependency DAG; eligible units are not silently omitted.
- Auditable evidence: every run records commands, environments, versions, input/output hashes, QC, tables, figures, and conclusions.
- Recoverable operation: preserve failure evidence, diagnose, apply a targeted repair, minimally verify, and resume only the failed phase.
- Explainable results: compare expectations with observations and document uncertainty, anomalies, literature evidence, and downstream impact.

## Lifecycle

User question → Supervisor intake → draft `00_PROJECT.md`/`01_PLAN.md` → Deep Research Gate → user discussion → final frozen five root documents → dependency/resource registry → execution → QC → literature-grounded interpretation and reflection → automatic progression.

## Supported execution scope

The bundled driver currently supports:

- local CPU/GPU execution;
- SSH-connected remote CPU/GPU servers;
- `systemd --user` job management and resource probing on local or remote hosts.

Docker, Slurm, cloud jobs, and online API adapters are not claimed as built-in features.

## Repository

`skills/scientific-research-project/` contains the Skill; `adapters/claude/` contains the Claude adapter; `project_template/` contains project templates. See `INSTALL.en.md` for English installation instructions and `INSTALL.zh-CN.md` for Chinese instructions.

Current release: **0.5.1**.
