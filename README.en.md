# Scientific Research Agent Design: Research Execution and Reporting

[Chinese guide](README.zh-CN.md)

This project is an automated research framework combining a Skill with a Supervisor Agent for real scientific projects. It organizes problem definition, literature research, study design, software and data preparation, execution, quality control, interpretation, and follow-up research into a continuous workflow. Starting from the overall objective, it helps researchers establish clear plans, manage execution progress, and build auditable, reproducible, human-readable research outputs.

The Skill defines how research work should be performed, guiding the Agent to understand the question, develop the plan, execute its steps, record evidence, and interpret results. The Supervisor coordinates tasks according to the approved plan, dependencies, available resources, and execution state, tracking progress, managing recovery, and advancing subsequent work. Together, they connect project objectives, execution, and research reports.

## 1. Core advantage: organize work like a researcher and deliver results step by step

The central principle is to **organize research as a researcher would: define the question, develop detailed steps through literature research and discussion, then have the Skill guide the Agent to follow the approved plan step by step and interpret and reflect on the findings**. Execution follows `01_PLAN.md`, with a corresponding, reviewable research package for every step under `results/`. Following the plan leads researchers directly to each step's data sources, software and methods, actual commands, results, conclusions, scientific interpretation, figures, tables, and Word report. When the research direction needs to change, discuss and record the plan amendment before continuing with the revised steps.

`00_PROJECT.md` defines scientific questions; `01_PLAN.md` decomposes them into executable tasks; `registry/tasks.tsv` assigns each task one canonical result path. Multiple runs, models, or seed sub-tasks remain inside that task's directory and feed its consolidated report. General research need not become a model-comparison matrix; comparative studies must include all participants approved in their plan.

The following is an organizational example, not an experiment that has already been run:

```text
00_PROJECT.md: Q01 Does a factor affect the study endpoint?
01_PLAN.md: Q01.01 Data quality; Q01.02 Primary comparison
registry/tasks.tsv: one canonical result_path per task
results/
└── Q01_research_question/
    ├── Q01.01_data_quality/
    │   ├── README.md          # Data, methods, results, conclusions, interpretation
    │   ├── REPORT.docx        # Word report consistent with Markdown
    │   ├── tables/            # Statistics, missingness, and failures
    │   ├── figures/           # Figures, legends, and captions
    │   └── _evidence/         # Runs, QC, hashes, and interpretation evidence
    └── Q01.02_primary_analysis/
        ├── README.md
        ├── REPORT.docx
        ├── tables/
        ├── figures/
        └── _evidence/
```

| Package component | Required detail |
|---|---|
| Plan correspondence | Scientific question, task ID, plan version, dependencies, expectations, and links back to the project and plan |
| Data provenance | Dataset description, source link, version, acquisition or access method, actual path, selection criteria, counts, and checksums; reference large raw data without duplicating it |
| Software and methods | Purpose, source, version, environment, checkpoint version, parameters, actual commands, seeds, host, and CPU/GPU resources |
| Results | Values, sample denominators, effect sizes and applicable uncertainty; retain missingness, failures, and approved exclusions |
| Tables and figures | Readable tables, corresponding plots and captions, sources, and generation methods; plotted data trace back to tables and runs |
| Conclusions | Answer this step's scientific question and state what the evidence does and does not support |
| Interpretation and reflection | Expected versus observed findings, mechanisms, alternatives, supporting or conflicting literature, limitations, and downstream impact |
| Human-readable reports | `README.md` and `REPORT.docx` contain consistent values, figures, and conclusions; logs alone are insufficient |
| Acceptance evidence | Run IDs, input/output hashes, QC checks, failure records, and review decisions |

Update corresponding tables, figures, and report drafts as batches are validated; deliver consistent Markdown and Word reports when the formal analysis finishes. Intermediate artifact nodes may release subsequent computation after hash and QC validation; the parent scientific analysis still needs reporting, interpretation, and project-event acceptance. Configured analysis/report workers produce figures, Word documents, and scientific interpretation. The daemon schedules work and checks structure; it does not replace scientific review.

## 2. Architecture: from research question to execution

```mermaid
flowchart TD
  U["User proposes a research project or question"] --> A["Clarify in rounds, wait for answers, confirm direction"]
  A --> B["Draft 00_PROJECT.md and 01_PLAN.md"]
  B --> C["Deep research: progress, significance, feasibility, methods"]
  C --> D["User discussion, revision, and confirmation"]
  D --> E["Establish five formal root documents and freeze the design"]
  E --> P["Specific steps in 01_PLAN.md"]
  P --> R["Register IDs, canonical result paths, dependencies, resources"]
  R --> S["Supervisor schedules ready tasks"]
  S --> X["Execute under the actual host configuration"]
  X --> V["Validate results and quality"]
  V --> O["Corresponding task package under results"]
  O --> I["Accept methods, results, interpretation, figures, tables, Word"]
  I --> H["Record events and update documents and status"]
  H --> N{"Scientific next-step decision"}
  N -->|"Continue or register supplementary evidence tasks"| R
  N -->|"Major anomaly or design change"| D
  X -->|"Technical failure"| F["Preserve evidence, diagnose, repair, minimally verify"]
  F -->|"Resume only the failed phase"| X
```

The five formal root documents establish an agreed project baseline. Unavailable software or data remain explicitly pending; status changes during execution, and design revisions retain approval and version records. “Formal” does not mean installation, downloads, or research have finished.

| File | Purpose |
|---|---|
| `00_PROJECT.md` | Objectives, scientific questions, scope, hypotheses, and final deliverables |
| `01_PLAN.md` | Data, software, methods, dependencies, result paths, and completion criteria for each step |
| `02_SOFTWARE.md` | Software/model descriptions, sources, versions, environments, installation/use, host locations, and validation |
| `03_DATA.md` | Data descriptions, sources/versions, download/access methods, storage, checksums, and splits |
| `04_STATUS.md` | Pending, running, failed, blocked, and complete tasks, with evidence links and next actions |

## 3. The core Skill workflow

1. **Understand the purpose.** Do not require a complete specification in the opening message. For a new project or vague direction, briefly restate the tentative understanding, ask 1–3 focused questions, then end the response and wait. Use feedback to clarify the question and explore alternatives. Summarize the purpose, focal question, scope, starting evidence/resources, and intended use; obtain confirmation before drafting. Do not append a full proposal to the clarification questions. Resuming an approved task does not repeat intake.
2. **Draft the plan.** Create preliminary `00_PROJECT.md` and `01_PLAN.md`, preserving hypotheses, candidate methods, and open decisions.
3. **Conduct deep research.** Search foundational and recent work, recording dates, sources, queries, and evidence. Compare conventional, current reproducible, and new methods; assess significance, whether the work is worthwhile, feasibility, and information gain. Recent searches usually cover 24–36 months alongside foundational literature.
4. **Agree on the design.** Present method options, risks, data, and resources. After user confirmation, establish the five formal documents and statistical, exclusion, stopping, and amendment rules.
5. **Prepare each planned step.** Select a dependency-ready step from `01_PLAN.md`; read its data, software, commands, result path, and acceptance criteria.
6. **Execute and document.** Preserve data references, actual methods, and run evidence in the mapped directory; progressively produce tables, figures, results, and reports so outputs remain connected to the plan.
7. **Validate and deliver.** Check counts, denominators, hashes, environments, and failure mechanisms; complete Markdown, Word, and visual deliverables. Explicitly identify unsuccessful checks.
8. **Interpret and reflect.** Answer the task question, compare expectations and literature, and document alternatives, limitations, and the value of downstream work.
9. **Recover or amend.** Diagnose technical failures before bounded repair and phase resume. Discuss major scientific anomalies and frozen-design changes with the user. Register low-risk, valuable supplementary analyses within scope as traceable tasks.
10. **Update and progress.** Project events record downloads, environments, runs, QC, and amendments, updating root documents and status. Authorized, dependency-ready work continues when resources are available.

The [deep-research gate](skills/scientific-research-project/references/deep_research_gate.md) describes the searches, appraisal, and user decisions in steps 3–4. It is an internal operating reference, not a release file. See the [project and result-package schema](skills/scientific-research-project/references/project_schema.md) for deliverable requirements.

### 3.1 Quality requirements for rationale, detailed steps and deep appraisal

The five root documents are not five fill-in forms. Preliminary drafts may contain open choices; the formal design must connect existing evidence, a specific gap, its significance, research steps, the data produced and the claims those data can support or refute.

| Document/stage | Required depth | Insufficient output |
|---|---|---|
| 00_PROJECT.md | Background and closest studies, supporting/contrary findings, precise gap, scientific/practical significance, contribution limits, null-result value, hypotheses and feasibility | A goal paragraph, a few hypotheses, or unsourced claims of importance/novelty |
| 01_PLAN.md | Beyond the roadmap, detailed tasks/substeps with purpose, inputs, full comparison scope, methods/controls/statistics, commands or planned interfaces, output schemas/paths, displays, QC, evidence use and decision branches | A clean–model–validate–report list, software names alone, or only result directories |
| Deep appraisal | Question-specific searching/screening, critical primary-text/method/figure reading, recent and conflicting evidence, method comparison, data feasibility, cross-study synthesis and design decisions | Only the first search page, serial abstract summaries, DOI existence checks, or raw search files not integrated into the design |

Describe each step as action → input → transformation/command → output fields/path → QC → evidence use. Outputs test hypotheses rather than promise to prove a preferred conclusion. Mark unimplemented scripts explicitly; discuss consequential choices instead of inventing parameters and thresholds to fill templates.

Organize evidence matrices, closest-study/gap comparisons and method/data feasibility first, then write a coherent rationale and detailed protocol. Before approval, substantively review specific deficiencies and remedies; do not equate word counts, citation totals or populated fields with depth. New freezing rejects an explicitly preliminary/incomplete or otherwise unready appraisal status while retaining legacy-format compatibility. The program does not assess the adequacy of the reasoning, and existing frozen projects are not automatically revoked.

See the [research-depth protocol](skills/scientific-research-project/references/research_depth.md), [project template](project_template/00_PROJECT.md) and [detailed-plan template](project_template/01_PLAN.md). Revising a template does not rewrite existing projects; frozen designs still require reviewed, approved amendments.

### 3.2 Design influences and acknowledgements: Skills / Agents

| Design source | Principles adopted | Boundaries retained |
|---|---|---|
| [Cheng-I Wu: academic-research-skills](https://github.com/Imbad0202/academic-research-skills), installed academic-research-suite 0.1.15 | Question/method alignment, source verification, cross-study synthesis and critical review | No competing directory system or automatic agent team; no paper vote-counting |
| [K-Dense: literature-review](https://github.com/K-Dense-AI/scientific-agent-skills), installed 1.2 | Staged retrieval, deduplication, screening, full-text extraction and citation verification | No mandatory paid tools, generated images or prestige-based inclusion |
| Host-provided deep-research-work, installed 0.1.15 | Choice-assisted scoping, following evidence leads and comprehensive synthesis | Availability depends on the host; proprietary platform tools/files are not copied |

These identify inspected local versions, not verified latest upstream releases or a completed comparative performance evaluation.

Framework-level design references also include Robin and Google Co-Scientist: research planning, evidence feedback and critical review informed our independently implemented plan-to-result workflow. Section 5 links their original papers and compares their positioning. This does not imply code reuse, official collaboration or superior performance.

The installed academic-research-suite, literature-review and host deep-research informed question/method alignment, staged evidence acquisition, thematic synthesis and critical review in the [research-skill integration policy](skills/scientific-research-project/references/research_skill_bridge.md). Use available providers for bounded stages; otherwise use this project's self-contained protocol, without requiring an entire additional framework.

This framework retains ownership of goals, five root documents, approval, task paths and scheduling. External skills must not create competing master plans or output trees. Separate passes by one Agent are not independent multi-agent review. No third-party source, prompt or template is copied: the observed ARS license has a noncommercial condition, and attribution alone cannot establish permission to redistribute other material. See the [bilingual comparison/provenance record](sources/RESEARCH_SKILL_COMPARISON.md) for sources, versions, file hashes and adoption decisions.


### 3.3 Where does the central scientific evidence come from?

Every project's `00_PROJECT.md` must answer this directly; readers should not have to infer it from dozens of references or appendices. Core evidence is the measurement, comparison or derivation that distinguishes the main hypothesis from competing explanations, not necessarily the largest dataset or most prestigious publication.

| Evidence layer | Required source and purpose | Distinctions to preserve |
|---|---|---|
| Prior scientific basis | Primary study, data accession/version, exact methods and figure/table location; supports significance and method selection | Reviews, search snippets and Skill acknowledgements do not replace primary scientific evidence |
| This project's decisive evidence | Actual inputs, independent units, critical measurements, controls, task/run and result tables/figures; directly tests the central hypothesis | Unexecuted work is planned, not observed; reanalysis must still acknowledge externally collected data |
| Independent validation and counterevidence | Independent samples/cohorts, orthogonal endpoints, negative controls and contrary findings; tests claim boundaries | Two papers using the same samples are not automatically independent; association does not directly establish mechanism |

In 00, map claim/question → primary source → measurement and independent unit → decisive comparison → task in 01 → result table/figure → supported and unsupported inference. Detail evidence acquisition in 01 and data access/version records in 03. After execution, the corresponding result package supplies actual denominators, failures/exclusions, effects and uncertainty. Evidence reviews primarily use extracted primary-study findings; simulation and theoretical projects state assumptions and proof boundaries rather than invent experimental data.

The Agent must explain which conclusions and tasks change if the strongest evidence is missing, a control fails, or the observation is contrary. Label external findings, project observations and Agent inference separately. See the [core-evidence protocol](skills/scientific-research-project/references/core_evidence.md). These are writing and review obligations, not scientific-validity guarantees provided by hashes or automated checks.

## 4. Responsibilities of the Skill and Supervisor

| Component | Responsibility and boundary |
|---|---|
| Core Skill | Guide execution from the plan, maintain task-to-result correspondence, produce reports, and interpret scientific meaning |
| Supervisor CLI | Inspect intake, project, task, and report structure; a single inspection does not start background execution |
| Resident Supervisor | Dispatch configured dependency/resource-ready contracts, track jobs, validate artifacts, and manage retries |
| Analysis, report, and interpretation workers | Invoke domain tools and generate tables, figures, Word, and interpretation; require real commands, environments, and access |
| Project events and status | Connect tasks, runs, and evidence; record failures/amendments and maintain human-facing entry points |

File existence, keyword, and Skill-format checks do not establish scientific correctness. Completion requires actual evidence and review.

## 5. Comparison with Robin and Co-Scientist

This compares organizational emphasis, not performance. Robin includes data analysis and experimental feedback and should not be described as only generating hypotheses. The project column describes this repository's protocol and implementation boundaries.

| Dimension | This project | Robin | Google Co-Scientist |
|---|---|---|---|
| Organizing objective | Execute a research plan and deliver traceable results step by step | Connect literature, hypotheses, experimental data analysis, and updated hypotheses | Generate, critique, and improve hypotheses toward a research objective |
| Human-facing entry points | Five root documents; one result directory and report per planned task | The paper presents experimental plans, analyses, and feedback iterations | The paper presents research proposals and hypothesis iterations |
| Scientific feedback | Compare results with expectations and literature to continue, supplement, or amend | Update hypotheses using experimental findings | Refine hypotheses through multi-agent critique and tournament evolution |
| Format emphasized here | Per-step provenance, methods, results, conclusions, interpretation, figures, tables, and Word | Do not infer that it uses this repository's directory and delivery conventions | Do not infer that it uses this repository's directory and delivery conventions |

Sources: [Robin paper](https://arxiv.org/abs/2505.13400), [Co-Scientist paper](https://arxiv.org/abs/2502.18864). This repository has no direct performance comparison against either system and provides no ready-made integration with them.

## 6. Current execution capabilities and limits

The bundled driver runs **Linux local or SSH-remote user-level systemd jobs**. Hosts need Python, a working user service manager, and task environments; remote hosts also need working SSH access. GPU probing uses `nvidia-smi` for NVIDIA GPU information, which does not establish validation for all accelerator vendors.

| Scope | Current code |
|---|---|
| Local jobs | The driver has local launch/probe paths; the scheduler still requires `host=local` tasks to declare `lightweight: true`. General local GPU-heavy execution is not claimed to be enabled |
| SSH servers | The driver can manage user-level systemd jobs; CPU/GPU resources and task commands require environment-specific verification |
| Containers, Slurm, cloud jobs, and online API scheduling | No bundled dedicated adapters; not listed as current capabilities |

The general documentation does not prescribe H100/V100. `bootstrap_supervisor.py` now requires a reviewed `--hosts` configuration rather than personal server defaults. This release adds design and result-package acceptance, not a new execution backend or hardware compatibility validation.

### 6.1 How workflow requirements are implemented and tested

New projects use `workflow_policy=plan_results_v1`, alongside `execution_policy=v2` for scheduling. This table separates programmatic checks from scientific responsibilities so that an instruction is not mistaken for verified execution.

| README requirement | Current implementation | Acceptance scope and boundary |
|---|---|---|
| Understand the question before drafting | The Skill, default prompt, and Claude adapter require focused dialogue, waiting for answers, and direction confirmation; CLI keywords no longer establish confirmation | Dialogue quality still requires human/behavioral review; the draft tool creates only 00/01 and cannot prove that discussion occurred |
| Discuss and agree after deep research | Before freezing, validate two search routes, hashed search evidence, method comparisons/appraisal, and user-decision records bound to the proposal and appraisal | The program neither searches nor authenticates human identity or assesses research value; the Agent must perform real searches and obtain the decision |
| Map the five documents to the plan | Freeze the version, task manifest, and canonical paths; check design/registry before new dispatch | Unapproved changes hold new work; existing jobs are still reconciled without duplicate submission |
| Execute completely and advance continuously | DAG, resource reservations, phase commands, durable state, and task-local recovery budgets | Requires real domain commands, environments, credentials, and monitoring; no new remote GPU or online AI validation was performed here |
| Deliver a readable package per step | Generate Markdown/Word from one manifest; compare source-table contents, embedded figures, run identity, and complete QC hashes | Supports CSV/TSV summary tables and PNG/JPEG figures; domain workers perform analysis and plotting |
| Interpret and reflect | Check expectations, observations, literature records, alternatives, and next-step decisions; scientific anomalies can hold formal publication | Structural/provenance checks do not establish statistical correctness, faithful graphical encoding, or sound reasoning; scientific review remains necessary |
| Update documents through events | Durable events and idempotent replay update 02/03/04, the task registry, and the result index | Progress does not rewrite frozen 00/01; QC failure creates an amendment draft, while design changes still require reviewed migration |

Regression tests include real small local subprocesses: two dependent tasks run, validate, and interpret; the scheduler is reconstructed between steps; actual Markdown, Word, tables, and figures are generated and checked. Inputs, searches, and approvals are explicitly synthetic fixtures. Resource-driver and monitoring interfaces are isolated substitutes, so this is not an end-to-end acceptance of real research, remote systemd, or an online Agent. See the [workflow execution contract](skills/scientific-research-project/references/workflow_contract.md) for schemas and boundaries.

## 7. Installation and use

### 7.1 Obtain the source

If the repository is not yet cloned:

```bash
mkdir -p "$HOME/git"
git clone https://github.com/shuifeng1988/scientific_agent_design.git "$HOME/git/scientific_agent_design"
```

For an existing checkout, preserve local changes before running `git pull --ff-only`. Develop in the source checkout and run from installed copies. The use of `Path.is_relative_to` requires Python 3.9 or newer; this is a code-level minimum, not evidence that every version has been fully tested.

### 7.2 Install for Codex

```bash
research_source="$HOME/git/scientific_agent_design"
research_skill="$research_source/skills/scientific-research-project"
codex_skill="$HOME/.codex/skills/scientific-research-project"
mkdir -p "$codex_skill"
cp -a "$research_skill/." "$codex_skill/"
```

Adjust the destination if using a custom Codex user directory. Invoke `$scientific-research-project` in a new turn/session; reopen the session if updates are not discovered. Check for independent edits in the installed copy before updating.

If the current installation includes the Skill validator:

```bash
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" "$codex_skill"
```

This validates Skill structure, not scientific analysis, Word generation, or server execution.

#### 7.2.1 Why are an existing PROJECT / PLAN unchanged after reinstallation?

Source updates, installed-copy updates, scientific-document revision and frozen-baseline migration are four different operations. Copying a Skill or restarting the Supervisor does not rewrite existing root documents. `draft` / `freeze` consume content supplied by the Agent; they do not automatically expand a shallow proposal into a detailed scientific design. Templates guide writing rather than automatically rendering existing projects.

First check the actual Skill path/content, then the project's `registry/design.json`, current 00/01 and existing amendment drafts. A passing `check` establishes baseline/hash consistency, not adequate scientific detail. A frozen project needs explicit revision work: preserve original records, write the actual replacement rationale and detailed steps, show differences and unresolved choices, then update the baseline after the required confirmation. Do not delete registries or alter old approval records to bypass checks. There is currently no one-command automatic amendment application.

Explicitly invoke in a new turn in the target project:

```text
$scientific-research-project
Report the actual Skill path read, then use research_depth.md and core_evidence.md
to review this project's 00_PROJECT.md / 01_PLAN.md and existing amendment drafts.
Produce complete replacement drafts, not just a list of suggestions: expand the rationale,
central evidence sources and each step's purpose, data, methods, outputs, QC and evidence use.
Preserve task IDs, existing results and the frozen baseline; reuse the amendment location.
Show differences and decisions that genuinely need my input. Do not overwrite formal
documents or launch new analysis before approved migration.
```

Improve an existing pending amendment instead of repeatedly creating a new “final version.” At handoff, state whether installation was verified, where the draft is, whether formal files changed and why. The updated Skill is available on the next turn; reopen the session if it still reads old rules. Running services use their own script paths, so installation alone does not establish that they were updated.

### 7.3 Install for Claude Code

Run from the target research project root, after checking that the destinations do not contain independent edits:

```bash
research_source="$HOME/git/scientific_agent_design"
mkdir -p .claude/skills/scientific-research-project .claude/agents
cp -a "$research_source/skills/scientific-research-project/." .claude/skills/scientific-research-project/
cp "$research_source/adapters/claude/scientific-supervisor.md" .claude/agents/scientific-supervisor.md
```

Reopen the session and invoke the Skill or Supervisor. This installs instructions and adapter files; the bundled `progress_worker.py` uses Codex CLI, so it does not establish acceptance of a resident Claude worker.

### 7.4 Start research and inspect tasks

#### 7.4.1 Explicit invocation in Codex

Open Codex in the target project and paste the following into the **message input, not a Bash terminal**. Type `$` and select the Skill if the client provides a selector, or explicitly name it. When several research skills are installed, do not rely solely on automatic matching.

A new project may start with an incomplete idea:

```text
$scientific-research-project

I want to study [broad direction], but my question is not yet specific.
Briefly restate your understanding, ask 1–3 focused questions per round,
prefer concise choices with an unrestricted Other/free-text route,
and wait for my answers. Let me reject every option and propose a different direction.
Work with my feedback to clarify the purpose,
focal question, scope, and starting resources.
Do not produce a complete proposal or start analysis before I confirm the direction.
Then draft 00_PROJECT.md / 01_PLAN.md, conduct deep research,
discuss methods with me, and execute only after the formal design is confirmed.
```

Dialogue first is the Skill's default requirement, not a reminder users must supply every time. The first reply should be a brief understanding and questions, not a long checklist, task tree, or report. Continue clarification after the answer rather than treating one response as approval of every design choice. Direction confirmation and post-appraisal formal design approval are separate stages.

For an existing approved project:

```text
$scientific-research-project

Read the five root documents, task registry, and existing approval evidence,
then continue the agreed research plan. Do not repeat answered intake questions
or recompute successfully validated phases.
Use registered task IDs and results paths for provenance, methods, actual commands,
results, conclusions, scientific interpretation, figures, tables, and Word.
Discuss new high-impact ambiguities or design changes with me.
```

Invoke on the next turn after installation/update; reopen the session if old instructions persist. Ask the Agent to report the actual `SKILL.md` path and first-response rule to detect an outdated same-name copy. The repository name `scientific_agent_design` is not the Skill name; installation does not provide a Codex Skill named `$scientific-supervisor`.

Prefer choices plus free text rather than asking users to write a complete specification from scratch. Normally offer 2–3 distinct options per question, include "Not sure yet — help me explore" when useful, and always preserve "Other — describe it yourself." Users may select, briefly elaborate, or reject all options and reframe the question. Do not duplicate a built-in Other/free-text field; respect actual option limits and single/multiple-selection support. A preselected default is not user confirmation. Prefer an available, permitted interactive question tool; otherwise follow interface rules for textual choices or a short open question, without claiming clickable controls exist. For exact targets, file paths, or similar details, ask only for the missing item.

#### 7.4.2 Invocation in Claude Code

This means Claude Code, not ordinary Claude web chat. After installing as in 7.3, invoke in the conversation:

```text
/scientific-research-project I want to study [direction]; clarify it with me in rounds and wait for answers before planning.
```

To use the repository's Supervisor subagent, explicitly name it in natural language:

```text
Use the scientific-supervisor subagent with scientific-research-project.
For a new project, clarify the research purpose first; for an existing project,
check the five root documents and approved plan first.
If the subagent needs my decision, relay concise questions through the main
conversation and wait for my answers. Do not let the subagent approve on my behalf.
```

Use `/agents` to check whether `scientific-supervisor` is recognized. If absent, check `.claude/agents/scientific-supervisor.md` and `.claude/skills/scientific-research-project/SKILL.md` in the current project, then reopen the session. The adapter's `skills` field loads the research Skill into the subagent. Having the source file is not installation and does not start a resident service. See the [Claude Code skills documentation](https://code.claude.com/docs/en/skills) and [subagent documentation](https://code.claude.com/docs/en/sub-agents).

#### 7.4.3 Responsibilities when multiple research skills coexist

| Layer | Entry point | Responsibility |
|---|---|---|
| Overall research protocol | `scientific-research-project` | Intake, planning, five root documents, task-to-package mapping, QC, and interpretation requirements |
| Continuous scheduling | Resident Supervisor; the Claude subagent can help inspect and operate it | Advance approved dependencies within resources; a subagent is not itself a resident process |
| Domain methods | Literature, statistics, RDKit, plotting, Word, and other skills as needed | Produce methods and artifacts for planned tasks without creating a competing master plan |

You may add this project convention to `AGENTS.md` (Codex) or `CLAUDE.md` (Claude Code):

```text
Use scientific-research-project as this project's overall research protocol.
For a new project or unclear scientific direction, discuss in rounds and wait
for answers; draft only after confirmation.
Other skills provide domain methods as needed, without separate master plans
or parallel result directory schemes.
Approved tasks follow 01_PLAN.md and registry/tasks.tsv, preserving full scope.
```

This is a responsibility convention, not a native platform skill-priority mechanism, and it cannot override platform permissions or higher-priority instructions. Do not disable every other research skill; for same-name old copies, inspect the actual loaded path rather than assuming automatic merging. Explanations, installation, and documentation edits are not new research projects and should not trigger scientific intake.

#### 7.4.4 Moving from conversation to execution

After direction confirmation, create the two drafts; establish the five formal documents and registry only after real appraisal and formal design confirmation. `project_template/` is a starting point, not approval. Templates, keywords, and Agent-written summaries are not user consent. The freeze tool installs a portable event hook but does not write domain analysis programs.

After the design is approved, request continuous background progress with:

```text
Inspect and connect this project's resident Supervisor. Reconcile existing
services and jobs first to avoid duplicate launches.
Continuously dispatch ready work within the approved scope and register monitoring.
Report the actual service, running scientific tasks, blockers, and monitoring instructions.
```

Invoking a Skill or Claude subagent does not automatically start resident scheduling. Services, real execution contracts, hosts, permissions, and monitoring still need configuration as in 7.5. The bundled worker uses Codex CLI; do not claim verified end-to-end Claude-driven background execution.

Once project files and the task registry are ready, use these inspection/review commands, replacing the path and task ID:

```bash
research_scripts="$HOME/git/scientific_agent_design/skills/scientific-research-project/scripts"
research_project="/absolute/path/to/project"
python3 "$research_scripts/supervisor_agent.py" intake --root "$research_project"
python3 "$research_scripts/supervisor_agent.py" inspect --root "$research_project"
python3 "$research_scripts/supervisor_agent.py" plan --root "$research_project"
python3 "$research_scripts/supervisor_agent.py" review --root "$research_project" --task-id Q01.01
python3 "$research_scripts/supervisor_agent.py" reflect --root "$research_project" --task-id Q01.01
```

These commands do not automatically write a complete research protocol; `plan` alone does not launch all analyses.

### 7.5 Continuous execution, monitoring, and updates

Follow the [continuous execution contract](skills/scientific-research-project/references/continuous_execution.md) to prepare `registry/supervisor.json`: dependencies, actual commands, environments, hosts, resources, hashes, reporting, and interpretation phases. Configure project hooks, reporting tools, and workers. Installing the Skill alone cannot complete a project without these prerequisites.

```bash
research_scripts="$HOME/git/scientific_agent_design/skills/scientific-research-project/scripts"
research_project="/absolute/path/to/project"
python3 "$research_scripts/supervisor_daemon.py" check --root "$research_project"
python3 "$research_scripts/install_supervisor_service.py" --root "$research_project" --start
python3 "$research_scripts/supervisor_daemon.py" status --root "$research_project"
tail -f "$HOME/.codex/monitor/status.md"
```

`--start` starts the service and ready, authorized tasks. The installer depends on an existing `codex-background-monitor.service`; its implementation is not bundled here, so new machines need compatible monitoring configured first. The installer returns the project service name. Stop scheduling with `systemctl --user stop SERVICE_NAME`; separately inspect already-running remote jobs.

Project progress appears in `04_STATUS.md` and `provenance/supervisor/status.md`. Shutdown stops local scheduling; reconcile original job IDs and outputs before resuming. Persistence after logout depends on user lingering settings. See [failure recovery](skills/scientific-research-project/references/failure_recovery.md).

After updating source, copy the Skill again, verify the installed files, and restart services as appropriate. Services use script absolute paths recorded during installation; updating a different copy does not replace those scripts.

### 7.6 Enable strict plan and result-package acceptance

These commands represent successive workflow stages, not a block to paste and run at once. Prepare the draft JSON using the [workflow execution contract](skills/scientific-research-project/references/workflow_contract.md); prepare proposal, approval, dependency, and host records only after actual research and user confirmation. Never fabricate an approval file to bypass discussion.

```bash
research_scripts="$HOME/git/scientific_agent_design/skills/scientific-research-project/scripts"
research_project="/absolute/path/to/new-project"
python3 -m pip install -r "$research_scripts/requirements-report.txt"
python3 "$research_scripts/research_workflow.py" draft --root "$research_project" --spec "$research_project/provenance/draft.json"
python3 "$research_scripts/research_workflow.py" freeze --root "$research_project" --proposal "$research_project/provenance/proposal.json" --approval "$research_project/provenance/approval.json"
python3 "$research_scripts/research_workflow.py" check --root "$research_project"
python3 "$research_scripts/bootstrap_supervisor.py" --root "$research_project" --dependencies "$research_project/registry/dependencies.tsv" --hosts "$research_project/registry/hosts.json"
```

`bootstrap_supervisor.py` creates only a dependency configuration skeleton; it does not invent runnable research commands. Complete and review the phase contracts before using the checks and startup commands in 7.5. The reporting environment requires `python-docx`; this acceptance used Python 3.13, python-docx 1.2.0, and Pillow 12.0.0 for figure fixtures.

The analysis worker first produces actual tables, figures, and the report manifest, then renders the final reports. Run the second validation command only after the interpretation phase records genuine reflection evidence and refreshes complete QC. Replace the example path with the registered task path; `SCI_RUN_ID` is the Supervisor-assigned run identifier.

```bash
python3 "$research_scripts/research_workflow.py" render --root "$research_project" --task-id Q01.01 --manifest "$research_project/results/Q01_question/Q01.01_analysis/_evidence/report.json"
python3 "$research_scripts/research_workflow.py" validate-package --root "$research_project" --task-id Q01.01 --run-id "$SCI_RUN_ID"
```

Once a final report receipt exists, the tool refuses silent overwrite; batch drafts must not masquerade as final reports. Revisions require preserving previous run evidence and reviewed handling. The program does not invent conclusions, literature, or user approvals.

Existing projects do not automatically gain these new gates. Do not run draft/freeze directly on an existing project: the tool refuses to overwrite its registry and hook. Migration must preserve the original plan, IDs, results, running-job state, and approval records and be reviewed before adoption. Do not delete registries or rerun completed research to bypass checks.

## 8. Repository navigation

```text
README.zh-CN.md                    # Chinese introduction and installation
README.en.md                       # Corresponding English guide
VERSION                            # Current version
skills/scientific-research-project/
  SKILL.md                         # Core operating contract
  references/                      # Deep research, packages, recovery, execution
  scripts/                         # Supervisor, driver, checks, tests
adapters/claude/                    # Claude Agent adapter
project_template/                  # Project document templates
documentation/                     # Existing guides/figures; check their versions
archive/                           # Historical material
```

Existing dated DOCX/PDF documents and figures may reflect earlier designs. Use these two READMEs and the corresponding source for current behavior; historical material is not evidence of newly implemented capabilities.

## 9. Version

Current source version: **0.6.3**, recorded in [`VERSION`](VERSION). Retains choice-assisted intake and deep appraisal, and makes central evidence sources, borrowed research-skill designs and the distinction between installation, complete replacement drafts, review and baseline migration explicit; templates and Supervisor instructions are aligned. New freezes reject explicitly unready appraisal status while retaining compatibility with older records lacking that field. Substantive research quality requires actual search and review; status/schema checks cannot guarantee it. No execution backend or automatic migration command is added, and installation updates do not automatically migrate or rerun existing projects.
