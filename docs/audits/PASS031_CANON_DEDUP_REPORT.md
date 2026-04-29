# PASS 031 — Canon deduplication report

## Action taken

The repository contained a parallel Omega source surface under:
- `integration/Orbital/main/data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega`

and a parallel relational mechanism source surface under:
- `integration/Orbital/main/src/ciel_relational_mechanism`

Canonical roots are now:
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega`
- `src/CIEL_RELATIONAL_MECHANISM_REPO/src/ciel_relational_mechanism`

## Consolidation policy

- Files that existed **only** in the mirror were copied into the canonical source tree.
- Overlapping files were resolved in favor of the canonical `src/` tree.
- `integration/Orbital/main/registry.py` was retained only as a compatibility shim and now forwards to the canonical implementation.
- Duplicate generated report artifact `integration/reports/sapiens_client/runtime_gating.json` was removed when identical to the orbital bridge copy.

## Important limitation

Generated registries and exported import maps may still mention legacy mirror paths. Those generated artifacts should be regenerated in a later pass if full path-level registry purity is required.

## Canon uplift

The canonical orbital model was extended to absorb integration-only operational fields:
- `mu_eff`
- `winding`
- `tau_orbit`
- `phase_slip_ready`
- `orbit_stability`

This removes one more reason for the integration layer to keep a richer parallel model.

## Validation

Passed after consolidation:
- `tests/test_main.py`
- `tests/test_braid_nonlocal_coupling.py`
- `tests/test_orbital_runtime.py`
- `tests/test_orbital_semantics.py`
