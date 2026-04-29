# Machine Authority — V2

## Purpose

This document declares the machine-readable authority targets during the controlled transition from legacy flat integration paths to class-separated v2 integration sectors.

It does not perform destructive replacement.
It defines authoritative direction.

## Authority declaration

### Canonical target index authority
The target canonical machine-readable index authority is:
- `integration/indices/hyperspace_index_v2.json`

### Canonical target registry authority
The target canonical machine-readable registry authority is:
- `integration/registries/index_registry_v2.yaml`

## Legacy mirror policy

The following legacy files remain valid during transition, but should be interpreted as compatibility mirrors rather than target authority surfaces:
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`

## Why this is valid now

This authority direction is justified because:
- v2 machine-readable files already exist,
- canonical documentation surfaces already point to them,
- v2-aware runtime readers already exist,
- runtime readers expose explicit path resolution,
- orbital protected-sector constraints remain unchanged.

## Constraint

This declaration does not mean:
- legacy files may be deleted,
- legacy files are already obsolete,
- all readers have already converged.

It only means:
- the repository now has a declared machine-readable authority direction,
- future root references should migrate toward the v2 machine-readable surfaces.

## Next controlled move

The next move after this declaration should be documentation-level demotion of legacy machine files, followed later by in-place switch operations when tooling or manual edits permit.
