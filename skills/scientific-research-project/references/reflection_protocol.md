# Result reflection and evidence expansion

Every task result must be read as evidence, not as an automatic conclusion.

Run a real literature search for each substantive result: save query, date, primary sources, supporting and conflicting findings, comparability of cohorts/tasks, and relevance to the claim. Group shard results into a scientific interpretation node to avoid duplicate searches. Search/API failure is retryable infrastructure work, not evidence that no relevant literature exists. Never fabricate citations or replace this project's results with literature values.

Preserve the expectation stated before the run. Evaluate both directions: does the observation support/contradict/leave unresolved the prediction, and was the prediction appropriately defined for this cohort and endpoint? Explain effect size, uncertainty, sample size, multiplicity, confounding, leakage, controls and competing mechanisms. Do not retrofit the hypothesis to the observation.

For every outgoing dependency, record whether the result supports its premise, reduces its information value, demands a control first, or makes the planned computation scientifically pointless. Record continue/supplement/needs_user in reflection.json. Strong effects on downstream meaning pause that branch before consuming more compute; unaffected branches continue. A null finding can be scientifically complete.

## Required comparison

The result README records:

- expected pattern and why it was expected;
- observed result and uncertainty;
- discrepancy class: none, technical, sampling, design, biological, or interpretation;
- competing explanations and checks already performed;
- evidence strength: strong, moderate, weak, or not interpretable;
- limitations and what would change the conclusion;
- next action and whether user approval is required.

## Decision rule

| Finding | Supervisor action |
|---|---|
| Expected and QC-valid | Freeze only the scoped conclusion; report uncertainty and limits. |
| Strong unexpected reversal, leakage concern, implausible value, or major failure concentration | Block the conclusion and ask the user to discuss competing explanations before changing scope. |
| Moderate discrepancy with a cheap, pre-specified check | Add a linked supplementary task without changing the primary endpoint or denominator. |
| Low-risk completeness or robustness gap | Add the supplementary audit automatically and report it as secondary/post hoc. |
| Technical failure | Preserve evidence, diagnose cause, repair specifically, pass minimal verification, then resume only the failed phase within budget. See failure_recovery.md. Exhaustion is an explicit blocker, not a scientific exclusion. |

## Supplementary task policy

A self-added experiment must be:
- clearly labelled supplementary or post hoc;
- linked to the triggering task and evidence;
- cheaper and lower risk than the primary run;
- unable to silently alter the primary endpoint, split, eligibility, or frozen conclusion;
- given its own Q/task ID or subtask record, tables, figures, and conclusion.

Examples include a seed sensitivity check, alternative ranking metric, missingness mechanism audit, calibration check, negative control, matched baseline, or leakage audit. User approval is still required for new data sources, new scientific claims, changed cohort, changed primary endpoint, or expensive remote computation.

## Reporting language

Separate: observed result, interpretation, alternative explanations, evidence strength, and proposed next experiment. An unexpected result is not automatically a failure; an attractive result is not automatically causal evidence.
