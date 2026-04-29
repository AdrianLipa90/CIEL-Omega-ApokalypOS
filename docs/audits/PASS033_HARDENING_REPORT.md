# PASS033 HARDENING REPORT

## Scope

This pass hardens the baseline repository around four concrete operational defects found during end-to-end smoke checks:

1. GitHub coupling commands crashed without network access.
2. The v2 index validator expected a canonical demo integration document that was missing.
3. Runtime evidence ingest was valid but too opaque for practical use.
4. The GUI entrypoint raised a traceback on missing Flask instead of failing cleanly.

## Fixes applied

### 1. Offline fallback for GitHub coupling

Updated:
- `src/ciel_sot_agent/gh_coupling.py`
- `src/ciel_sot_agent/gh_coupling_v2.py`

Behavior now:
- catches network/URL failures,
- preserves previous HEAD state when available,
- emits structured JSON with:
  - `status: degraded_offline`
  - `offline_fallback_active: true`
  - `degraded_reasons`
  - per-upstream `status: offline_fallback`
- exits cleanly instead of crashing.

### 2. Canonical demo integration document restored

Added:
- `docs/integration/CIEL_OMEGA_DEMO_INTEGRATION.md`
- `docs/CIEL_OMEGA_DEMO_INTEGRATION.md` (legacy forwarding note)

This satisfies the missing canonical reference expected by the v2 validator.

### 3. Runtime evidence ingest clarified

Updated:
- `src/ciel_sot_agent/runtime_evidence_ingest.py`

Added:
- template generation support,
- contract/schema summary output,
- contract summary embedded in ingest report,
- starter template file:
  - `integration/runtime_modes/runtime_evidence_template.json`

New CLI capabilities:
- `ciel-sot-runtime-evidence-ingest --show-contract`
- `ciel-sot-runtime-evidence-ingest --template <path>`

### 4. GUI entrypoint fails cleanly

Updated:
- `src/ciel_sot_agent/gui/app.py`

Behavior now:
- `--help` remains available,
- missing Flask now returns a clean error message and exit code `2`,
- no traceback is required for the user to understand the issue.

## Validation

Targeted tests passed:
- `tests/test_gh_coupling.py`
- `tests/test_gh_coupling_v2.py`
- `tests/test_runtime_evidence_ingest.py`
- `tests/test_gui.py`
- `tests/test_index_validator_v2.py`
- `tests/test_main.py`

Smoke checks passed:
- `python -m ciel_sot_agent gh-coupling`
- `python -m ciel_sot_agent gh-coupling-v2`
- `python -m ciel_sot_agent runtime-evidence-ingest --show-contract`
- `python -m ciel_sot_agent runtime-evidence-ingest --template /tmp/...`
- `python -m ciel_sot_agent gui --help`
- `python -m ciel_sot_agent index-validate-v2`

## Result

The repository is materially more robust for local use:
- network-sensitive commands degrade gracefully,
- canonical doc linkage is restored,
- runtime evidence ingest is now practical to use,
- GUI startup behavior is controlled and readable.
