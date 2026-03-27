# GitHub Workflows

## Role

This folder stores GitHub Actions workflows used by the SOT integration layer.

## Current workflows

- `gh_repo_coupling.yml` — runs every 15 minutes and on manual dispatch, executes `scripts/run_gh_repo_coupling.py`, and commits refreshed live coupling artifacts when state changes are detected.

## Structural rule

Workflows in this folder should remain operationally explicit:
- the trigger should be clear,
- the executed entrypoint should be named explicitly,
- the written files should be auditable,
- hidden architectural logic should not live only in YAML.
