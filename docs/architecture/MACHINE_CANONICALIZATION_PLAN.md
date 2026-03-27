# Machine Canonicalization Plan

## Purpose

This document defines the controlled transition of machine-readable authority from legacy flat integration paths to class-separated v2 integration sectors.

It is a sub-plan of the broader canonical switch process.

## Current authority split

### Legacy machine-readable surfaces still active
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`

### V2 machine-readable surfaces already available
- `integration/indices/hyperspace_index_v2.json`
- `integration/registries/index_registry_v2.yaml`

## Canonicalization goal

Move default machine-readable authority from:
- flat legacy paths

to:
- v2 class-separated paths

without breaking runtime readers that still depend on fallback behavior.

## Canonicalization rule

A v2 machine-readable file may become authoritative when all of the following hold:

1. the v2 file exists and is internally coherent,
2. at least one validated runtime reader already prefers the v2 path,
3. canonical human-readable surfaces already point to the v2 path,
4. legacy file remains available as compatibility mirror during transition,
5. orbital protected-sector constraints remain unchanged.

## Target authoritative paths

### Index authority
- authoritative target: `integration/indices/hyperspace_index_v2.json`
- compatibility legacy mirror: `integration/hyperspace_index.json`

### Registry authority
- authoritative target: `integration/registries/index_registry_v2.yaml`
- compatibility legacy mirror: `integration/index_registry.yaml`

## Immediate blockers

- legacy machine-readable files are still presented in some surfaces without explicit secondary status
- not every runtime reader has been migrated yet
- in-place update of legacy machine files has not yet been executed

## Controlled machine phases

### Phase M1 — authority declaration surfaces
Create canonical notes that declare v2 machine authority as the target authoritative surface.

### Phase M2 — runtime preference validation
Confirm that key v2-aware readers prefer the v2 paths and report explicit path resolution.

### Phase M3 — legacy mirror policy
Document that legacy machine files remain compatibility mirrors rather than primary authority.

### Phase M4 — in-place authority switch
When tooling allows or manual switch is performed:
- annotate legacy files as compatibility mirrors,
- point root machine authority references to v2 files.

## Constraint

No machine canonicalization step may claim that legacy machine files are obsolete before the runtime layer is sufficiently converged.
