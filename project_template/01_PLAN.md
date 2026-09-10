# Detailed scientific research plan

_Drafting guide, not a ready protocol. Write in the user's language. Keep the roadmap concise, but complete a task card and ordered substeps for every planned task. Early drafts may show open choices; formal approval must resolve consequential scientific decisions. Unimplemented scripts remain explicitly planned._

## 1. Design overview and roadmap

Link the approved purpose and Q IDs in 00_PROJECT.md. Explain the overall evidence sequence, complete comparison scope and shared design assumptions.

| Task ID | Parent Q | Specific purpose | Depends on | Input IDs | Critical output/evidence | Registered result path |
|---|---|---|---|---|---|---|
| Q01.01 | Q01 | [Uncertainty addressed or readiness purpose] | [IDs/artifacts] | [Data/software IDs] | [What is produced and tested] | results/Q01_question_slug/Q01.01_task_slug/ |

The table is an index, not the protocol. Repeat section 3 for every task. Technical substeps stay within the parent result path; separately register independently reportable scientific tasks.

## 2. Shared scientific and statistical design

Define populations, inclusion/exclusion, independent analysis units, controls/comparators, primary/secondary endpoints, split/leakage protections, seeds, uncertainty/multiplicity and pre-specified sensitivity analyses where relevant.

State the meaningful effect/decision criterion or why one cannot yet be justified. Distinguish technical invalidity, low precision, scientific null findings and actual contradictory evidence. Do not invent thresholds or use outcomes to redefine success.

## 3. Task Q01.01 — [specific scientific action]

### Purpose and evidence role

Parent question: Q01. Explain the uncertainty or hypothesis addressed, why this step is needed and whether it creates scientific evidence or only a prerequisite. Specify what it can support/refute and what cannot be inferred.

Link the central claim/evidence row in 00_PROJECT.md. Name its primary source and decisive measurement/control, whether this is discovery, independent validation or counterevidence, and the exact planned result table/figure. State sample reuse, inferential limits and missing-evidence consequences. At completion replace planned availability with observed QC and real result locators; never present a literature finding as a new project result.

### Inputs and prerequisites

List exact upstream artifacts and their required QC; data IDs/source/version/access, sample unit, selection, necessary columns/labels and expected counts or a count-audit method. Reference 03_DATA.md. List all approved software/models, role, version/checkpoint, host and environment from 02_SOFTWARE.md; do not shrink the panel to convenient models.

### Methods, controls and rationale

Describe operations precisely enough for another researcher to implement them without inventing an important scientific choice. Define transformations/formulas, model fitting and selection, covariates, controls, uncertainty, comparison tests and alternatives as applicable. Explain why these methods answer the question.

### Ordered substeps

| Local substep | Purpose | Input | Transformation/procedure | Output and path | QC/decision | Evidence use or next consumer |
|---|---|---|---|---|---|---|
| 1 | [Audit prerequisites] | [Exact source/metadata] | [Check units, labels, availability and correspondence] | [Artifact/schema] | [Declared acceptance rule] | [Determines analysis eligibility, not a biological conclusion] |
| 2 | [Prepare analysis input] | [Validated artifact from 1] | [Defined transformation, parameters and exclusions] | [Artifact/schema] | [Counts, keys, missingness and leakage checks] | [Input for the specified comparison] |
| 3 | [Estimate or compare] | [Frozen analysis input] | [Exact method, controls and uncertainty] | [Estimates/predictions/schema] | [Model/measurement validity checks] | [Tests stated hypothesis against alternative] |
| 4 | [Interpret and package] | [Validated estimates and sensitivity results] | [Planned contrasts, displays and interpretation] | [Tables, figures, README, REPORT.docx] | [Evidence linkage and scientific review] | [Parent Q and downstream decision] |

Adapt or expand these example substeps; do not copy them as generic prose for every study. Separate operations whenever inputs, methods, outputs or decisions differ.

### Execution and resource contract

Record actual commands/procedure, arguments, input/output paths, environment activation, host, CPU/RAM/GPU, estimated runtime basis and limits. Reference versioned scripts where appropriate.

If code is not implemented, explicitly state its intended interface and implementation/verification task; do not label invented commands runnable or tested. Before dispatch, actual phase contracts, source/input hashes and minimal verification are mandatory.

### Produced data and planned displays

| Artifact under the registered result path | Format and row unit/key | Required columns/dimensions | Source/transformation | Scientific use or downstream consumer |
|---|---|---|---|---|
| [Relative artifact path] | [CSV/TSV/array/etc.; observation unit and unique key] | [Names/types and expected count checks] | [Substep/input provenance] | [Exact uncertainty addressed] |

For each table specify comparison columns, denominators and uncertainty. For each figure specify axes, grouping, uncertainty and what it lets the reader assess. These are intended outputs, not fabricated values or promised favorable findings.

### QC, interpretation and decision branches

| Outcome | Pre-specified interpretation | Permissible next action |
|---|---|---|
| Valid evidence supports the hypothesis | [Supported claim and its scope] | [Named ready dependent or corroboration] |
| Valid null/weak evidence | [No detectable effect versus sufficient evidence of little effect] | [Retain result; follow precision/stop rule] |
| Contrary evidence | [Which hypothesis/assumption is weakened] | [Discuss consequential revision; no post-hoc endpoint change] |
| Technical failure/inconclusive evidence | [Why the scientific question remains unanswered] | [Bounded technical repair or focused user decision] |

Specify objective QC, failed-row handling, approved exclusions and stopping rules. Preserve evidence, diagnose, remedy, minimally verify and resume only failed phases. Unknown remote status never authorizes duplicate launch.

### Completion

A formal scientific task requires its registered README.md, REPORT.docx, tables, figures, run-bound QC, interpretation and evidence hashes, followed by the project hook. A technical artifact may release subsequent computation after its own approved validation but does not complete the parent scientific question.

## 4. Dependencies and continuous execution

Maintain registry/task_dependencies.tsv and registry/supervisor.json with all approved tasks/technical children, resource limits, actual phase contracts and hashes. Link their generated runtime status from 04_STATUS.md; do not write changing status tables into a frozen 01_PLAN.md.

Dispatch independent authorized branches when inputs and resources permit. A failed report or blocked scientific choice holds affected dependents, not unrelated computation. The final synthesis waits for complete eligible evidence or explicitly reviewed exclusions. Per-task/phase recovery budgets follow failure_recovery.md, not a project-wide retry cap.

## 5. Substantive review and amendments

Before requesting final approval, check every task for purpose → data → method → output → evidence use, feasible controls and informative alternatives, using the Skill's research_depth.md. Link the review to the exact proposal version. Missing consequential choices require discussion; generic headings are not completion.

For an amendment record the triggering evidence, affected questions/tasks, changes in methods/resources/inference, user decision and versioned diff. Do not silently rewrite a frozen design or replace unsuccessful outcomes.
