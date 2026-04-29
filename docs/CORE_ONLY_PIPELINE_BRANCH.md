# Core-only pipeline branch

This branch introduces a minimal bootstrap path for running and testing the CIEL core without attaching any LLM backend.

## Goal

Provide a deterministic path for:
- creating a local virtual environment,
- installing the repository-side package needed by the CIEL engine,
- running a no-LLM smoke test,
- running the repo test suite with stable import resolution.

## Scope

This branch does **not** remove existing LLM code from the repository history.
Instead, it adds an isolated `core-only` operational path that leaves the canonical runtime untouched.

## Added files

- `scripts/bootstrap_core_only.sh`
- `scripts/run_core_smoke.sh`
- `scripts/run_repo_tests.sh`

## Behavior

`bootstrap_core_only.sh`:
- creates `.venv` if needed,
- upgrades `pip`,
- installs the engine package from `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega`,
- installs `pytest` only when available or needed for local test execution.

`run_core_smoke.sh`:
- activates `.venv`,
- installs the engine package if missing,
- runs `ciel-smoke`.

`run_repo_tests.sh`:
- activates `.venv`,
- exports `PYTHONPATH=.`,
- runs `pytest -q tests`.

## Minimal usage

```bash
bash scripts/bootstrap_core_only.sh
bash scripts/run_core_smoke.sh
bash scripts/run_repo_tests.sh
```

## Notes

This is a branch-scoped operational addition intended for safe testing and further refactor work.
