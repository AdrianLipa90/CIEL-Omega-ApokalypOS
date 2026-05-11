# Memory and Orbital Classification Audit

Date: 2026-05-11  
Status: working audit snapshot  
Scope: CIEL1 memory layers, orbital layers, NOEMA projection layers, continuity surfaces

## Classification labels

- `canonical_runtime` — active execution authority
- `canonical_durable` — durable memory / state authority
- `runtime_continuity` — live continuity surface used between cycles/sessions
- `canonical_relational_injection` — authoritative relational objects injected into runtime
- `derived_registry` — machine-generated registry or index
- `projected_surface` — export / projection / report surface
- `mirror_compat` — compatibility mirror, not primary authority
- `operational_shadow` — useful operational surface, but not core authority

## Core classification

| Component | Classification | Notes |
|---|---|---|
| `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/orchestrator.py` | `canonical_runtime` | Runtime M0-M8 memory core |
| `src/ciel_sot_agent/ciel_pipeline.py` | `canonical_runtime` | Main CIEL/Ω adapter |
| `src/ciel_sot_agent/orbital_bridge.py` | `canonical_runtime` | Orbital-to-pipeline bridge |
| `src/ciel_sot_agent/synchronize.py` | `canonical_runtime` | Repo phase synchronizer |
| `integration/Orbital/main/*` | `canonical_runtime` | Canonical orbital mechanism layer |
| `integration/Orbital/main/phase_control.py` | `canonical_runtime` | Canonical control law surface |
| `src/ciel_geometry/semantic_mass.py` | `canonical_runtime` | Canonical `M_sem` and Kepler-like orbit law |
| `src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db` | `canonical_durable` | Main semantic durable store |
| `src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/WPM/wave_snapshots/wave_archive.h5` | `canonical_durable` | Main affective / wave durable store |
| `~/.claude/ciel_state.db` | `canonical_durable` | Central telemetry / state persistence |
| `~/Pulpit/CIEL_memories/memories_index.db` | `canonical_durable` | Session/chat durable store |
| `~/Pulpit/CIEL_memories/local_test/consolidator.db` | `canonical_durable` | Consolidation durable store |
| `~/Pulpit/CIEL_memories/state/ciel_orch_state.pkl` | `runtime_continuity` | Runtime continuity snapshot |
| `~/.claude/ciel_orch_state.pkl` | `runtime_continuity` | Persistent runtime continuity snapshot |
| `integration/registries/timeline.json` | `runtime_continuity` | Dynamic phase history |
| `~/Pulpit/CIEL_memories/state/htri_state.json` | `runtime_continuity` | HTRI cache state |
| `~/.claude/htri_state.json` | `runtime_continuity` | HTRI daemon state |
| `integration/registries/ciel_entity_cards.yaml` | `canonical_relational_injection` | Entity source for OrchOrbital |
| `src/ciel_sot_agent/orch_orbital.py` | `canonical_relational_injection` | Entity injection into orbital runtime |
| `integration/Orbital/main/manifests/sectors_global.json` | `canonical_relational_injection` | Orbital geometry input |
| `integration/Orbital/main/manifests/couplings_global.json` | `canonical_relational_injection` | Orbital coupling input |

## Derived registries

- `integration/registries/file_universal_catalog.json`
- `integration/registries/file_catalog.json`
- `integration/registries/file_wij_graph.json`
- `integration/registries/py_library_index.json`
- `integration/registries/md_library_index.json`
- `integration/registries/file_sense_registry.json`
- `integration/registries/definitions/orbital_definition_registry.json`
- `integration/registries/definitions/nonlocal_definition_edges.json`
- `integration/registries/definitions/nonlocal_cards_registry.json`

## Projected surfaces

- `integration/imports/noema_sapiens_orbital/generated/registry_export.noema`
- `integration/imports/noema_sapiens_orbital/CONTRACT_CONCORDANCE.json`
- `integration/reports/noema_sot_report.json`
- `integration/reports/orbital_bridge/*`
- `integration/reports/file_sense_report.json`

## Mirror / compatibility

- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db`

This DB is treated as a compatibility mirror rather than a co-equal durable source.

## Operational shadow surfaces

- `integration/db/ciel_cards.xlsx`
- `src/ciel_sot_agent/spreadsheet_db.py`

These surfaces are operationally useful, but should not be mistaken for the primary authority for memory, nonlocal cards, or telemetry.

## Nonlocal layer split

The audit distinguishes three nonlocal strata:

1. `runtime_nonlocal`
   - `nonlocal_coherent_fraction`
   - `phi_ab_mean`
   - `phi_berry_mean`
   - `bridge_target_phase`
   - `euler_bridge_closure_score`

2. `registry_nonlocal`
   - `orbital_definition_registry.json`
   - `nonlocal_definition_edges.json`
   - `nonlocal_cards_registry.json`
   - `registry_export.noema`

3. `memory_nonlocal`
   - `holonomic_memory.py`
   - `semantic_scorer.py`
   - Hebbian edges
   - nonlocal memory index

These strata should not be merged conceptually without an explicit contract layer.
