# Dynamic Deictic Operators

Version: v1.2 local patch

## Thesis

Words such as **gdzieś**, **kiedyś**, **jakoś**, **dokądś**, and **skądś** are not ordinary concept cards. They are dynamic operators that introduce unresolved anchors into the semantic field.

They do not name a stable object. They open a variable:

```text
gdzieś   -> ∃x ∈ Place, unresolved location anchor
kiedyś  -> ∃t ∈ Time, unresolved temporal anchor
jakoś   -> ∃m ∈ Manner, unresolved method/manner anchor
skądś   -> ∃s ∈ Source, unresolved origin anchor
dokądś  -> ∃d ∈ Destination, unresolved goal-location anchor
```

## Formal form

A dynamic deictic operator is represented as:

```text
D = (domain, anchor_type, resolution_state, scope, context_dependency)
```

The generic resolution equation is:

```text
Resolve(D, C) -> anchored_variable | unresolved_anchor
```

where `C` is context, memory, grammar, goal, and active discourse frame.

## Why this matters

Mapping these words too early into precise locations or times creates false precision. In CIEL-LNS/Ω the unresolved state is meaningful and must be preserved until the context legitimately resolves it.

```text
Surface similarity is not enough.
Resolution state is part of meaning.
```

## Cross-linguistic note

Polish can compactly encode indefinite deictic force through forms like `gdzieś`, `kiedyś`, `jakoś`, `skądś`, `dokądś`. English, German, French, and Spanish often distribute the same force over adverbs, pronoun-like forms, phrases, and modal context.

Therefore:

```text
indefinite deictic operator ≠ simple adverb
indefinite deictic operator = dynamic unresolved anchor
```
