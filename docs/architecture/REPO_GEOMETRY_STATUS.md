# Repository Geometry Status

## Status

Repository refactor is in progress.
The target geometry has been established additively, but legacy flat paths still exist.

## Most important constraint now in force

The orbital sector is not to be treated as generic package clutter.

It is split into three distinct layers:

1. `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/`
   - full source orbital architecture
   - canonical orbital workflow
   - system model and diagnostic engine

2. `integration/Orbital/main/`
   - imported integration-facing runtime snapshot
   - protected import sector
   - explicit manifest/readme/launcher coupling

3. `src/ciel_sot_agent/orbital_bridge.py`
   - native SOT bridge/reduction layer
   - downstream consumer of orbital diagnostics

## Consequence for refactor

### Allowed now
- create clearer documentation sectors
- create canonical navigation files for the new geometry
- improve binding documents between source and imported orbital layers
- improve indices around the orbital sector

### Not allowed now
- silently absorb orbital runtime into `src/ciel_sot_agent/`
- erase imported-status markers
- flatten source orbital architecture into generic cleanup
- let orbital runners mutate unrelated integration layers without explicit documentation

## Legacy-path status

The following legacy documents still need a later normalization pass:
- `README.md`
- `docs/INDEX.md`
- flat `docs/*.md` compatibility paths
- root governance compatibility paths

## Phase-2 outcome so far

The repository now has a documented architectural rule that the orbital layer is protected and structurally distinct during refactor.
This should guide every later cleanup step.
