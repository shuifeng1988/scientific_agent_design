#!/usr/bin/env python3
"""A bounded Codex planning/repair call. Uses current user's CLI auth and policy."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

from structured_output import proposal_object
from supervisor_daemon import atomic, file_hash


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--request', type=Path, required=True)
    ap.add_argument('--codex', default=shutil.which('codex'))
    a = ap.parse_args()
    request = json.loads(a.request.read_text())
    if not a.codex:
        raise RuntimeError('Codex CLI unavailable; configure another progress worker')
    output = a.request.with_name('proposal.json')
    raw = a.request.with_name('proposal.raw.txt')
    prompt = '''Use scientific-research-project Skill to advance this authorized research project.
This noninteractive worker cannot clarify a new research purpose with the user. If a requested
node lacks an agreed scientific direction, return needs_user with 1–3 focused questions for the
outer conversation; do not invent answers, draft an entire new study, or freeze a design.
For each such question, suggest concise choices plus an unrestricted Other/free-text route
for the outer operator to render using its permitted interface; never infer a default answer.
Do not treat automatic Skill selection as consent. Reuse existing actual approvals for unchanged tasks;
ordinary method implementation within that authority does not require repeating intake.
Read the five canonical documents and the supplied work request. You are a bounded planning/repair
worker, not the scheduler. Prepare executable phase contracts for the requested existing nodes,
write/test the necessary small implementation scripts and verify relevant source/input metadata.
Read each task's actual 01_PLAN.md step and keep its canonical result path.
Read core_evidence.md when planning or interpreting central claims: distinguish primary sources,
actual project measurements, independent corroboration and inference, with task/result locators.
Skill attribution and technical integrity checks are not scientific evidence. Installation/resume
does not revise a frozen design; route authorized design revisions through research_depth.md.
Missing scientific design detail is not permission to invent it. Read research_depth.md: connect
the node's purpose, inputs, method/controls, output schema, QC and evidence use to the approved
task. Supply routine implementation within that scope; return needs_user for unresolved
scientifically consequential choices. Do not mistake a broad task title for a detailed protocol.
For projects with registry/design.json, use research_workflow.py check before planning new computation. Formal
reports must use a task/run/plan-bound report manifest and render Markdown and Word from the same
content with research_workflow.py render. QC covers the manifest, report receipt, reflection,
README, Word, all summary tables and figures. This renderer formats real supplied analysis;
never invent data, searches, conclusions, user approvals or a scientific review. User approval
records and design freezing belong to the outer operator, never to this planning worker.
If a node has worker_failure_record, the PREVIOUS PLANNING WORKER failed. Read that immutable
record and its raw output/stderr first, diagnose and address its cause before proceeding; reuse
valid prior work. Do not repeat the same unsuccessful planning operation without a remedy.
For new structured-output adapters, reuse the bundled structured_output.py decoder with raw
output preservation and explicit schema checks; reject conflicting or incomplete content.
For EVERY failed step: preserve evidence, diagnose cause, apply a targeted remedy, run minimal
verification, then resume ONLY the failed phase. Never blindly resubmit unchanged broken work.
If node state has repairable=true, read its failure_record and the supplied recovery_protocol.
Return recovery alongside id/contract: failure_record_sha256, diagnosis, action, resume_phase,
validation {path,sha256}, preserved_artifacts [{path,sha256}], and reuse_justification.
Actually run the minimal test. Its validation JSON must contain passed:true, exit_code:0,
command:[...], log:{path,sha256}, tested_gates:[{path,sha256}] covering new/changed executable code.
Tests and repair evidence live under that node's result path. Preserve original non-code gates,
earlier successful phase specs, scientific method, inputs and attempt budget. Use versioned repair
scripts when a shared old script is still needed to verify earlier results. For later-phase resume
reuse SCI_RUN_ID; isolate new outputs by SCI_ATTEMPT/SCI_JOB_ID and verify reused artifact hashes.
Unknown remote status means reconcile, not duplicate submission. Scientific anomalies require
discussion; never change an endpoint or exclusion to make results pass. Do not use synthetic
fixture success as evidence that real model smoke, coverage or scientific results passed.
Do not run heavy computation locally. Do not submit detached work: the resident daemon owns launch.
Do not invoke intervene, reset counters, grant new budget rounds, or restart the supervisor.
Only a fresh explicit human instruction handled by the outer operator can reset a named task.
Do not edit registry/supervisor.json, registry/tasks.tsv, provenance/supervisor/state.json or core
Markdown files (the daemon owns them). Do not change frozen scientific scope, cohort, eligibility,
endpoints or split. Do not create performance values or mark tasks complete. Missing scientific
decisions must be reported as needs_user with concrete evidence. Preserve all eligible models.
For completion_policy=artifact, supply run and validate only. Validate must synchronize a
run-bound _evidence/qc.json with passed:true and artifact hashes plus README to the local
node result directory. This releases artifact dependencies, never final scientific release.
For interpretation/report contracts use a real literature-search/reasoning worker with full source records,
preregistered expected-vs-observed comparison and downstream scientific impact. Failed searches or
unknown inputs must never be declared verified. Inspect the source references/continuous_execution.md
for contract schema. Keep each run's evidence isolated by SCI_RUN_ID. All required phases need explicit
argv, host, cwd, resources, timeout_seconds and immutable input/script/contract gate hashes.
Create a unique logs/sessions/ journal for this call; never read other conversation journals.
Output ONLY a JSON object {"contracts":[{"id":"existing node", "contract":{...}}],
"blocked":[{"id":"existing node", "reason":"specific evidence and recovery action",
"needs_user":false}], "expansions":[]}. Expansions are optional and must follow the exact
parent expansion_policy model/stage matrix, IDs parent.model.stage, canonical paths and
stage dependencies; the daemon checks and adopts them, never edit live state yourself.
For a scoped model prepare node, implement the actual remote fix/integration and runnable
prepare/validation commands. Existing deployment evidence must be reused when hashes and
environment still match; new-input compatibility still requires real checks. A missing
dependency is a concrete install/repair job, not a reason to write another broad inventory.
Do not require all models to be ready before supplying one model's independent contract.
Empty contracts is allowed for genuine missing authority or unavailable evidence, but
repeated empty proposals trigger planning_stalled. Tested helper code alone is not dispatch.
Do not approve changes outside the current user-authorized scope. The dispatcher validates the
proposal, preserves dependencies and resource limits, and assigns the execution hash.
Work request follows:\n'''
    # Noninteractive CLI support verified against installed exec --help.
    cmd = [a.codex, 'exec', '--approve-for-me', '--skip-git-repo-check', '-C', str(a.root.resolve()),
           '--output-last-message', str(raw), '-']
    atomic(a.request.with_name('worker_prompt.txt'),prompt + json.dumps(request, ensure_ascii=False))
    with a.request.with_name('worker_stdout.log').open('w') as so, a.request.with_name('worker_stderr.log').open('w') as se:
        result = subprocess.run(cmd, input=prompt + json.dumps(request, ensure_ascii=False),
                                text=True,stdout=so,stderr=se)
    if result.returncode:
        raise SystemExit(result.returncode)
    proposal, normalization = proposal_object(raw.read_text())
    atomic(a.request.with_name('output_validation.json'),dict(raw_sha256=file_hash(raw),
           normalization=normalization, worker_exit_code=result.returncode, schema_valid=True))
    atomic(output, proposal)


if __name__ == '__main__':
    main()
