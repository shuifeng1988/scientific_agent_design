---
name: scientific-intake
description: "Provide the intake stage of a scientific-research-project workflow. Use for scoped intake work governed by its five root documents and registered task/result paths."
---

# Scientific Intake

This stage requires the bundled `scientific-research-project` core Skill. Locate its installed package using the host's Skill catalog; do not assume a user home path. If unavailable, report the missing core rather than creating another project convention. Reading the core does not repeat intake for an already approved task.

Read the core's `references/project_contract.md` and `references/roles/supervisor.md`, then these core-relative references only as relevant:

- `references/intake_protocol.md`

Deliver: A direction brief with real user answers, uncertainty and the next decision; no invented approval.

Resolve capability `intake` through the core's `scripts/module_provider.py resolve --root PROJECT --capability intake --host HOST` (HOST: codex, claude, or the actual host name). Without a project provider override, use the built-in method in these references. With an override, read `references/provider_contract.md`, verify the named provider is actually available, and use it only for the bounded method. Never recursively invoke this same stage entry as its own provider.

The provider cannot replace the five root files, task IDs/result mapping, scientific scope, real approvals, required report contents or existing acceptance gates. Return missing authority/access explicitly. In a noninteractive worker, send needs_user to the outer conversation; never manufacture answers. Write only the assigned task/provenance artifacts. Runtime and the project event hook own shared execution state and managed document updates.
