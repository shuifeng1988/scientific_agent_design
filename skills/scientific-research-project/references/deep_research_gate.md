# Deep-research gate before scientific planning

This gate is mandatory after intake and before freezing a new scientific plan.

1. Restate the decision, population, hypotheses, and decision-changing outcomes.
2. Search at least two scholarly routes (PubMed, Crossref/OpenAlex, domain databases, and official repositories). Record dates, exact queries, inclusion/exclusion rules, and a 24–36 month recent-work cutoff. Prefer primary papers, benchmark papers, official code/checkpoints, and dataset documentation.
3. Map positive, null, negative, and conflicting evidence: task, cohort, leakage controls, split, comparator, endpoint, uncertainty, compute, availability, license, reproducibility, and independent validation.
4. Compare conventional strong baselines, current reproducible baselines, and frontier candidates, including expected gain, assumptions, failure modes, confounders, cost, and fallback.
5. Assess significance, novelty, decision relevance, information gain, data sufficiency, reproducibility, compute/transfer feasibility, licensing, and null-result value. Produce go/no-go or staged recommendations.
6. Draft hypotheses, data versions, models, splits, metrics, statistics, QC, failure/exclusion rules, resources, stopping criteria, dependencies, and artifact/report paths.
7. Discuss high-impact choices with the user before freezing the plan; preserve decisions, uncertainty, dissent, and amendments.

Prepare a human-readable appraisal covering the evidence, method options and decisions required, with source/search evidence under project provenance. The implemented machine contract is `appraisal.json` (searches, source records, method tiers and appraisal), the exact proposed five documents/tasks, and a separate user-decision receipt. See [workflow_contract.md](workflow_contract.md) for fields. Existing APPRAISAL.md, METHOD_OPTIONS.md and source tables may be retained as evidence; do not create redundant parallel summaries merely for filenames.

The freeze command verifies at least two recorded search routes, hashed search evidence, all appraisal/method fields, and user approval bound to both proposal and appraisal hashes before establishing the baseline. It then journals research.appraisal.completed and research.appraisal.discussed receipts. These receipts record the prior appraisal/discussion; the command does not perform the searches or obtain approval. An operator must preserve actual user-message evidence and must never manufacture it. Literature is context, never silently imported project results.
