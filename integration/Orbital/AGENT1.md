# AGENT1.md

## Folder role

`integration/Orbital/` stores the imported orbital subsystem and its integration metadata inside `CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold`.

This folder is an integration-layer snapshot, not a claim that the orbital subsystem is already the full engine of the repository.

## Agent 1 scope

Agent 1 uses this folder for:
- imported orbital module snapshots,
- orbital manifests,
- orbital extension notes,
- explicit separation between imported code and native SOT integration code.

## Rules

- Imported orbital files must remain marked as imported or integration-facing.
- Orbital diagnostic runners should not silently rewrite non-orbital registry layers.
- If the orbital layer is extended, the import manifest or its addendum should be updated.
