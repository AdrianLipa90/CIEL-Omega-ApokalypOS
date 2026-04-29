# Integration Path Migration

## Purpose

This document explains the architectural meaning of the `integration/` path migration now in progress.

The repository is moving from a mostly flat integration layer toward class-separated machine-readable sectors while preserving backward compatibility during transition.

## Why this migration exists

The earlier flat layout placed multiple distinct machine-readable classes side by side:
- registries,
- coupling maps,
- indices,
- upstream state,
- reports,
- protected imported runtime sectors.

That worked initially, but it made the integration layer harder to read and more likely to drift semantically as more artifacts accumulated.

## Target sectors

The target class split is:
- `integration/registries/`
- `integration/couplings/`
- `integration/indices/`
- `integration/upstreams/`

These sectors are now established and already contain compatibility copies of core machine-readable files.

## Architectural rule

Path migration is not just cosmetic.
It enforces a stronger distinction between:
- identity-like state,
- relation/coupling state,
- navigation/index state,
- external/upstream binding state.

This reduces semantic ambiguity in the integration layer.

## Protected exception

The orbital layer remains outside the generic path split:
- `integration/Orbital/`
- `integration/Orbital/main/`

This is a protected imported/runtime architecture and must not be flattened into the generic data-class migration.

## Current migration mode

Current migration mode is:
- additive,
- compatibility-preserving,
- non-destructive.

That means:
- legacy paths stay valid,
- target-sector copies are created,
- indices and docs are switched only after enough convergence exists.

## Canonical migration index

The detailed old-path/new-path map lives in:
- `integration/MIGRATION_INDEX_V2.md`

That file should be treated as the practical switchboard for future path rewrites.

## Immediate consequence

Until human-readable indices and machine-readable registries are switched together, the old flat paths remain temporarily canonical.
This is deliberate and avoids false closure.
