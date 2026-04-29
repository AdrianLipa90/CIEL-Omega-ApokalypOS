# Orbital Infrastructure Rules

## Purpose

This document makes the orbital layer's local rules explicit inside the new repository geometry.

It exists so that repository-wide refactor work does not accidentally flatten or misclassify the orbital subsystem.

## What the orbital layer is

The orbital layer in `CIEL-_SOT_Agent` is:
- an imported orbital subsystem,
- an integration-facing runtime snapshot,
- a diagnostic layer,
- a bridge-adjacent executable package,
- not yet the full native engine of the repository.

Primary paths:
- `integration/Orbital/`
- `integration/Orbital/main/`

## Canonical local rules

These rules are inherited from the orbital layer's own local documentation and must be preserved during refactor:

1. Imported orbital files must remain marked as imported or integration-facing.
2. The orbital layer must stay explicitly separated from native SOT integration code.
3. Orbital diagnostic runners should not silently rewrite non-orbital registry layers.
4. Prefer read-only diagnostics and explicit manifests over hidden write-back.
5. If new orbital files are added, launchers and manifest notes must stay synchronized.
6. If the orbital layer is extended, the import manifest or its addendum must be updated.

## Refactor consequences

### 1. Do not absorb orbital runtime into `src/` in phase 1 or phase 2

Even if `integration/Orbital/main/` is executable Python, it should not be treated as just another native package under `src/ciel_sot_agent/`.
Its imported/runtime status is part of the meaning of the repository.

### 2. Keep orbital runtime and orbital bridge distinct

- `integration/Orbital/main/` = imported orbital runtime and diagnostics
- `src/ciel_sot_agent/orbital_bridge.py` = native reduction layer that consumes orbital outputs

The bridge may evolve.
The imported orbital runtime must remain visibly separate.

### 3. Preserve manifest-first interpretation

The orbital layer should remain legible through:
- import manifests,
- explicit launcher paths,
- human-readable addenda,
- report directories.

### 4. Treat write-back as exceptional

If any future orbital process writes into broader integration state, that write path must be:
- explicit,
- documented,
- auditable,
- distinguishable from read-only orbital diagnostics.

## Immediate phase-2 decision

During repository refactor, `integration/Orbital/` remains a protected sector.
The current task is to improve the surrounding repository geometry without collapsing the orbital layer into a generic package migration.

## Follow-up tasks

1. Replace or repair `integration/Orbital/IMPORT_MANIFEST.json`.
2. Keep `IMPORT_MANIFEST_V2.md` and launcher references synchronized until the JSON manifest is repaired.
3. Fold orbital report paths into higher-level indices after path normalization is complete.
