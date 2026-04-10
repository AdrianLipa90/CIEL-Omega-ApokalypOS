# OFFLINE DEPENDENCY BUNDLE V1

## Purpose
Provide a deterministic offline dependency surface for `CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold` so the repository can be bootstrapped and tested without relying on live network access.

This operation introduces:
- a wheelhouse scaffold under `vendor/wheels/`,
- a machine-readable manifest under `vendor/manifests/`,
- offline bootstrap scripts under `tools/bootstrap/`,
- and documentation showing where the bundle lives and how it is used.

---

## Current status
**Implementation status:** scaffolded and documented.

**What exists now:**
- offline wheelhouse structure,
- bundle manifest,
- offline runtime bootstrap script,
- offline dev/test bootstrap script,
- documentation and index links.

**What does not exist in this commit:**
- third-party wheel binaries themselves.

This commit intentionally does **not** pretend that vendored `.whl` files were embedded when they were not physically available in the execution environment.

---

## Why this exists
The repo has already demonstrated that lack of network access can block:
- `pytest` installation,
- dev/test bootstrap,
- and full-certification style audit passes.

The goal of this bundle is to remove PyPI/network dependence from:
- runtime bootstrap,
- developer bootstrap,
- test bootstrap,
- and future agent-driven audits.

---

## Bundle layout

### Runtime wheelhouse
- `vendor/wheels/runtime/`

Required runtime/build package family:
- `setuptools`
- `wheel`
- `numpy`
- `PyYAML`

Optional GUI package family:
- `flask`

### Dev/test wheelhouse
- `vendor/wheels/dev/`

Expected dev/test package family:
- `pytest`
- `ruff`
- `mypy`
- optional duplication of `flask` when GUI tests run from dev bootstrap

### Machine-readable manifest
- `vendor/manifests/offline_dependency_bundle_v1.yaml`

### Bootstrap scripts
- `tools/bootstrap/bootstrap_offline_runtime.sh`
- `tools/bootstrap/bootstrap_offline_dev.sh`

---

## How it works

### Runtime bootstrap
```bash
bash tools/bootstrap/bootstrap_offline_runtime.sh
```

The script:
1. verifies that the required runtime/build wheels exist locally,
2. installs `setuptools` and `wheel` from the local runtime wheelhouse,
3. installs the package with `--no-index` and `--find-links vendor/wheels/runtime`,
4. optionally installs GUI extras if matching wheels are present,
5. refuses to pretend success when required wheels are missing.

### Dev/test bootstrap
```bash
bash tools/bootstrap/bootstrap_offline_dev.sh
```

The script:
1. verifies runtime/build + dev wheel presence,
2. installs `setuptools` and `wheel` from the local runtime wheelhouse,
3. installs the package with `.[dev]` using only local wheelhouses,
4. optionally installs `.[dev,gui]` if local `flask` wheels are present,
5. refuses to pretend success when required wheels are missing.

---

## Operational rule
This bundle is considered **valid** only when the wheel files referenced by the manifest are physically present under the expected `vendor/wheels/...` paths.

Scaffold-only state is useful for:
- deterministic repo structure,
- documentation,
- agent navigation,
- and future direct population of wheels,

but it is **not** equivalent to a fully populated offline wheelhouse.

---

## Expected next step
Populate:
- `vendor/wheels/runtime/`
- `vendor/wheels/dev/`

with the exact wheel files matching the manifest and target Python/platform matrix.

Recommended first target matrix:
- CPython 3.11+
- Linux x86_64

Optional later extensions:
- Windows
- macOS

---

## Success criterion
The offline dependency bundle is complete when a clean machine can run:

```bash
bash tools/bootstrap/bootstrap_offline_runtime.sh
bash tools/bootstrap/bootstrap_offline_dev.sh
pytest -q
```

without touching the network.
