# GitHub Workflows

## Role

This folder stores GitHub Actions workflows used by the SOT integration layer.

The repository currently uses workflows for four distinct purposes:
- lint and test quality gates,
- runtime smoke and packaging checks,
- scheduled live GH coupling refresh,
- build artifact production.

## Current workflows

- `ci.yml` — installs development dependencies, runs Ruff, then runs pytest.
- `runtime_pipeline.yml` — performs editable-install smoke execution, builds a wheel, reinstalls from wheel, and re-runs selected runtime surfaces.
- `package.yml` — builds the Debian package and Android APK, then uploads produced artifacts.
- `gh_repo_coupling.yml` — runs on a 15 minute schedule and manual dispatch, executes `scripts/run_gh_repo_coupling.py`, and commits refreshed integration artifacts when state changes.

## Structural rule

Workflows in this folder should remain operationally explicit:
- the trigger should be clear,
- the executed entrypoint should be named explicitly,
- the written files should be auditable,
- hidden architectural logic should not live only in YAML.

## Documentation rule

Whenever a workflow is added, removed, or substantially repurposed, update:
- this file,
- `docs/OPERATIONS.md`,
- and `docs/INDEX.md` if the workflow affects the visible operational surface.
