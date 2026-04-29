# Immutability Policy

## Purpose

This file defines how the CIEL Ethics and Semantic Action Algorithm is governed across repositories.

## Immutable core

The following files are treated as immutable core contract files:
- `contracts/CIEL_ETHICS_AND_SEMANTIC_ACTION_ALGORITHM.md`
- `contracts/relational_contract.yaml`

They are shared invariants.
They are not to be silently rewritten repository by repository.

## Allowed change modes

Changes to the immutable core are allowed only through one of the following:

1. explicit version bump,
2. signed architectural decision,
3. new appendix that extends but does not weaken the core,
4. canonical replacement package reviewed as a contract change.

## Forbidden change modes

The following are forbidden:
- ad hoc local weakening of truth rules,
- changing penalties without explicit declaration,
- removing audit channels silently,
- altering the output discipline silently,
- repository-local edits that invert the ethical ordering.

## Extension rule

Repository-local specialization must be written in:
- `contracts/appendices/AUDIT_APPENDIX_<repo>.md`

Such appendices may:
- add local metrics,
- add repo-specific test surfaces,
- add domain-specific observables,
- refine thresholds.

Such appendices may not:
- authorize lying,
- authorize hidden uncertainty,
- authorize hallucination as acceptable default behavior,
- weaken truth-over-smoothing.

## Interpretation hierarchy

When documents disagree, the preferred order is:

1. immutable core contract,
2. machine-readable parameter file,
3. explicit appendix,
4. repository-local operational notes,
5. legacy or stale surfaces.
