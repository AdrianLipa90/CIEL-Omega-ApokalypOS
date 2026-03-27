# CIEL Relational Mechanism Repo

Status: **canonical mechanism and registry repo** for the embedded `CIEL_OMEGA_COMPLETE_SYSTEM` snapshot contained in `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/`.

## Scope

This repository is the **mechanism layer**, not the final physics closure and not a product-level orbital cockpit.

Primary outputs in this repo:
- runtime file inventory
- runtime function inventory
- orchestrator-down dependency graph
- formal symbol registry from contract / PDF references
- symbol-to-runtime mapping scaffolds
- phase coupling / Euler-Berry mechanism tables
- documentation audit notes and canonical documentation map

Primary registries:
- `registries/runtime_files.csv`
- `registries/runtime_functions.csv`
- `registries/orchestrator_graph_edges.csv`
- `registries/formal_symbols.csv`
- `registries/symbol_to_runtime_map.csv`
- `registries/phase_couplings.csv`

## Out of scope

Out of scope at this stage:
- final derivations of `D_f`, `J(epsilon)`, or full metric closure
- treating any single PDF as Source of Truth
- presenting the embedded runtime as a fully integrated orbital product
- claiming that the orbital subsystem already closes the runtime decision loop

## Working rule

1. inventory
2. map
3. graph
4. only then derive

## Documentation canon

Read these first:
1. `docs/DOCUMENTATION_CANON.md`
2. `docs/MECHANISM_SCOPE.md`
3. `docs/FORMALISM_V0.md`
4. `docs/MD_AUDIT_NOTES.md`
5. `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/README.md`

## Current audit status

Current local audit state on this workspace:
- package import topology normalized
- test suite passing
- CLI smoke run passing
- orbital subsystem functional as a diagnostic engine
- orbital subsystem not yet proven to be the active runtime control law

See:
- `docs/AUDIT_REPORT_2026-03-27.md`
- `docs/AUDIT_REPORT_2026-03-27_CONTINUATION.md`
