# Governance

This sector is the stable home for repository governance and coordination artifacts.

## Purpose

`CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold` is an integration repository. Governance files should not stay indefinitely scattered across the root.

This directory begins the migration toward a clearer separation between:
- governance,
- canonical documentation,
- machine-readable integration state,
- executable code.

## Phase-1 rule

During phase 1, files may exist in both their legacy locations and their new target locations.
That duplication is deliberate and temporary.

The goal of phase 1 is to establish the target geometry first, then update references and remove legacy duplicates in a later pass.

## Planned substructure

- `governance/AGENT.md` — repository-wide operating rules
- `governance/coordination/agentcrossinfo.md` — multi-agent coordination state
- `governance/agents/` — future normalized agent-specific scope files

## Migration note

Do not treat root-level governance files as canonical forever.
They remain present only for backward compatibility until references are updated.
