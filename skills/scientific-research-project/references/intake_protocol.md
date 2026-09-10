# Project intake protocol

The Supervisor must understand the user's actual scientific purpose before freezing a plan. It should ask concise grouped questions and show a draft understanding for correction.

## Mandatory conversational entry

Apply to a new project or a materially unclear new scientific direction, not to documentation work, a factual explanation, or resumption of an unchanged approved task.

1. Read the actual request and relevant user-supplied context. Identify what is known, what is inferred, and which ambiguity would change the study. Do not import another project's purpose from old conversations.
2. First reply: briefly restate your tentative understanding; ask 1–3 focused questions about the intended decision, focal research question, or available starting evidence. End the turn and wait. Do not append a full proposal or issue searches, file-generation, delegation, download, or compute actions for the new study while waiting.
3. After the answer, explain your updated understanding, probe contradictions and useful alternatives, and ask only the next necessary questions. Avoid a ten-field questionnaire and do not re-ask answered questions. Offer concrete examples when the user cannot yet formulate a precise question; label suggestions as possibilities, not decisions. A narrowly authorized terminology/source check can help the dialogue but does not authorize the full appraisal or analysis.
4. When enough is known, present a short direction summary: purpose/decision, focal question, scope/non-goals, existing data/resources, intended useful output, and unresolved items for research. Ask the user to confirm or correct it and wait. Preserve their actual confirmation/corrections before drafting. If they have already explicitly confirmed that exact summary, do not ask again. Do not infer consent from silence or from a vague prompt.
5. Only then create preliminary 00/01 and conduct the deep-research gate. Discuss its findings and method choices before obtaining the separate final-plan approval and freezing. Direction agreement is not approval of yet-unseen methods, costs, or compute.

Intake is sufficient for appraisal when the purpose, focal question, scope, starting evidence/resources (including known absence), and desired outcome are mutually understood. Exact metrics, model choices, sample sizes, and statistical designs may remain open for appraisal; never invent them to fill every field. No fixed number of dialogue rounds is required, but an ambiguous opening must receive a real user-response opportunity.

Example (illustrative, not a scientific recommendation): User: "I want to study AI for drug discovery." First response: "That could mean evaluating prediction methods or finding candidates for a specific target. Which outcome matters to you? What target, data, or previous results do you already have?" Then stop. Do not immediately choose a disease, dataset, panel, or twelve-step experiment.

An autonomous/noninteractive worker cannot conduct this exchange: return a scoped needs_user hold with concise questions for the outer operator. Human waiting is not a technical failure or a reason to spend repair attempts. Do not use subagents to manufacture user answers. Existing approved tasks and unrelated ready branches retain their authority.

## Choice-assisted questions

- For each question, normally suggest 2–3 short, meaningfully different answers. Use plain language and add at most a sentence explaining a choice's practical consequence. Follow the interface's actual option limits. Do not turn the 1–3 questions into bundles of many subquestions.
- Always preserve an unrestricted route: "Other — describe it in your own words." If the question tool already supplies Other/free text automatically, do not add a duplicate option. A user may reject every suggestion, combine compatible choices, or propose a wholly different direction. Retain that answer as given and ask focused follow-ups instead of coercing it into your categories.
- Include "Not sure yet — help me explore" when the user is still forming an idea; it is not equivalent to consent to the first option. Distinguish single choice from multiple choice, respecting the actual UI. Never silently submit or treat a preselected choice as the user's decision.
- Prefer the host's permitted interactive choice/question tool. If unavailable, use lettered choices in the conversation only when that interface permits it, with Other/free text explicit. Do not claim clickable buttons exist in plain text. If higher-priority interface rules forbid textual choices, use the supported free-text question instead; never bypass those rules.
- Ask open text for inherently specific details (such as an exact research target, file path, or the user's own alternative), but ask only the missing detail, not for an entire research proposal. Recommendations must have a stated basis, not steer an undecided user toward the Agent's favorite field or easiest experiment.

Example first question: "What would be most useful as your main outcome? A. Compare existing methods on common data. B. Answer a specific biological question using AI. C. Not sure yet; help me explore. Other: describe a different outcome." This is an illustrative textual fallback, not an assumption about the user's domain or a requirement to show four options in a UI limited to three. After selection, tailor the next round; do not deliver the whole plan.

## Intake field checklist (for the Agent, not a first-turn questionnaire)

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

After the dialogue, intake produces a concise brief with answered fields, unresolved high-impact questions, assumptions, actual user decisions, and the next approval needed. A proposed Q/task tree belongs to the subsequent draft, not the first clarification reply. Reuse the project's provenance/decision records rather than adding redundant root documents. The CLI's keyword inventory is only a diagnostic aid; it cannot establish dialogue quality or user consent. Intake does not launch downloads or compute jobs.
