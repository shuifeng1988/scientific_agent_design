# Scientific Research Agent Design — English Guide

Scientific Research Agent Design is a general-purpose Skill + Supervisor Agent for auditable scientific work. It operationalizes the full research loop: clarify the question, perform a literature-grounded appraisal, design a protocol, pin software/data/splits, execute the complete eligible matrix, validate evidence, interpret results, reflect on anomalies, and continue to the next ready task.

## Architecture

The system has five human-facing project documents (`00_PROJECT.md`, `01_PLAN.md`, `02_SOFTWARE.md`, `03_DATA.md`, `04_STATUS.md`), a registry and provenance layer, a dependency/resource-aware DAG, a resident Supervisor daemon, execution workers on declared GPU servers, and an interpretation/review layer. A new plan cannot be frozen until recent (24–36 month) and foundational literature has been searched, conventional/current/frontier methods compared, feasibility assessed, and high-impact choices discussed with the user.

## Strengths

- Auditable event history, checksums, software/checkpoint versions, and run evidence.
- Complete eligible model coverage; no silent panel reduction.
- Explainable reports with methods, data provenance, QC, figures, uncertainty, expectations, and limitations.
- Portable deployment because hosts, environments, resources, commands, and paths are registered.
- Bounded diagnosis-and-repair recovery instead of blind retries.
- Continuous, resource-aware progression through ready DAG nodes.

## Main components

- `scientific-research-project` Skill: operating contract and research gates.
- Supervisor Agent: intake, inspect, plan, review, and reflect modes.
- Resident Supervisor Daemon: monitoring, dispatch, dependency release, and bounded recovery.
- Project templates and Claude adapter.

## Layout and installation

See [`INSTALL.md`](INSTALL.md) for Codex/Claude installation and validation. The Skill entry point is `skills/scientific-research-project/SKILL.md`; detailed procedures are in `skills/scientific-research-project/references/`.

Current release: **0.5.1**.
