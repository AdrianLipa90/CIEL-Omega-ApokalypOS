# Documentation Index — Canonical V2

Canonical human-readable navigation surface for the repository geometry refactor.

## Status

This document defines the target canonical documentation surface.
Until the final in-place switch is executed, legacy `docs/INDEX.md` remains valid as a compatibility layer.

## Root guidance

- `README_CANONICAL_V2.md` — canonical v2 root surface
- `docs/architecture/V2_CANONICAL_SWITCH_PLAN.md` — switch logic and phases
- `docs/architecture/V2_CANONICAL_SWITCH_READINESS.md` — readiness report
- `integration/CANONICAL_SWITCH_CHECKLIST.yaml` — machine-readable readiness state

## Governance

- `governance/AGENT.md` — repository-wide operating rules
- `governance/coordination/agentcrossinfo.md` — multi-agent coordination state
- `governance/contracts/RELATIONAL_FORMAL_PROTOCOL.md` — relational-formal interaction protocol
- `governance/contracts/SAPIENS_PACKET_PROTOCOL.md` — Sapiens packet protocol

## Architecture

- `docs/architecture/ARCHITECTURE.md` — repository topology and role
- `docs/architecture/REPO_REFACTOR_PLAN.md` — target geometry and migration phases
- `docs/architecture/REPO_GEOMETRY_STATUS.md` — geometry state and constraints
- `docs/architecture/INTEGRATION_PATH_MIGRATION.md` — architectural interpretation of path migration
- `docs/architecture/ORBITAL_ARCHITECTURE_CANON.md` — canonical orbital interpretation
- `docs/architecture/V2_CANONICAL_SWITCH_PLAN.md` — canonical switch plan
- `docs/architecture/V2_CANONICAL_SWITCH_READINESS.md` — readiness assessment

## Operations

- `docs/operations/OPERATIONS.md` — operational layer
- `docs/operations/V2_RUNTIME_ENTRYPOINTS.md` — preferred v2 runtime entrypoints during transition

## Integration

- `docs/integration/CIEL_OMEGA_DEMO_INTEGRATION.md` — demo shell bridge
- `docs/integration/ORBital_INTEGRATION_ADDENDUM.md` — orbital integration addendum
- `docs/integration/ORBITAL_INFRASTRUCTURE_RULES.md` — orbital protected-sector rules
- `docs/integration/SAPIENS_SURFACE_BINDING.md` — orbital bridge to relational-formal Sapiens surface

## Integration data — canonical class split

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

### Migration and switch control
- `integration/MIGRATION_INDEX_V2.md`
- `integration/INTEGRATION_DATA_SPLIT_STATUS.md`
- `integration/CANONICAL_SWITCH_CHECKLIST.yaml`

## Orbital sector

Protected imported/runtime sector:
- `integration/Orbital/INDEX.md`
- `integration/Orbital/ARCHITECTURE_BINDING.md`
- `integration/Orbital/IMPORT_MANIFEST_V2.md`
- `integration/Orbital/IMPORT_MANIFEST_REPAIRED.json`
- `integration/Orbital/main/README.md`

## Native runtime

- `src/ciel_sot_agent/orbital_bridge.py`
- `src/ciel_sot_agent/sapiens_surface_policy.py`
- `src/ciel_sot_agent/sapiens_client.py`
- `src/ciel_sot_agent/index_validator_v2.py`
- `src/ciel_sot_agent/gh_coupling_v2.py`
- `src/ciel_sot_agent/synchronize_v2.py`

## Validation

- `tests/test_sapiens_surface_policy.py`
- `tests/test_sapiens_client_packet.py`
- `tests/test_sapiens_persist_session.py`
- `tests/test_index_validator_v2.py`
- `tests/test_gh_coupling_v2.py`
- `tests/test_synchronize_v2.py`

## Canonical interpretive rule

Read the repository through this dependency direction:

`orbital source architecture -> imported orbital runtime -> native bridge reduction -> relational-formal Sapiens surface -> packet/session/report artifacts`

## Legacy note

Legacy `README.md` and legacy `docs/INDEX.md` remain compatibility surfaces until the final in-place switch is executed.
