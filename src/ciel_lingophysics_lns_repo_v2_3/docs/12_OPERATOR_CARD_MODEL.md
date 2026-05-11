# 12. Operator Card Model

CIEL-LNS/Ω v0.8 separates **semantic bodies** from **linguistic functions**.

A card such as `water/woda` is a `CONCEPT_CARD`: it has semantic mass, an attractor, multilingual surfaces, contexts and relations.

A word such as `inside`, `contains`, `have`, `not`, `how`, `and`, `from`, or `to` is usually not a concept-body. It is an operator. It transforms, binds, localizes, phases, negates, queries, couples or routes concept cards.

Canonical split:

```text
Library = Concepts + Operators + Relations + Grammar
```

Minimal operator tuple:

```text
op = (id, family, class, symbol, arity, surfaces, equations, duals, examples)
```

A sentence becomes a composition of concept bodies and operators:

```text
Sentence = Operators(Concepts)
```

Example:

```text
Water is in the glass.
The glass contains water.
```

Surface differs, focus differs, but the topological invariant is shared:

```text
Inside(Water, Glass) ⇔ Contains(Glass, Water)
```

This is why CIEL must store `inside` and `contains` as dual operator cards, not as ordinary dictionary entries.
