# Shared project contract

These requirements are retained from the original project Skill; rule numbers preserve their original identifiers (the other rules live in design_contract.md and execution_contract.md). Reference paths below are relative to the scientific-research-project package root.

Use this skill to execute the approved steps in 01_PLAN.md and deliver a corresponding research package for each step under results/. Every formal analysis links its question and plan to data provenance, software and exact methods, results, conclusions, interpretation, tables, figures, REPORT.docx, and verification evidence. Domain analysis/report workers create the scientific content; the Supervisor schedules and checks it.

1. For an existing project, read 00_PROJECT.md, 01_PLAN.md, 02_SOFTWARE.md, 03_DATA.md, and 04_STATUS.md. For a new project, first discuss the user's question and create draft 00_PROJECT.md and 01_PLAN.md; do not fabricate approved root documents.

3. Treat Qxx as a scientific question and Qxx.xx as its executable task. Every executable plan task must have one pre-registered result path in registry/tasks.tsv. At execution, read that task's methods/data/commands and write its package to this path; link back to the question and plan. Keep multiple runs and technical children inside the task path. Update validated tables, figures and report drafts as results arrive, and deliver consistent Markdown and Word reports at formal completion. Read references/project_schema.md for the required contents.

4. Use all eligible models and datasets specified by the task. A pilot subset is evidence for readiness, never a formal benchmark replacement.

6. Record every download, software/checkpoint, run, QC, failure, and approved plan change with the project event hook.

7. Every result must compare preregistered expectations with observations and uncertainty, search supporting and conflicting literature, explain alternatives, and assess how the evidence changes each downstream task's scientific value. A strong unexpected result holds affected dependent branches for discussion; unrelated ready tasks continue. Add low-risk, high-value evidence tasks with explicit dependencies and provenance under the existing scope.

8. Do not call a process exit a scientific completion. A task is complete only when its result package has README, Word report, tables, figures, QC, reflection, and evidence hashes; exclusions remain in the audit denominator.

9. Never silently rewrite a frozen goal, endpoint, cohort, split, eligibility rule, or exclusion rule. Use a visible qc.failed or plan-amendment draft.

13. Separate artifact readiness from scientific release: completion_policy=artifact permits only run → validate, requires run-bound hashes and a methods/provenance README, and must set scientific_result=false and finalizes_task=false. Downstream computation may consume verified artifacts immediately. Report nodes retain real literature interpretation, Word/tables/figures/reflection; scientific publication additionally waits for the event-hook acknowledgement. A failed report must not invalidate independent verified computation.

## Portable operation and session evidence

Keep session notes in a unique project-local logs/sessions/ file; never read or merge another session journal without an explicit historical-review request. Preserve the original methods, source/version, actual host/command, input/output checksums and failure evidence. Before server-bound downloads assess network reliability; when needed download on a reliable local host, verify size/checksum, transfer and verify again on the target server, retaining URL, paths and transfer command. Local verification never proves remote bytes.

For work continuing in the background, preserve the task registry, active monitoring service, fresh snapshot, child-job visibility and final output verification requirements. Completion/stopping updates the registered state. Report service health separately from actual scientific progress and show the monitoring command. No change of provider relaxes the current project/host permissions or scientific decision boundaries.
