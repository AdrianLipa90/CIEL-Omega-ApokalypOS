# Declaration vs Implementation Matrix

This document records where repository documentation and structure are aligned, transitional, stale, or still planned-only.

## Status keys

- **implemented** — the declaration matches a real present surface.
- **implemented_transitional** — the declaration is true, but the repo is in a deliberate migration state.
- **incomplete_doc** — the implementation exists, but the docs do not describe it adequately.
- **stale_doc** — the docs point to the wrong path or wrong execution surface.
- **declared_future** — the docs describe a target geometry that does not yet exist.
- **scope_limited** — the surface exists, but validation for this review was intentionally limited.

## Current matrix

| Area | Declared in | Status | Reality |
|---|---|---:|---|
| Native synchronization kernel | `README.md`, `AGENT.md` | implemented | Present in `src/ciel_sot_agent/repo_phase.py` and `src/ciel_sot_agent/synchronize.py`. |
| GH coupling subsystem | `README.md`, `docs/INDEX.md` | implemented | Present in v1 and v2 code plus workflow automation. |
| Orbital bridge subsystem | `README.md`, `docs/INDEX.md` | implemented | Present in `src/ciel_sot_agent/orbital_bridge.py` and related reports. |
| GUI web interface | `README.md`, `docs/INDEX.md` | implemented | Present in `src/ciel_sot_agent/gui/` and exposed as `ciel-sot-gui`. |
| GGUF model manager | `packaging/README.md`, `docs/INDEX.md` | implemented | Present in `src/ciel_sot_agent/gguf_manager/`. |
| Local Sapiens client wrapper script | `docs/INDEX.md`, `docs/Orbitrary shifts.md` | stale_doc | `scripts/run_sapiens_client.py` does not exist; the real surface is `ciel-sot-sapiens-client` and `src/ciel_sot_agent/sapiens_client.py`. |
| Core-only helpers under `scripts/` | `docs/CORE_ONLY_PIPELINE_BRANCH.md` | stale_doc | Actual files live under `tools/core_only/`. |
| Workflow layer as only GH coupling | `docs/OPERATIONS.md`, `.github/workflows/README.md` | incomplete_doc | Repo has four workflows: CI, runtime pipeline, package, GH coupling. |
| Top-level repo map | `README.md`, `docs/INDEX.md` | incomplete_doc | Native package layer is described, but embedded/imported sectors are not surfaced clearly enough. |
| Governance normalized target | `governance/README.md` | declared_future | `governance/agents/` is named as target geometry but is not present. |
| Legacy + target integration geometry | `integration/indices/README.md`, `integration/registries/README.md` | implemented_transitional | Legacy flat integration paths coexist with target geometry paths during migration. |
| Package executable surface | `pyproject.toml` | implemented | The installed surface includes console scripts for sync, GH coupling, validators, orbital bridge, pipeline, Sapiens client, runtime ingest, GUI, and GGUF install. |
| Android runtime/device validation | `packaging/android/README.md`, `.github/workflows/package.yml` | scope_limited | Build sources and workflow are present; device/runtime validation remains out of scope for this review package. |

## Immediate documentation repair priorities

1. Replace stale Sapiens client wrapper references with the real console script and module path.
2. Replace stale core-only script paths with `tools/core_only/*`.
3. Document all four current GitHub workflows.
4. Surface the repo as hybrid: native package + integration state + operational layer + embedded/imported sectors.
5. Keep migration geometry explicit instead of implying the legacy paths are accidental duplicates.
