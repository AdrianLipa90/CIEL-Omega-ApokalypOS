# CIEL OMEGA COMPLETE SYSTEM

Canonical merged build created from:
- CIEL_UNIFIED_SYSTEM_EULER_EXTENDED.tar.gz (full runtime base)
- CIEL_UNIFIED_SYSTEM_SEMANTIC_EULER.tar.gz (latest semantic Euler patch overlay)

## Scope of this manifest

This manifest records the **actual packaged state** of `systems/CIEL_OMEGA_COMPLETE_SYSTEM` after P0 integrity work on 2026-03-24.

Excluded from manifest fingerprints:
- `CANONICAL_BUILD_MANIFEST.md` itself (to avoid self-reference)
- `__pycache__/`
- `.pytest_cache/`
- `*.pyc`
- `*.pyo`

Included in manifest fingerprints:
- code, docs, tests, demos, configs
- top-level runtime data layer `CIEL_MEMORY_SYSTEM/`
- package-embedded legacy data mirror under `ciel_omega/CIEL_MEMORY_SYSTEM/`

## Build facts (synchronized)

- Whole-system payload file count: **307**
- Whole-system payload fingerprint (path+size SHA-256): `874926cee90af09544e09bca4a05432189bccb2e8f3161049b67fc09cbc76cee`
- Code+docs payload file count (excluding `.db` and `.h5`): **304**
- Code+docs payload fingerprint (path+size SHA-256): `9e9ed93e7d701afe0cee0d632799a51abe720fefe4a9e2e5a040d2b3fcc3c91c`
- `ciel_omega/` subtree file count: **298**
- `ciel_omega/` subtree fingerprint (path+size SHA-256): `98061d0ecd22860fc2ab31fd4c01ffa26141d88256a56cfc90346e3f2291fe0a`
- `ciel_omega/` code+docs count (excluding package-internal `.db`): **297**
- `ciel_omega/` code+docs fingerprint (path+size SHA-256): `57a726f0bb889e2f3e770b179e7c65dc71ce40458e925108b7cdc9b2d534d6d6`
- Persistent data artifact count (`.db` + `.h5`): **3**
- Persistent data artifact fingerprint (path+size SHA-256): `cbe0887bb7b105422ad7eb92a9bbff5de2fa1303f48be182806f91eb45aae696`

## Runtime package facts

Inside `ciel_omega/` there are currently:
- **258 Python files** including `TODO/`
- **244 Python files** excluding `TODO/`

Largest Python subsystems inside `ciel_omega/` excluding `TODO/`:
- `memory/` — 36
- `core/` — 23
- `ext/` — 17
- `runtime/` — 11
- `emotion/` — 11
- `mathematics/` — 11
- `vocabulary/` — 10
- `ciel/` — 9
- `cognition/` — 8
- `orbital/` — 8
- `fields/` — 7

## Included layers

- core/runtime
- bridge
- constraints (Euler/EBA extended + semantic sector)
- vocabulary.yaml
- vocabulary_tools (resolver + symbol_extractor)
- demos/tests
- packaged runtime data layer

## Data layer policy

Current P0 policy:
- authoritative packaged runtime data layer = top-level `CIEL_MEMORY_SYSTEM/`
- package-internal `ciel_omega/CIEL_MEMORY_SYSTEM/.../memory_ledger.db` is retained as a legacy compatibility mirror until P1
- persistent data artifacts are not silently deleted during integrity work

See also:
- `DATA_LAYER_POLICY.md`
- `../../reports/audit/P0_CANONICAL_INTEGRITY_AUDIT_2026-03-24.md`
- `../../reports/audit/P0_1_MANIFEST_SYNC_2026-03-24.md`

## Intent

This artifact is the current whole-system canonical package after semantic Euler overlay, with manifest values synchronized to the actual payload and volatile validation residue explicitly excluded.
