# Supervisor / skill architecture assessment

User scope: read current supervisor and skills; assess whether multi-skill / multi-agent restructuring is appropriate before implementation.

Only this session journal is used. Existing tracked pycache change is preserved.

## Verified findings

- Read current Skill entry, Claude supervisor definition, worker prompt, supervisor CLI, scheduler worker handling, project purpose, and relevant reference contracts.
- Source Skill has 12 reference files; entry is 13,953 UTF-8 bytes.
- Corresponding source/installed Skill files match excluding pycache; no runtime deployment changes made.
- Recommend progressive Skill separation, role-specific worker routing, small on-demand Agent roster, shared contracts and retained deterministic runtime ownership.
- Static assessment only; no measured performance or scientific-quality benefit claimed.
- Assessment artifact: [report](../../results/architecture_assessment/20260922_assessment.md) (project-root path: results/architecture_assessment/20260922_assessment.md).
- No detached work launched. Existing background monitoring snapshot was read; unrelated tasks not modified.

## Modular implementation following user clarification

User required preservation of ALL existing traits, including traits not explicitly enumerated, and replaceable external deep-research/literature Skill/sub-agent integration. Added capability Skills, shared role/core contracts, thin Claude adapters, provider handoff tooling, and Codex worker method routing. Retained all 15 numbered original Skill rules verbatim in scoped contracts; templates and nine runtime/gate/driver implementations remain byte-identical to HEAD.

Validation: 105 unit tests passed; 9 Skill validators passed; local links and Claude dependencies passed; git diff --check passed. No installed package/live project/service changes. Full validation record: results/architecture_assessment/20260922_implementation_validation.md.

## Architecture visualization

Prepared a complete in-conversation Mermaid architecture diagram from current modules.json and modular architecture documentation: shared project contract/five roots; five roles/eight stage Skills; host-mediated replaceable providers; handoff and stage-specific gates; deterministic runtime; artifact/scientific release separation; canonical results, events and monitoring. Mark platform execution limits and provider substitution boundaries. No source behavior or live service changes.

## High-resolution PNG architecture

Created and visually inspected a 4000 × 3380 PNG using deterministic Pillow typography/layout: results/architecture_assessment/figures/scientific_architecture_v0.7.0.png. Reproducible source: results/architecture_assessment/scripts/draw_architecture.py. Diagram shows five roots, invariant workflow/features, five roles/eight Skills, replaceable providers, runtime, scientific release and monitoring. PNG integrity verified; linked from modular architecture guide. No runtime or service changes.

## Scientific-agent reasonableness assessment

User requested evaluation, not further implementation. Read actual provider routing, worker invocation, publication gates, reflection/supplement transitions and amendment behavior. Assessment: coherent human-supervised research framework; execution/provenance protections are materially implemented, while independent-review enforcement, scientific behavior evaluation, complete external-provider adapters, and amendment/supplement execution need further work. Do not equate prior 105 offline tests with scientific reliability or cross-platform live validation. Report: results/architecture_assessment/20260922_scientific_agent_evaluation.md. No implementation or deployment changes this turn.

## v0.8.0 implementation following the user's authorization

Implemented independent-review receipts/gates and non-retrying scientific waits; foreground read-only Codex reviewer wrapper and restricted Claude reviewer; transactional reviewed amendments with historical report preservation and recovery; registered required/optional supplements; schema-2 provider inputs/context/limits and normalized stage checks; installed-literature adapter/probe; six synthetic behavior cases and evidence-linked human scoring/comparison. Updated source version, bilingual README, core/stage references and feature-preservation notes. Preserved preexisting tracked pyc modification and all user-level installations/live projects.

Validation: 126 isolated unit tests passed (11.103 s final suite), nine Skill validations passed, git diff --check clean. Synthetic model/review/search fixtures do not establish scientific quality. Installed literature-review entry inspected; parallel-cli absent; no online research or real model comparison run. No background task launched. Latest unrelated monitoring snapshot showed 20 healthy / 19 needs_attention.

Outputs: results/architecture_assessment/20260922_revision_v0.8.0.md, 20260922_literature_provider_probe.json, literature_provider.example.json. Remaining empirical validation and host limits are stated in that report.

## literature-review provider selection

User selected the installed `literature-review` skill as the first external literature/review provider. Added the portable provider template at `skills/scientific-research-project/assets/provider_examples/literature-review-local.example.json`, linked it from provider_contract.md, and updated both READMEs and the v0.8.0 revision record. Re-ran the installed entry inspection: SKILL.md exists with SHA-256 `bd2db633e1565f4a25af55ff78cff668b791685b93f1558166320701ff564980`; `parallel-cli` is not present, and online access/authentication/quality remain unverified. Final regression: 126 tests passed; git diff --check clean. No online search or background task launched.

## parallel-cli installation

Applied the explicitly selected `parallel-web` setup instructions. The official installer stalled on the GitHub release connection and was interrupted before writing any install directory. Downloaded the official v0.9.3 Linux x64 archive with aria2c, verified ZIP integrity and official SHA-256 `0abd18bc65f73fc680a5d909a83253c11a59b5ae7ee1975a6831aa7a5a054bb9`, then installed the bundled binary to `/home/shuifeng/.local/share/parallel-cli` with `/home/shuifeng/.local/bin/parallel-cli` symlink. `parallel-cli --version` reports 0.9.3. `parallel-cli auth --json` reports unauthenticated; no API key was requested, stored or exposed. README.zh-CN.md and README.en.md now explain that it is the primary literature-review search/extraction tool, not a PyPI package, how to install/authenticate, and what remains unverified. No online search was run.

Final installation validation: `parallel-cli --version` reports 0.9.3 and `auth --json` reports `authenticated: false` with no environment key or stored credentials. README structural parity initially caught a differing code-comment line; it was corrected. Final regression: 126 tests passed, core Skill quick validation passed, and `git diff --check` passed.

## Agent runtime workflow visualization

User requested a view of the running Agent workflow rather than the overall architecture. Added and rendered `results/architecture_assessment/scripts/draw_agent_workflow.py`, producing `scientific_agents_runtime_workflow_v0.8.0.png` (4400x3000) and a 1600x1090 preview. The diagram shows Supervisor → Researcher → Executor → Reviewer → Reporter, handoff artifacts, `needs_user` / `repairable` / `reviewing` branches, and the event/state feedback loop. Preview was visually inspected after correcting multiline handoff-card overlap. Linked from `documentation/MODULAR_ARCHITECTURE.md`. Original v0.7.0 architecture PNG remains unchanged.

Updated the overall architecture diagram as `scientific_architecture_v0.8.0.png` (4000x3380) and preview. It now shows the literature-review provider, independent review, amendment transaction, supplemental analysis and governance additions while retaining the v0.7.0 artifact. Preview was visually inspected; script syntax and image dimensions validated.

## detailed workflow visualization

User found the first runtime workflow too high-level. Inspected the repository and confirmed there is no `.github/workflows` directory; the actual workflow is defined by project references and scripts. Added `draw_agent_workflow_detailed.py` and rendered `scientific_agents_workflow_detailed_v0.8.0.png` (4800x6800) plus preview. The detailed diagram has seven phases: intake/clarification, evidence/provider handoff, design review/approval/freeze, execution/DAG/recovery, interpretation/review/supplements, reporting/events, and controlled amendment. It includes actual command/protocol labels, result paths, state branches, user decisions, review gates and feedback loops. Preview was visually inspected and image dimensions/script syntax validated.

User clarified that the canonical flow should preserve the original flowchart shape and include Agent/Skill assignments plus self-validation and iterative improvement. Added `draw_canonical_workflow.py`, producing `scientific_research_workflow_v0.8.0.png` (4800x6800) and preview. Added matching Mermaid to `documentation/MODULAR_ARCHITECTURE.md`. The new canonical workflow preserves the original U→A→B→C→D→E→P→R→S→X→V→O→I→H→N spine, adds literature-review/provider handoff, review and supplement gates, `needs_user`/`reviewing`/technical recovery loops, amendment routing, and cross-stage schema/hash/scope/run/review self-validation. Preview was visually inspected and script/image checks passed.

## authentication follow-up

On 2026-09-23, after the user configured Parallel credentials, `parallel-cli auth --json` returned `authenticated: true`. The CLI reported method `oauth`, stored credentials present, and `env_var_set: false`; the credential value was never read or printed. No search was run because no research topic was supplied and a search would consume external service quota. Online literature quality remains unverified until a real scoped evidence task is authorized and executed.

## clear canonical workflow revision

The first original-style canonical PNG was visually too dense: branch and self-validation lines crossed the main cards. Added `draw_canonical_workflow_clean.py` and rendered `scientific_research_workflow_clean_v0.8.0.png` (4400x6200) plus a 1600x2247 preview. The revised layout keeps one vertical U→H spine, a separate right-side branch/recovery rail, a separate self-validation rail, and a final decision panel. Self-validation connectors now stay in the outer gutter and do not cross any main card. Linked the clean PNG from `documentation/MODULAR_ARCHITECTURE.md`; the matching Mermaid flowchart remains the GitHub-readable fallback. Script compilation, image dimensions, visual preview inspection, and `git diff --check` passed. No background task launched.

## v0.8.1 readable workflow revision

User reported that the portrait `scientific_research_workflow_clean_v0.8.0.png` remained unreadable when viewed because too much text was compressed into a long vertical image. Added `draw_canonical_workflow_v081.py` and rendered a landscape `scientific_research_workflow_v0.8.1.png` (5200x3800) plus a 1600x1169 preview. It restores the v0.6.3-style phase bands and left-to-right cards: A understanding/evidence/design, B freeze/plan/execution, C results/quality/acceptance, D branch states/self-validation. Detailed contracts remain in Mermaid and the architecture document rather than inside tiny cards. Preview inspected; script compilation and image dimensions passed. Linked the v0.8.1 image as the recommended chart.

User requested larger text and an English counterpart. Increased the Chinese v0.8.1 card typography, added `draw_canonical_workflow_v081_en.py`, and rendered `scientific_research_workflow_v0.8.1_en.png` (5200x3800) plus preview. The English preview was visually inspected and its long titles use adaptive sizing to stay within cards. Both PNG links are now in `documentation/MODULAR_ARCHITECTURE.md`; both scripts compile and `git diff --check` passes.

User clarified that the charts must show separate language files, unambiguous arrow placement, the core one-to-one plan/result identity, and RSI self-improvement after failed evaluation. Removed ambiguous diagonal cross-row arrows and replaced them with explicit `A → B` and `B → C` transition pills in the stage gaps. Promoted `plan_step_id = task_id = result_path` to a main B-stage node in both language charts. Added `RSI auto-improvement` with the bounded loop `failed evaluation → preserve evidence → improve → rerun → re-evaluate`; scope-changing improvements still route to user/Reviewer amendment. Updated the Mermaid workflow and architecture explanation accordingly. Both charts were re-rendered and visually inspected; both scripts compile and `git diff --check` passes.

The architecture note now distinguishes the diagram's RSI workflow semantics from the current implementation: the daemon currently automates bounded technical diagnosis/recovery and blocks scientific review failures; runtime RSI for scientific evaluation would require a separate auditable proposal/attempt/re-evaluation implementation and tests.

User decided RSI should be removed because this framework serves one concrete scientific project and must not optimize for unbounded idea generation. Removed RSI labels and loops from both language charts and Mermaid. Replaced them with evidence-centered acceptance: each claim is classified as supported, contradicted, or unresolved; insufficient evidence creates a bounded supplementary evidence task. Preserved technical recovery and explicit user/Reviewer approval for scope, endpoint, or core-method changes.

User requested a publication-quality scientific figure Skill and bounded self-correction for figure quality. Inspected the installed `scientific-visualization` and `scientific-schematics` Skills and verified public sources for both. Added the project adapter `skills/scientific-visualization/SKILL.md`, core `figure_quality_contract.md`, `visualization` capability routing, reporting-stage requirement, README documentation and architecture guidance. The contract requires source-table/run lineage, journal-size typography, uncertainty/denominator honesty, accessible color, vector/raster export and a bounded render → inspect → revise plotting source/layout → re-render → recheck loop. It forbids changing data, denominators, conclusions or scientific scope during visual correction. JSON validation passed and the relevant regression suite passed: 48 tests.
