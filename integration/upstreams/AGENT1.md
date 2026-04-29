# AGENT1.md

## Folder role

`integration/upstreams/` stores per-repository upstream maps.

## Agent 1 scope

Agent 1 uses this folder for:
- one mapping file per upstream repository,
- imported shell object maps,
- future engine object maps,
- provenance-aware imported object registries.

## Rules

- Each upstream should have its own file once object-level mapping starts.
- Objects imported from `ciel-omega-demo` should be labeled as shell objects.
- Keep shell objects and future engine objects explicitly separated.
