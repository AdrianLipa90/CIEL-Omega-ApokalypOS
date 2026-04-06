# Documentation Index — V2

Human-readable navigation index aligned with the target repository geometry.

## Status

This index is the preferred navigation surface during the repository refactor.
The legacy `docs/INDEX.md` remains valid until full convergence is complete.

## Governance

- `governance/AGENT.md` — repository-wide operating rules for the integration attractor
- `governance/coordination/agentcrossinfo.md` — multi-agent coordination state
- `governance/contracts/RELATIONAL_FORMAL_PROTOCOL.md` — relational-formal interaction protocol
- `governance/contracts/SAPIENS_PACKET_PROTOCOL.md` — packet-level protocol for Sapiens-facing layers

## Architecture

- `docs/architecture/ARCHITECTURE.md` — repository role, topology, and integration position
- `docs/architecture/REPO_REFACTOR_PLAN.md` — target geometry, migration phases, and invariants
- `docs/architecture/REPO_GEOMETRY_STATUS.md` — current geometry state and protected-sector rules
- `docs/architecture/INTEGRATION_PATH_MIGRATION.md` — architectural explanation of the `integration/` path migration
- `docs/architecture/ORBITAL_ARCHITECTURE_CANON.md` — canonical interpretation of the full orbital source sector

## Operations

- `docs/operations/OPERATIONS.md` — workflows, scripts, automation paths, and operational layer

## Integration notes

- `docs/integration/CIEL_OMEGA_DEMO_INTEGRATION.md` — shell-level bridge to `AdrianLipa90/ciel-omega-demo`
- `docs/integration/ORBital_INTEGRATION_ADDENDUM.md` — orbital integration addendum
- `docs/integration/ORBITAL_INFRASTRUCTURE_RULES.md` — protected-sector rules for orbital infrastructure
- `docs/integration/SAPIENS_SURFACE_BINDING.md` — binding from orbital bridge state to relational-formal Sapiens surface

## Integration data navigation

- `integration/MIGRATION_INDEX_V2.md` — old-path/new-path migration switchboard
- `integration/INTEGRATION_DATA_SPLIT_STATUS.md` — split status for integration data classes

### Registries
- `integration/registries/repository_registry.json`
- `integration/registries/index_registry.yaml`
- `integration/registries/index_registry_orbital.yaml`
- `integration/registries/index_registry_v2.yaml`

### Couplings
- `integration/couplings/repository_couplings.json`
- `integration/couplings/gh_coupling_state.json`

### Indices
- `integration/indices/hyperspace_index.json`
- `integration/indices/hyperspace_index_orbital.json`
- `integration/indices/hyperspace_index_v2.json`

### Upstreams
- `integration/upstreams/gh_upstreams.json`
- `integration/upstreams/gh_live_registry.json`
- `integration/upstreams/ciel_omega_demo_shell_map.json`
- `integration/upstreams/ciel_omega_demo_inventory.json`

## Orbital sector

Protected imported/runtime sector:
- `integration/Orbital/INDEX.md` — local orbital index
- `integration/Orbital/ARCHITECTURE_BINDING.md` — source/import binding
- `integration/Orbital/IMPORT_MANIFEST_V2.md` — repaired human-readable import note
- `integration/Orbital/IMPORT_MANIFEST_REPAIRED.json` — repaired machine-readable import manifest
- `integration/Orbital/main/README.md` — mechanism/runtime interpretation

## Native runtime

- `src/ciel_sot_agent/orbital_bridge.py` — native reduction layer consuming orbital diagnostics
- `src/ciel_sot_agent/sapiens_surface_policy.py` — explicit relational-formal surface policy helper
- `src/ciel_sot_agent/sapiens_client.py` — Sapiens packet/session runtime with `surface_policy`

## Validation

- `tests/test_sapiens_surface_policy.py` — validates relational-formal surface policy
- `tests/test_sapiens_client_packet.py` — validates packet `v0.2` and `surface_policy`
- `tests/test_sapiens_persist_session.py` — validates persisted Sapiens artifacts

## Current interpretive rule

The repository should now be read through this dependency direction:

`orbital source architecture -> imported orbital runtime -> native bridge reduction -> relational-formal Sapiens surface -> packet/session/report artifacts`

This direction is explicit in documentation and partially explicit in machine-readable v2 indices.
