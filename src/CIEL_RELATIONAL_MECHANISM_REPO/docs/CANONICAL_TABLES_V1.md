# Canonical Tables v1

This file freezes the current repository-facing mechanism tables for the thread.

## Scope
- Runtime source of truth: `CIEL_OMEGA_COMPLETE_SYSTEM`
- Tables are mechanism-first, not metric-first.
- Only confirmed or clearly flagged candidate/unresolved rows are allowed.

## Deliverables
- `canonical_couplings.csv`
- `canonical_symbol_runtime_pipeline.csv`
- `canonical_dependency_tables.csv`
- `canonical_tables_v1.xlsx`

## Rules
- PDF values are candidates unless directly confirmed and not superseded.
- `Sigma_i` is local fingerprint only.
- `Sigma_global` is not assumed in runtime.
- `D_f` remains unresolved.
- `A_ij` remains toy-model notation for an effective pair-connection kernel.

## Interpretation
The goal of these tables is to answer:
1. What couples to what?
2. Which runtime object is the canonical target?
3. Which pipeline layer does it belong to?
4. What remains unresolved?
