# Orbital Architecture Canon

## Purpose

This document records the architectural meaning of the full orbital source sector so that repository refactor work can follow its own rules instead of flattening it into a generic package migration.

## Canonical source sector

The full orbital source architecture lives under:

- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/`

This source sector is distinct from the imported integration-facing runtime snapshot currently hosted in:

- `integration/Orbital/`
- `integration/Orbital/main/`

## Canonical role

The orbital source sector is not merely a utility package.
It is defined by its own README as a:

- global read-only orbital coherence engine,
- repository-scale geometry extractor,
- coherence metric engine,
- spectral observable engine,
- diagnostic pass that precedes any write-back automation.

## Canonical workflow

The orbital source README defines the workflow as:

1. derive real geometry from imports + README/AGENT mesh + manifests,
2. build global `A_ij(tau_i, tau_j, Omega_ij, d_ij)`,
3. evolve the six-sector system,
4. report:
   - `R_H`
   - `T_glob`
   - `Lambda_glob`
   - `closure_penalty`
   - spectral observables

## Structural model

The source code makes the orbital layer explicit as a system model, not just a collection of scripts.

### State objects

`model.py` defines:
- `Sector`
- `ZetaVertex`
- `ZetaPole`
- `OrbitalSystem`

This establishes that orbital processing is built around:
- sector states,
- pairwise couplings,
- parameterized system evolution,
- optional zeta-pole support geometry.

### Registry / load layer

`registry.py` loads the orbital system from:
- sector manifests,
- coupling manifests,
- parameter dictionaries,
- a constructed zeta structure.

That means the orbital architecture is manifest-driven and system-loaded, not hard-coded as ad hoc logic.

### Global pass layer

`global_pass.py` confirms that the orbital layer:
- derives geometry from repository structure,
- builds fresh sector and coupling payloads,
- loads a full orbital system,
- evolves that system for multiple steps,
- emits explicit summaries and observables.

## Interpretation of "read-only"

The orbital layer is read-only with respect to broad repository rewrite and hidden write-back.

However, the source global pass does explicitly emit:
- diagnostic report files,
- derived geometry payloads,
- generated sector/coupling manifests for the run.

So the correct operational reading is:

- allowed: explicit, auditable diagnostic artifacts,
- not allowed: silent mutation of unrelated registry or integration layers.

## Refactor invariants derived from the source sector

1. Do not collapse the orbital source architecture into generic package cleanup.
2. Keep orbital runtime distinct from native SOT bridge code.
3. Preserve the manifest-driven nature of the orbital system.
4. Preserve the repository-geometry reading based on README/AGENT/import mesh.
5. Treat orbital outputs as explicit artifacts, not hidden side effects.
6. Keep the six-sector system, coupling structure, and observables legible in documentation.

## Binding to SOT

Inside `CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold`, the correct relation is:

- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/` = full source orbital architecture
- `integration/Orbital/main/` = imported integration-facing runtime snapshot
- `src/ciel_sot_agent/orbital_bridge.py` = native bridge/reduction layer

This distinction must remain explicit during repository refactor.
