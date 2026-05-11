# v1.5 Scope, Quantifier and Negation Patch Report

## Added

- Scope, quantifier and negation layer.
- Quantifier signatures for ALL, EACH, SOME, MANY, FEW, ONE, NO and ANY.
- Cross-lingual surface forms for PL/EN/DE/FR/ES.
- Normalization rules for `not all`, `all not`, `not some`, `some not`, and negative quantifiers.
- False-equivalence guards for scope-sensitive statements.
- Python scope resolver and tests.

## Core result

```text
not all != none
some not != none
all not == none only under same domain and predicate
unresolved scope is a valid state
```

## Epistemic status

Curated seed. No external dictionary import.
