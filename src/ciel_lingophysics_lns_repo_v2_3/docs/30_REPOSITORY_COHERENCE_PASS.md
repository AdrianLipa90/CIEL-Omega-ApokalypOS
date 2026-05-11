# CIELingo v1.6 — Repository Coherence Pass

This pass hardens the repository before further lexical expansion. It does **not** add a new linguistic layer. It adds the audit, registry, and coherence spine needed before Batch02.

## Purpose

The system must distinguish curated seed data, generated artifacts, fallback artifacts, schemas, source code, and reports. CIELingo now treats repository coherence as part of semantic coherence.

## New invariants

```text
Every file has a type.
Every card layer has a registry entry.
Every preferred storage format must have a JSON fallback policy.
Every unresolved or incomplete relation must be visible, not hidden.
WARN is acceptable for draft seeds. BLOCKER is not.
```

## Added audit layers

- card/data type registry
- canonical status registry
- YAML/JSON pair audit
- schema coverage map
- relation integrity report
- fallback manifest

## Why this matters

Batch02 will increase the graph density. Without a coherence pass, each new card would multiply hidden uncertainty. This pass makes missing mappings and schema coverage explicit.

## Interpretation

This is a repo-level version of the CIEL principle:

```text
Unknown is legal. Hidden unknown is not.
```
