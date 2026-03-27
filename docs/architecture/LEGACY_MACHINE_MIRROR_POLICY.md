# Legacy Machine Mirror Policy

## Purpose

This document defines how legacy machine-readable files should be interpreted during the controlled transition to v2 machine authority.

## Legacy files covered

The following legacy machine-readable files are covered by this policy:
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`

## Policy

These files remain:
- valid,
- readable,
- executable inputs for fallback-aware runtime layers,

but they should no longer be interpreted as the target machine authority surfaces.

## Interpretation rule

### Legacy files are now compatibility mirrors
They preserve backward compatibility and transitional operability.

### V2 files are now target authority surfaces
The target authority direction is:
- `integration/indices/hyperspace_index_v2.json`
- `integration/registries/index_registry_v2.yaml`

## What this policy does not mean

This policy does **not** mean:
- legacy files may already be deleted,
- legacy files are broken,
- all runtime readers have already converged,
- in-place root authority has already been rewritten.

## What this policy does mean

It means:
- documentation should stop treating legacy machine files as the preferred default,
- new architectural guidance should point first to v2 machine-readable files,
- runtime layers should continue to expose explicit fallback behavior when both surfaces are supported.

## Constraint

Any future destructive action still depends on convergence across:
- human-readable surface,
- machine-readable authority,
- runtime behavior.
