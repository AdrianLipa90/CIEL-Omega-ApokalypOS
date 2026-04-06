# Immutability Policy

## Purpose
This file governs the CIEL Ethics and Semantic Action Algorithm across repositories.

## Immutable core
The following files are immutable-core contract files:
- `contracts/CIEL_ETHICS_AND_SEMANTIC_ACTION_ALGORITHM.md`
- `contracts/relational_contract.yaml`
- `contracts/AUDIT_SCHEMA.yaml`

They are shared invariants and may not be silently weakened repository by repository.

## Allowed change modes
Changes are allowed only through:
1. explicit version bump,
2. signed architectural decision,
3. new appendix that extends but does not weaken the core,
4. canonical replacement package reviewed as a contract change.

## Forbidden change modes
Forbidden:
- local weakening of truth rules,
- changing penalties silently,
- removing audit channels silently,
- inverting truth-over-smoothing priority,
- collapsing online structural truth into post-hoc audit truth.

## Appendix rule
Repo-local additions belong in `contracts/appendices/`.
Appendices may specialize observables, bindings, and thresholds, but may not weaken the immutable core.

## Current companion files
- `contracts/SEMANTIC_ACTION_REFERENCE_CARD.md`
- `contracts/appendices/`
