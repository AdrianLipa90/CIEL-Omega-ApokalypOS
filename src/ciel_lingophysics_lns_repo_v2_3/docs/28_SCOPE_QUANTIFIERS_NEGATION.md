# 28. Scope, Quantifiers and Negation Layer

Version: v1.5

This layer formalizes how quantifiers and negation act as scope operators rather than ordinary lexical concepts.

The central warning is:

```text
not all != none
some not != none
all not == none only under a restricted predicate-domain reading
```

In CIEL-LNS/Ω, scope is represented as an ordered operator stack:

```text
ScopeStack(S) = [Q, Neg, TAM-E, PredicateFrame, CaseGauge, Context]
```

A sentence is not equivalent to another sentence unless its predicate frame, roles, polarity, TAM-E signature and scope signature are compatible.

## Canonical examples

```text
PL: Nie każdy człowiek wie.
EN: Not every human knows.
FORM: ¬∀x Human(x) => Know(x)
NORM: ∃x Human(x) ∧ ¬Know(x)
```

```text
PL: Żaden człowiek nie wie.
EN: No human knows.
FORM: ∀x Human(x) => ¬Know(x)
NORM: ¬∃x Human(x) ∧ Know(x)
```

These are not equivalent.

## Scope phase

Each quantifier and negation placement receives a phase contribution. Two statements may have similar surface content but different scope phase and therefore different semantic trajectory.

```text
φ_scope = φ_quantifier + φ_negation_position + φ_focus + φ_domain
```

## Cross-language mapping

Languages without rich case or with fixed word order often surface scope through word order, auxiliaries, negative polarity items, determiners or prosody. The canonical CIEL representation must therefore be based on normalized scope structure, not surface token order alone.
