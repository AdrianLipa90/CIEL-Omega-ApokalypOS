# 18. Batch Library Build Protocol

This document defines the local growth rhythm for CIELingo concept-card batches.

## Principle

A batch is not a word list. A batch is a controlled update to a growing semantic graph.

```text
NewCards -> CompareAgainstExistingCards -> TagRelations -> UpdateDB -> RecomputeGraphs -> ReportConflicts
```

## Batch sizing

- Rounds 1-3: 36 concept cards × 5 languages.
- Rounds 4-7: 20 concept cards × 5 languages.
- Later rounds: 15 concept cards × 5 languages.

The batch size shrinks because graph density increases. Each new card must be checked against all existing cards for synonymy, antonymy, dual operators, false friends, phase conflicts, and attractor membership.

## Separation rule

```text
Concept cards are semantic masses.
Operator cards are forces/functions.
Grammar is geometry.
A sentence is a trajectory.
```

Do not place functional words such as `inside`, `have`, `not`, `if`, `as/how/like`, `with`, `without` into ordinary concept-card batches. They belong to the operator library.
