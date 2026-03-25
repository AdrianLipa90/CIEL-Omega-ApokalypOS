# AGENT1.md

## Folder role

`src/` stores executable integration logic.

For Agent 1, this folder is for SOT integration code,
not for claiming full canonical theory ownership.

## Agent 1 scope

Agent 1 uses this folder for:
- registry-aware integration code,
- upstream synchronization logic,
- shell-facing and cross-repository coupling utilities,
- future shell/engine interface code.

## Rules

- Code here should remain traceable to docs and registries.
- If a code object depends on imported sources, provenance should stay explicit.
- Shell logic and future engine logic must not be silently conflated.
