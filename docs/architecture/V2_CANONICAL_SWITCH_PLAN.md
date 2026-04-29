# V2 Canonical Switch Plan

## Purpose

This document defines the controlled transition from:
- **v2 preferred**
- to **v2 canonical**

for repository geometry, runtime entrypoints, and navigation surfaces.

The goal is to reduce semantic drift without pretending that legacy paths are already obsolete before runtime convergence is sufficient.

## Current state

The repository already has:
- v2 human-readable navigation,
- v2 machine-readable indices,
- v2-aware runtime modules for selected readers,
- compatibility copies across integration data sectors,
- protected orbital-sector exception rules.

However, legacy entrypoints and legacy flat paths are still present and still partly canonical in practice.

## Canonical-switch principle

A path or entrypoint may become canonical only when these three layers agree:

1. **surface**
   human-readable documentation points to the v2 location,
2. **machine registry**
   machine-readable index/registry points to the v2 location,
3. **runtime**
   operational modules prefer and correctly consume the v2 location.

No canonical switch is valid if it is only surface-deep.

## Required convergence domains

### Domain A — documentation surface
Must converge:
- `README.md`
- `docs/INDEX.md`
- architecture and operations notes that still imply legacy defaults

### Domain B — machine-readable navigation
Must converge:
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`
- any remaining orbital addendum references that still point to flat legacy docs paths when a v2 path already exists

### Domain C — runtime entrypoints
Must converge:
- validation runtime
- gh coupling runtime
- synchronization runtime
- any remaining readers that still hard-code legacy flat integration paths

### Domain D — deprecation signaling
Must converge:
- legacy entrypoints must remain executable during transition,
- but they should be marked as secondary once the v2 runtime path is validated,
- destructive deletion happens only after stable convergence.

## Controlled switch phases

### Phase 1 — readiness capture
Record what already exists and what is still blocking full canonical switch.

Deliverables:
- this plan,
- `docs/architecture/V2_CANONICAL_SWITCH_READINESS.md`,
- `integration/CANONICAL_SWITCH_CHECKLIST.yaml`

### Phase 2 — surface canonicalization
Switch root and documentation surfaces from "v2 preferred" to explicit canonical v2 guidance.

Candidate actions:
- update `README.md` to point first to v2 navigation,
- update `docs/INDEX.md` to point first to v2 navigation,
- mark legacy navigation as compatibility layer rather than primary layer

### Phase 3 — machine canonicalization
Move default machine-readable authority from legacy flat paths to class-separated v2 sectors.

Candidate actions:
- switch authoritative references from `integration/index_registry.yaml` to `integration/registries/index_registry_v2.yaml`
- switch authoritative references from `integration/hyperspace_index.json` to `integration/indices/hyperspace_index_v2.json`
- preserve legacy files as compatibility mirrors until runtime convergence is proven

### Phase 4 — runtime canonicalization
Make v2 runtime entrypoints the default operational surface.

Candidate actions:
- ensure all preferred launchers are documented,
- ensure all major path readers have v2-aware implementations,
- downgrade legacy launchers to compatibility status in docs and operational guidance

### Phase 5 — selective legacy de-emphasis
Only after the above convergence is stable:
- label legacy paths as deprecated in docs,
- stop presenting them as default examples,
- retain them as compatibility layer until deletion is justified

## Hard constraints

1. No generic split may flatten the protected orbital sector.
2. No runtime switch may hide path resolution.
3. No document may claim legacy is obsolete before runtime convergence is demonstrably sufficient.
4. No deletion should occur before both surface and machine registry layers converge.

## Immediate next move

The next step should be readiness capture, not destructive switch.
