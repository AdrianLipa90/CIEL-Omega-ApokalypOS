# Audit Report — 2026-03-27

## Scope
Audit and repair of the fully extracted `CIEL_RELATIONAL_MECHANISM_REPO` snapshot in isolated workspace.

Workspace root:
`/mnt/data/isolated_ciel_relational_full/CIEL_RELATIONAL_MECHANISM_REPO`

## Actions performed
1. Structural inspection of repository layout.
2. Python compilation audit over `src/`, `scripts/`, and `data/source/CIEL_OMEGA_COMPLETE_SYSTEM`.
3. Runtime importability scan of non-test Python modules under `ciel_omega`.
4. CLI smoke execution for:
   - `python -m ciel_omega.ciel --mode once --text "smoke"`
   - `python -m ciel --mode once --text "smoke"`
5. Full pytest run.
6. Targeted repairs for broken runtime import topology.

## Defects found

### D1. Broken internal import topology in CIEL runtime facade
Affected files:
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/ciel/__init__.py`
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/ciel/cli.py`
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/ciel/engine.py`
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/ciel/memory/__init__.py`
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/calibration/rcde.py`

Observed symptom before repair:
- `ModuleNotFoundError: No module named 'ciel'`
- `ModuleNotFoundError: No module named 'core'`
- runtime CLI not bootable from canonical extracted tree

### D2. Missing compatibility layer for legacy top-level package imports
Observed pattern:
- many runtime modules assume legacy top-level packages such as `config`, `core`, `fields`, `emotion`, `memory`, `runtime`, `orbital`, `ciel`, etc.
- extracted snapshot only contained `ciel_omega/...` hierarchy

Observed symptom before repair:
- multiple import failures in runtime and demo modules despite tests passing

### D3. Optional HF backend unavailable in current environment
Affected module:
- `ciel_omega.ciel.hf_backends`

Observed symptom:
- `ModuleNotFoundError: No module named 'transformers'`

Status:
- not repaired in code because this is an external optional dependency, not an internal logic defect

## Repairs applied

### R1. Normalized key runtime imports
- adjusted runtime facade imports so `ciel_omega.ciel` and related modules import consistently from package-qualified paths
- adjusted RCDE calibrator import to package-qualified `ciel_omega.core.math_utils`

### R2. Added compatibility symlink layer at source root
Created legacy-compatible aliases in `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/`:
- `ciel -> ciel_omega/ciel`
- `config -> ciel_omega/config`
- `core -> ciel_omega/core`
- `fields -> ciel_omega/fields`
- `emotion -> ciel_omega/emotion`
- `ethics -> ciel_omega/ethics`
- `memory -> ciel_omega/memory`
- `runtime -> ciel_omega/runtime`
- `orbital -> ciel_omega/orbital`
- plus other equivalent aliases for package families used by legacy imports

This preserves the current snapshot while restoring expected import topology.

## Test results after repair

### Compilation
- `python -m compileall -q src scripts data/source/CIEL_OMEGA_COMPLETE_SYSTEM`
- Result: **PASS**

### Pytest
- `pytest -q`
- Result: **60 passed**

### Importability scan
- Non-test modules scanned under `ciel_omega`: **226**
- Failures remaining: **1**
- Remaining failure:
  - `ciel_omega.ciel.hf_backends` → missing optional dependency `transformers`

### Runtime smoke
Commands executed successfully:
- `python -m ciel_omega.ciel --mode once --text "smoke"`
- `python -m ciel --mode once --text "smoke"`

Both returned status `ok` and emitted structured JSON.

## Residual issues
1. The repository still contains many `__pycache__` directories inherited from snapshot state.
2. Legacy import style is still widespread in the embedded `CIEL_OMEGA_COMPLETE_SYSTEM`; the compatibility alias layer fixes execution, but deeper normalization is still advisable.
3. HF backend remains unavailable until `transformers` is installed.

## Current verdict
- Embedded runtime is now **bootable in the extracted snapshot**.
- Test suite is **green**.
- Core import topology defect has been **repaired**.
- Remaining failure is **environmental / optional dependency**, not a blocking internal code defect.
