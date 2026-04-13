# Integration Migration Index V2

## Purpose

This file records the explicit migration map between the legacy flat `integration/` layout and the new class-based target sectors.

It is the first controlled navigation switch for the integration split.

## Status legend

- **legacy-canonical** — old path is still the active canonical reference in indices/docs/runtime
- **compat-copy-present** — content has been copied to the target sector, but references are not yet switched
- **target-candidate** — target path is now the intended destination for future canonical use
- **protected-exception** — excluded from generic split because it belongs to the protected orbital sector

## Migration map

| Legacy path | Target path | Status | Notes |
|---|---|---|---|
| `integration/repository_registry.json` | `integration/registries/repository_registry.json` | legacy-canonical + compat-copy-present + target-candidate | Keep legacy until index and docs rewrites are performed |
| `integration/couplings.json` | `integration/couplings/repository_couplings.json` | legacy-canonical + compat-copy-present + target-candidate | Keep legacy until code and machine registry references are switched |
| `integration/hyperspace_index.json` | `integration/indices/hyperspace_index.json` | legacy-canonical + compat-copy-present + target-candidate | Current content still points to legacy paths |
| `integration/index_registry.yaml` | `integration/registries/index_registry.yaml` | legacy-canonical + compat-copy-present + target-candidate | Current content still points to legacy paths |
| `integration/gh_upstreams.json` | `integration/upstreams/gh_upstreams.json` | legacy-canonical + compat-copy-present + target-candidate | Safe candidate for later switch |
| `integration/gh_live_registry.json` | `integration/upstreams/gh_live_registry.json` | legacy-canonical + compat-copy-present + target-candidate | Content synchronized by mirror-merge workflow |
| `integration/gh_coupling_state.json` | `integration/couplings/gh_coupling_state.json` | legacy-canonical + compat-copy-present + target-candidate | Content synchronized by mirror-merge workflow |
| `integration/hyperspace_index_orbital.json` | `integration/indices/hyperspace_index_orbital.json` | legacy-canonical + compat-copy-present + target-candidate | Still points to legacy orbital addendum paths |
| `integration/index_registry_orbital.yaml` | `integration/registries/index_registry_orbital.yaml` | legacy-canonical + compat-copy-present + target-candidate | Still anchored to orbital addendum legacy path |
| `integration/upstreams/ciel_omega_demo_shell_map.json` | `integration/upstreams/ciel_omega_demo_shell_map.json` | legacy-canonical | Already lives in target upstream sector |
| `integration/upstreams/ciel_omega_demo_inventory.json` | `integration/upstreams/ciel_omega_demo_inventory.json` | legacy-canonical | Already lives in target upstream sector |
| `integration/Orbital/` | n/a | protected-exception | Protected orbital import/runtime sector |
| `integration/Orbital/main/` | n/a | protected-exception | Executable imported orbital runtime |

## What is already synchronized

The following target-sector copies are already present:
- `integration/registries/repository_registry.json`
- `integration/registries/index_registry.yaml`
- `integration/registries/index_registry_orbital.yaml`
- `integration/couplings/repository_couplings.json`
- `integration/couplings/gh_coupling_state.json`
- `integration/indices/hyperspace_index.json`
- `integration/indices/hyperspace_index_orbital.json`
- `integration/upstreams/gh_upstreams.json`
- `integration/upstreams/gh_live_registry.json`

Mirror synchronization workflow:
- `scripts/run_integration_mirror_sync.py`
- `src/ciel_sot_agent/integration_mirror.py`

## What is not switched yet

The following layers still rely on legacy references and therefore block canonical switch-over:
- `README.md`
- `docs/INDEX.md`
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`
- orbital addendum references pointing to flat legacy docs paths

## Recommended next switch order

1. switch human-readable migration docs and architecture notes,
2. switch selected machine-readable indices,
3. switch code/config readers where needed,
4. remove legacy duplicates only after both docs and machine registries converge.

## Constraint

No switch step may flatten or reclassify the protected orbital sector.
