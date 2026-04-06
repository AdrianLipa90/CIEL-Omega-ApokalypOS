# Changelog

All notable changes to this repository will be documented in this file.

The format is based on Keep a Changelog and the project follows Semantic Versioning.

## [0.1.0] - 2026-04-01
### Added
- Root `pyproject.toml` so the repository is installable via `pip install -e .`.
- CLI entry points for synchronization, GitHub coupling, validators, orbital bridge, and Sapiens client.
- CI workflow for pull requests and pushes to `main` that runs install, lint, and test gates.
- `ruff` and `mypy` baseline configuration for the canonical package.
- Production readiness protocol and release gate contract.

### Changed
- Declared runtime dependency on `PyYAML`.
- Clarified repository status by distinguishing tested logic from production release readiness.
