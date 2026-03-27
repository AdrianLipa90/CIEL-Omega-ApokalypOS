# AGENT1.md

## Folder role

`integration/reports/` stores generated report artifacts for the SOT integration layer.

These files are outputs of documented code paths.
They should not be treated as the primary source of architecture or registry truth.

---

## Agent 1 scope in this folder

Agent 1 may use this folder for:

- synchronization reports,
- live GitHub coupling reports,
- generated state summaries,
- future audit artifacts derived from registry-aware code.

---

## Rules

- Generated reports should be traceable to `src/`, `scripts/`, or workflows.
- Placeholder reports must remain explicitly marked as placeholder in registry-facing documentation.
- Reports should not silently introduce new semantics that are absent from docs or registries.
