# Substantive research design and evidence depth

Read after direction confirmation, before composing the appraisal and final 00_PROJECT.md / 01_PLAN.md. This specifies scientific writing and review obligations, not a semantic validator. Keep the concise choice-assisted intake separate: do not overwhelm the first reply with these checklists.

Read core_evidence.md and make the central claim-to-evidence map explicit in 00/01. The most important evidence must be identifiable without searching all appendices.

## 1. 00_PROJECT.md must explain why the study matters

Write a connected argument supported by identifiable sources, not a slogan or a table of task names:

1. **Problem and context:** who faces what scientific or practical uncertainty, under which conditions, and why existing knowledge is insufficient. Define key concepts and the intended decision.
2. **State of the evidence:** synthesize established findings, the closest existing studies, recent developments, disagreements and methodological limitations. Cite the specific claims; distinguish primary findings, reviews, preprints and the Agent's inference. Link to the detailed appraisal but keep the central reasoning in 00 itself.
3. **Precise gap:** for each gap identify the closest prior evidence, what it actually established, what remains unresolved and why. A different model or dataset alone does not demonstrate a meaningful gap. Unavailable access is not evidence that no research exists.
4. **Significance:** explain the scientific knowledge gained, practical decision improved and/or methodological contribution. Use only applicable categories with justification. Explain why the gap is consequential, why now, who could use the result, and whether a negative/null result would still be informative.
5. **Contribution and boundaries:** compare proposed outputs with the nearest studies. Explicitly label replication, robustness testing, extension, integration or a genuinely new hypothesis. Do not claim novelty from search absence or promise a positive result.
6. **Objectives and questions:** separate the overall goal from specific Q IDs. Give testable hypotheses, plausible nulls and competing explanations, or explicit exploratory questions where hypotheses are inappropriate. State the applicable population, unit of analysis, scope and non-goals.
7. **Evidence strategy:** map each question to the studies/controls that could answer it, the critical assumptions and the type of evidence expected. Distinguish prediction, association, mechanism and causality; observational comparisons alone do not establish a causal mechanism.
8. **Feasibility and value:** data access, sample/measurement adequacy, licensing/ethics, methods, resources, risks, reasonable alternatives and stop/go conditions. Explain why the proposed information gain justifies the cost without fabricating budgets or durations.
9. **Deliverables and limitations:** identify human-readable and machine-readable outputs, intended use and limits of generalization. Link each question to planned task/result locations. Put actual results in results/, not in a proposal's expected-outcome section.

Use a compact gap-to-evidence table where helpful:

| Q ID | Closest evidence and limitation | Unresolved question | Why it matters | Planned distinguishing evidence | Claim boundary |
|---|---|---|---|---|---|

Do not pad every row with a citation that supports only background. Explain the inferential step from prior work to the proposed gap. A project can be worthwhile as a careful replication; novelty is not mandatory.

## 2. 01_PLAN.md is an executable scientific protocol, not just a task list

Start with a roadmap and dependency overview; then write a detailed card for EVERY planned task. A summary table indexes the cards, never replaces them. Decompose a broad task into ordered substeps whenever inputs, transformations, checks or decisions differ. Keep substeps within the same registered task path unless they are independently registered scientific tasks; do not create a parallel numbering system.

Each task card must contain:

| Element | Required scientific and operational detail |
|---|---|
| Purpose | Parent Q, specific uncertainty/hypothesis, why this step is necessary, whether it generates evidence or only prepares an input |
| Dependencies | Exact upstream task/artifact and required QC; independent branches and resource constraints |
| Inputs | Data IDs, source/version/access, unit of observation, required columns/labels, population/sample count or estimation procedure, inclusion/exclusion, missingness and raw-to-analysis transformations |
| Software/models | Complete approved comparison panel with versions, checkpoint/source, role, environment and host; reference 02/03 rather than duplicating inventories |
| Method and rationale | Ordered operations, assumptions, chosen method versus plausible alternatives, controls, parameters, split/leakage rules and seeds as applicable |
| Statistical design | Estimand/primary comparison, analysis unit, effect size, uncertainty, pairing/clustering, multiplicity, meaningful-effect threshold or justification that none is established; power/precision plan where applicable |
| Execution | Script/command or exact procedure, arguments, input/output paths, CPU/RAM/GPU, time budget, dependencies; clearly distinguish verified commands from planned scripts not implemented yet |
| Produced data | Name and format of every critical artifact, row unit/key, required columns, expected dimensions/count checks, provenance, destination within registered results and intended downstream consumer |
| Tables/figures | Planned table columns, figure axes/groups/uncertainty and the question each display answers; do not invent numerical values |
| Evidence interpretation | What observation supports or weakens the hypothesis; what cannot be concluded; alternative explanations and the controls that distinguish them |
| QC and failure | Objective checks/thresholds justified before results, allowable technical recovery, exclusions requiring review, invalid versus scientifically null outcomes |
| Branches and completion | Actions for supportive, null, contradictory and inconclusive results; affected dependents; formal package/acceptance criteria and required human decisions |

Substep format: **action → inputs → transformation/command → output schema/path → QC → evidence use/next consumer**. Do not collapse data acquisition, preprocessing, model fitting, evaluation and interpretation into “perform analysis.” A software invocation must not substitute for a methods description.

Granularity test: could another qualified researcher execute or implement the step without inventing a scientifically consequential choice? If not, either expand it or explicitly mark the unresolved decision. During preliminary planning, assumptions and options may remain open. Before scientific design freeze, resolve choices that alter the estimand, cohort, comparator, endpoint or inferential validity with the user. Technical paths/scripts may remain planned if attached to concrete implementation tasks; no node is runnable until actual contracts and verification exist.

Expected output is not an expected positive result. Explain what a table is meant to test, not that it will “prove our method is superior.” Preserve the value of null findings and retain unsuccessful observations in the approved denominator. Add a useful discriminator/control only within authorized scope; discuss changes in scientific scope or cost.

## 3. Deep-research synthesis must change the design

Follow deep_research_gate.md for actual searching and evidence acquisition. Deliver an integrated appraisal, not a bibliography plus generic prose. The reader must be able to trace:

**source finding → limitation/conflict → unresolved Q → chosen method/control → planned data/figure → permissible inference**.

For each important methodological choice cite the evidence or methodological rationale, explain alternatives and practical feasibility, and state why the chosen design is informative. Record decisions revised after finding contradictory or newer evidence. If the appraisal leaves the initial generic plan unchanged, explain why the evidence supports that plan rather than claiming research automatically added value.

Keep 00 as the readable argument, 01 as the detailed protocol, 02/03 as software/data catalogs and 04 as status. Preserve one linked appraisal and supporting source/search/method tables in project provenance (reuse existing locations). Do not create additional root entry points or dozens of duplicative “final” reports.

## 4. Substantive review before presenting the final plan for approval

Use the bounded method-provider and four-pass review guidance in research_skill_bridge.md. Review remains necessary even when an external Skill produced the report; neither its reputation nor its successful process exit establishes adequate science.

Record a concise review in the appraisal's existing evidence directory, bound to the exact proposed documents by path/hash. This is a scientific review record, not a new substitute approval file. For each criterion report **adequate / revise / needs_user**, point to the actual section/table/source and explain the reasoning:

- Importance is supported by concrete consequences, not “important and innovative.”
- Closest prior studies are compared and gaps are accurately bounded.
- Recent and contradictory evidence has been examined, or its access/search limitations are explicit.
- Each Q maps to tasks capable of answering it and distinguishing alternatives.
- Central claims name their decisive sources, measurements, independent units and controls, with planned versus verified availability and task/result locators; borrowed Skills are not scientific sources.
- Every task/substep has purpose, input, method, output and evidence use; no orphan outputs or unexplained analyses.
- Controls, uncertainty and failure policy prevent foreseeable overinterpretation.
- Planned methods are feasible or have explicit readiness tasks; unverified commands are not called tested.
- The report separates supporting, null, contradictory and inconclusive findings and defines their downstream implications.

Revise inadequate content before asking the user to approve a formal plan; ask focused, choice-assisted questions for unresolved high-impact decisions. Missing literature access means an incomplete appraisal with stated consequences, not a fabricated pass. Do not use page counts, number of papers, keyword checks or passing schema tests as proof of depth. The existing CLI validates records/hashes, not these scientific judgments. Existing frozen projects require reviewed amendments; do not rewrite their scope to retrofit this protocol.

## 5. Reassessing an existing project after a Skill update

When the user asks to improve an existing thin project/plan, inspect the actual installed Skill path/content, current 00/01, design baseline and existing amendment/appraisal records. Do not infer that an unchanged document means installation failed, or that frozen means scientifically adequate. Avoid reading other session journals unless requested.

Distinguish four operations: source update, installation update, scientific-document revision, and approved baseline migration. A resume/daemon restart performs none of the latter automatically. Templates guide the writing Agent; draft/freeze consume supplied content and do not expand a shallow proposal by themselves.

For an authorized revision, reuse the existing amendment location and produce actual proposed replacement 00/01 content with detailed task cards and a claim-to-evidence map, plus a concise old-to-new difference summary. A list of proposed changes alone is not the revised project/plan. Preserve task IDs, result paths, completed evidence and unresolved choices. Keep the current baseline untouched until any required approval and deliberate reviewed migration; the CLI has no automatic amendment-apply command. Do not manufacture approval, rewrite receipt hashes to hide drift, or run freeze on top of an existing registry.

Report explicitly: installed path/hash, current approved version, where the replacement draft is, what remains to be decided, and whether the root documents changed. Link the draft in the project's existing status/amendment area without modifying frozen content. If the current request is only framework installation/documentation, explain this separation rather than silently revising another project's science or starting its jobs.
