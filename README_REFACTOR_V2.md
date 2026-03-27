# CIEL-_SOT_Agent — Refactor V2 Surface

Integration attractor for the CIEL ecosystem.

## Status

This file is a refactor-surface README aligned with the target repository geometry.
It does not yet replace the legacy `README.md`, which remains valid during transition.

## Role in the ecosystem

- **canon / Seed of the Worlds** — source of truth for axioms, definitions, derivations, manifests, and nonlocal repository hyperspace
- **ciel-omega-demo** — cockpit, UI surface, educational analogies, and shell publication layer
- **Metatime** — historical theory, simulations, and earlier archive layer
- **CIEL-_SOT_Agent** — integration kernel, machine-readable registry layer, orbital bridge host, Sapiens interaction seed, and public operational attractor

## Target geometry

### Governance
- `governance/`
  - operating rules
  - agent coordination
  - relational-formal contracts
  - Sapiens packet protocol

### Documentation
- `docs/architecture/`
- `docs/operations/`
- `docs/integration/`
- `docs/archive/`

### Integration data
- `integration/registries/`
- `integration/couplings/`
- `integration/indices/`
- `integration/upstreams/`
- `integration/reports/`

### Protected orbital sector
- `integration/Orbital/`
- `integration/Orbital/main/`

This sector remains protected and is not part of the generic machine-readable data-class split.

### Native runtime
- `src/ciel_sot_agent/`
  - repository phase logic
  - orbital bridge
  - Sapiens surface policy
  - Sapiens client runtime

## Core architectural direction

The repository should now be read through this direction:

`orbital source architecture -> imported orbital runtime -> native bridge reduction -> relational-formal Sapiens surface -> packet/session/report artifacts`

## Preferred navigation during refactor

- `docs/INDEX_V2.md` — preferred human-readable navigation index
- `integration/MIGRATION_INDEX_V2.md` — old-path/new-path switchboard
- `integration/indices/hyperspace_index_v2.json` — preferred machine-readable v2 index
- `integration/registries/index_registry_v2.yaml` — preferred machine-readable v2 registry

## Current refactor mode

The refactor is currently:
- additive,
- compatibility-preserving,
- non-destructive.

That means legacy paths remain valid until:
- human-readable docs,
- machine-readable indices,
- and runtime readers

converge sufficiently for a controlled canonical switch.
