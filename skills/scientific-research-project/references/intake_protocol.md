# Project intake protocol

The Supervisor must understand the user's actual scientific purpose before freezing a plan. It should ask concise grouped questions and show a draft understanding for correction.

## Required intake fields

1. Decision: what scientific or practical decision should the project support?
2. Objective: what must be demonstrated, compared, predicted, or ruled out?
3. Scope: which biological/chemical population, modalities, models, datasets, servers, and time/version boundary are in scope?
4. Hypotheses: expected direction, plausible null result, and competing explanations.
5. Endpoints: primary endpoint, secondary endpoints, metrics, aggregation, and what must not be combined.
6. Eligibility: complete eligible model list, controls, exclusion rules, missingness policy, and audit denominator.
7. Design: split, leakage control, seeds, power/uncertainty, external validation, and stopping rules.
8. Operations: software/checkpoint versions, environment, host/GPU, budget, parallelism, and runtime limits.
9. Deliverables: tables, figures, Markdown, Word, manifests, hashes, and the audience's required level of detail.
10. Communication: what requires user approval, what the Supervisor may add autonomously, and reporting cadence.

## Communication gate

- If a missing answer could change the goal, cohort, primary endpoint, eligibility, or interpretation, stop and ask the user.
- If the missing answer affects only implementation detail with a safe default, state the assumption and continue.
- Before freezing, present a short interpretation of the goal and a task outline for user correction.
- Preserve the user's corrections as a dated decision in provenance/decisions.tsv or a plan-amendment record.

## Output

intake produces an auditable brief with answered fields, unresolved high-impact questions, assumptions, proposed Q/task tree, and the next approval needed. It does not launch downloads or compute jobs.

