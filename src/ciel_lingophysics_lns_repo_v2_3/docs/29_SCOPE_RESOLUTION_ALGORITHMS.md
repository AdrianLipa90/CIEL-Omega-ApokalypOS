# 29. Scope Resolution Algorithms

Version: v1.5

The scope resolver turns surface quantifier/negation patterns into canonical logical and lingophysical forms.

## Pipeline

```text
surface sentence
→ detect quantifier surface
→ detect negation surface
→ infer negation position
→ attach to predicate valency frame
→ normalize scope
→ compute scope phase
→ guard equivalence
```

## Core algorithm

```python
q = encode_quantifier(surface_or_name)
expr = normalize_scope(q, predicate, negation_position)
```

Negation positions:

```text
none                no negation operator
outside_quantifier  ¬Q(x)P(x)
inside_predicate    Q(x)¬P(x)
quantifier_negative negative quantifier such as no/żaden/nikt
```

## Equivalence guard

Two statements are not equivalent unless:

```text
predicate_frame_equal
roles_equal
TAM-E compatible
polarity compatible
scope_signature compatible
```

The guard rejects false equivalences such as:

```text
Not every X is P  ≠  No X is P
Some X are not P  ≠  No X is P
Every X is not P  ≠  Not every X is P
```

## Fallback rule

If scope resolution cannot determine the position of negation, the output must be:

```text
scope_status: unresolved
```

not a guessed normalized form.
