# Machine Authority Surface

## Purpose

This document is the human-readable surface counterpart of `integration/MACHINE_AUTHORITY_V2.md`.

It explains which machine-readable files should now be treated as target authority surfaces and which should be treated as compatibility mirrors.

## Target machine authority

### Target canonical machine index authority
- `integration/indices/hyperspace_index_v2.json`

### Target canonical machine registry authority
- `integration/registries/index_registry_v2.yaml`

These are now the preferred machine-readable authority targets for all future architectural guidance and v2-aware runtime work.

## Legacy compatibility mirrors

The following files remain valid during transition, but should be interpreted as compatibility mirrors rather than preferred authority surfaces:
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`

## Why this matters

Without explicit surface-level clarification, the repository would still appear to have two equally primary machine-readable authority layers.

That would increase semantic drift between:
- documentation,
- runtime behavior,
- and machine-readable ownership.

## Current repository reading rule

Read machine authority through this direction:

`target v2 authority -> fallback-aware runtime reader -> legacy mirror compatibility`

not the reverse.

## Dependency links

- machine authority declaration: `integration/MACHINE_AUTHORITY_V2.md`
- machine canonicalization plan: `docs/architecture/MACHINE_CANONICALIZATION_PLAN.md`
- readiness report: `docs/architecture/MACHINE_CANONICALIZATION_READINESS.md`
- mirror policy: `docs/architecture/LEGACY_MACHINE_MIRROR_POLICY.md`
