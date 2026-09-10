# Deep-research gate before scientific planning

This gate is mandatory after intake and before freezing a new scientific plan.

Do not start this gate directly from a vague opening prompt. First complete the focused dialogue and direction confirmation in [intake_protocol.md](intake_protocol.md). An initial scientific idea, automatic Skill activation, or generated 00/01 text is not evidence that the user has confirmed the direction. Keep pre-appraisal direction agreement separate from post-appraisal design approval.

1. Restate the decision, population, hypotheses, and decision-changing outcomes.
2. Search at least two scholarly routes (PubMed, Crossref/OpenAlex, domain databases, and official repositories). Record dates, exact queries, inclusion/exclusion rules, and a 24–36 month recent-work cutoff. Prefer primary papers, benchmark papers, official code/checkpoints, and dataset documentation.
3. Map positive, null, negative, and conflicting evidence: task, cohort, leakage controls, split, comparator, endpoint, uncertainty, compute, availability, license, reproducibility, and independent validation.
4. Compare conventional strong baselines, current reproducible baselines, and frontier candidates, including expected gain, assumptions, failure modes, confounders, cost, and fallback.
5. Assess significance, novelty, decision relevance, information gain, data sufficiency, reproducibility, compute/transfer feasibility, licensing, and null-result value. Produce go/no-go or staged recommendations.
6. Draft hypotheses, data versions, models, splits, metrics, statistics, QC, failure/exclusion rules, resources, stopping criteria, dependencies, and artifact/report paths.
7. Discuss high-impact choices with the user before freezing the plan; preserve decisions, uncertainty, dissent, and amendments.

Prepare a human-readable appraisal covering the evidence, method options and decisions required, with source/search evidence under project provenance. The implemented machine contract is `appraisal.json` (searches, source records, method tiers and appraisal), the exact proposed five documents/tasks, and a separate user-decision receipt. See [workflow_contract.md](workflow_contract.md) for fields. Existing APPRAISAL.md, METHOD_OPTIONS.md and source tables may be retained as evidence; do not create redundant parallel summaries merely for filenames.

The freeze command verifies at least two recorded search routes, hashed search evidence, all appraisal/method fields, and user approval bound to both proposal and appraisal hashes before establishing the baseline. It then journals research.appraisal.completed and research.appraisal.discussed receipts. These receipts record the prior appraisal/discussion; the command does not perform the searches or obtain approval. An operator must preserve actual user-message evidence and must never manufacture it. Literature is context, never silently imported project results.

## Depth and coverage: two routes are a floor, not completion

Before choosing research tools, read research_skill_bridge.md. Reuse suitable installed research capabilities within the approved scope and preserve source/claim, cross-study and evidence-to-decision review. Do not create a second project workflow or assume a provider is installed. The self-contained procedure below remains the fallback.

Before searching, translate the confirmed question into explicit coverage axes: closest prior work/theory, mechanisms and competing explanations, intervention/negative evidence, measurement/analysis methods, data availability, and practical significance. Adapt the axes to the discipline; do not assume every study is a model benchmark. Map each axis to queries, dates, sources and unresolved questions. Search methods and software separately from biological or application findings.

Perform targeted searches, not just one broad keyword query and one DOI lookup. A bibliographic lookup verifies identity; it is not an independent substantive survey. For large result sets, page/screen where feasible or refine by question, intervention, population and method; record retrieved, screened and included counts separately. A first page of results cannot establish coverage of a field. Explain budget/time/access limits and obtain direction if those prevent the requested depth.

Read the primary evidence behind design-changing claims: methods, sample/replicate units, controls, endpoints, key figures/tables and supplements when needed. Record a section/figure/table locator and whether full text, an abstract, repository documentation or only metadata was accessible. A search snippet is discovery evidence, not a full-paper review. Trace reviews to primary work; distinguish exploratory claims, replication and experimentally supported causality. Check corrections/retractions for critical studies.

For recent progress, use the actual search date, a justified recent window (often 24–36 months) and a final focused update for the latest relevant papers, preprints, code and dataset releases. Retain foundational work. Record publication/online dates and preprint status instead of claiming "latest" from memory. Follow references and citing work around the closest studies when accessible; explicitly search for null, contradictory and replication evidence.

## Evidence extraction and synthesis

Use core_evidence.md to identify the decisive evidence for each central claim, not just a broad bibliography. Separate primary background evidence, planned project measurements/comparisons, independent validation and contrary evidence. Optional Skill sources document methods borrowed by the framework, not evidence for a scientific hypothesis.

Keep supporting tables alongside ONE human-readable appraisal in the existing provenance location:

- **Evidence matrix:** source ID/link/date/type/access depth; study question/design; population and independent sample units; intervention/comparator; measurements/endpoints; principal finding and uncertainty as reported; exact evidence locator; limitations/confounding; what it supports, what it cannot establish, and which project Q it informs. Mark unreported values unknown; never fabricate them.
- **Closest-study/gap matrix:** what the closest work already did, overlap with this proposal, remaining gap, whether it matters, and the exact distinguishing analysis. Distinguish new discovery, extension and valuable replication.
- **Method comparison:** conventional strong methods, current reproducible methods and relevant frontier candidates; assumptions, input needs, statistical suitability, leakage/confounding risks, code/version/license/data availability, estimated resources with basis, expected information gain and reasons for choosing/rejecting them. A list of tool names is insufficient; absence of a feasible frontier method is acceptable if documented.
- **Data feasibility:** accession/source/version, processed versus raw availability, independent units/group structure, required measurements/metadata, missingness, overlap, access/license and actual verification level. A repository HTTP response is not proof that the data support the planned inference.
- **Design consequences:** every major hypothesis/method/control links to supporting/conflicting evidence and states what changed or was retained after appraisal, why, and which decision requires the user.

Synthesize agreement and conflict across studies rather than summarizing papers serially. Explain whether apparent contradictions follow from population, intervention, timing, outcome definition, bias, or genuine uncertainty, without automatically dismissing contrary results. Separate what is established, plausible, unsupported and currently unidentifiable. Evaluate scientific/practical significance, novelty boundaries, feasibility and null-result value using research_depth.md.

## Completion and version integrity

Stop when decision-critical coverage axes and closest alternatives have been addressed, the remaining uncertainty is explicit and the proposed design can be justified—not when a paper quota or two successful tool calls is reached. State the search stopping rationale and outstanding blind spots. If critical evidence remains unavailable, call the appraisal preliminary/incomplete and explain its effect on the plan.

New appraisal records should use status `preliminary`, `incomplete`, or `ready_for_design_review` accurately. A ready status requires a substantive review as in research_depth.md; it is not user approval. The new-freeze code rejects an explicitly declared status other than `ready_for_design_review` or legacy `complete`. It still accepts missing status for legacy schema compatibility; this does not authorize a worker to omit the field to evade the rule. Previously frozen baselines are not retroactively rewritten or revoked.

When deeper searches have been performed, integrate them into the human appraisal and its evidence matrix; update the machine appraisal references/hashes too. Do not leave a new raw-search directory unlinked while freezing an older preliminary appraisal. Preserve old versions, show material changes to the user and bind the subsequent decision to the actual final proposal/appraisal. Approval to explore or prepare files is not approval of a later, unseen scientific design. A schema/hash pass does not establish that sources were read deeply or the reasoning is sound.
