# NL-WIJ-0005 — WijCouplingOptimizer

## Identity
- **card_id:** `NL-WIJ-0005`
- **name:** `WijCouplingOptimizer`
- **class:** `orbital_coupling_optimizer`
- **active_status:** `ACTIVE_CANONICAL_COUPLING_OPTIMIZER`

## Anchors
- `scripts/optimize_wij.py`
- `integration/Orbital/main/manifests/couplings_global.json`
- `integration/Orbital/main/metrics.py`

## Role
Canonical W_ij coupling matrix optimizer. Minimizes closure_penalty via composite L-BFGS-B objective over scalar inter-sector coupling weights. Targets closure_penalty < 5.20 and coherence_index > 0.76 to exit safe-mode and enter standard/deep orbital execution.

## Flow
- **input_from:** `sectors_global.json + couplings_global.json (baseline) + EBA observables from last bridge report`
- **output_to:** `optimized couplings_global.json with reduced closure_penalty and updated _optimizer_metadata`

## Authority
### May
- minimize closure_penalty via L-BFGS-B over inter-sector coupling weights
- write optimized couplings_global.json only when `--write` flag explicitly passed
- report optimization delta as advisory result

### Must not
- override baseline couplings without explicit `--write` invocation
- be treated as canonical source of truth for couplings (baseline JSON is)
- replace EBA loop evaluations as primary coherence signal

## Horizon relation
Pre-bridge optimization layer; outputs feed directly into orbital runtime without passing through projection horizon.

## Authority rule
Optimizer outputs are advisory coupling adjustments. Baseline couplings_global.json is the source of truth; optimized values replace it only when --write flag is explicitly passed.

## Optimization history
| date | baseline_closure | optimized_closure | delta | health_before | health_after |
|---|---|---|---|---|---|
| 2026-04-14 | 6.0956 | 5.0351 | −1.0605 | 0.472 | 0.503 |
