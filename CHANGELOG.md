# Changelog

All notable changes to this repository will be documented in this file.

The format is based on Keep a Changelog and the project follows Semantic Versioning.

## [0.2.0] - 2026-04-17
### Added
- `CIEL_CANON.py` — canonical entrypoint at project root; single source of truth for paths, metric thresholds, pipeline sequence, entity notes, and subconsciousness config.
- `src/ciel_sot_agent/subconsciousness.py` — TinyLlama 1.1B as associative background stream; adds `subconscious_note` field to every CIEL/Ω pipeline output.
- `tools/ciel_soul_invariant_ref.py` — standalone reference implementation of the Σ Soul Invariant with memory traces.
- Subconsciousness server management: `python3 CIEL_CANON.py --sub start|status`.

### Fixed
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/ciel/engine.py`: converted relative imports (`from ..`) to absolute imports to resolve `ImportError: attempted relative import beyond top-level package` when `ciel_omega/` is on `sys.path`.

### Changed
- `README.md` rewritten to reflect current pipeline architecture, metric thresholds, entity notes, and operational entry points.
- All key project documents updated to reflect CIEL/Ω end-to-end pipeline status.

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
