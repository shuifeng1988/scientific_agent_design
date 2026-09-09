# Deep-research gate before scientific planning

This gate is mandatory after intake and before freezing a new scientific plan.

1. Restate the decision, population, hypotheses, and decision-changing outcomes.
2. Search at least two scholarly routes (PubMed, Crossref/OpenAlex, domain databases, and official repositories). Record dates, exact queries, inclusion/exclusion rules, and a 24–36 month recent-work cutoff. Prefer primary papers, benchmark papers, official code/checkpoints, and dataset documentation.
3. Map positive, null, negative, and conflicting evidence: task, cohort, leakage controls, split, comparator, endpoint, uncertainty, compute, availability, license, reproducibility, and independent validation.
4. Compare conventional strong baselines, current reproducible baselines, and frontier candidates, including expected gain, assumptions, failure modes, confounders, cost, and fallback.
5. Assess significance, novelty, decision relevance, information gain, data sufficiency, reproducibility, compute/transfer feasibility, licensing, and null-result value. Produce go/no-go or staged recommendations.
6. Draft hypotheses, data versions, models, splits, metrics, statistics, QC, failure/exclusion rules, resources, stopping criteria, dependencies, and artifact/report paths.
7. Discuss high-impact choices with the user before freezing the plan; preserve decisions, uncertainty, dissent, and amendments.

Required artifacts under the registered provenance path: `APPRAISAL.md`, `sources.tsv` or `.json`, `METHOD_OPTIONS.md`, `DECISION_REQUIRED.md`, and `evidence_hashes.json`. Emit `research.appraisal.completed` only after validation and freeze only after `research.appraisal.discussed`. Literature is context, never silently imported project results.
