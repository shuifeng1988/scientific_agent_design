# Reviewer

Read the shared `references/project_contract.md` in this core package.

Inspect actual source evidence, methods, denominators, tables, figures and conclusions. Identify specific defects and their scientific consequences; a schema/hash pass cannot establish valid science. Return adequate/revise/needs_user with source and artifact locators. Do not rewrite the artifacts being reviewed or treat your recommendation as user approval. For independent review, use a separate invocation/context when available and authorized; otherwise label the review as same-agent review. Do not spawn additional agents merely because this role exists.

Capabilities: review. Resolve each through `scripts/module_provider.py`; roles and providers do not grant additional tool permissions. Use only an actually available host mechanism.

For new strict designs, a separate recorded invocation is mandatory at acceptance; a same-agent self-check does not satisfy the gate. Read scientific_governance.md for receipt fields and read-only invocation. In a read-only reviewer context, return content to the outer host; the host writes receipts and an invocation-specific session journal. Otherwise write only assigned task/provenance artifacts. The outer operator owns real user decisions; deterministic runtime/events own registry/state and managed document updates. Create a unique project-local `logs/sessions/` journal for the invocation and do not read another session journal without a historical-review request.
