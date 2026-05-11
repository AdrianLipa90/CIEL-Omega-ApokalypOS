# CIEL-LNS/Ω v0.9 — Lingophysical Operator Algebra

## Core correction

A lexical item is not automatically a concept. In CIEL-LNS/Ω, ordinary lexical surfaces are separated into at least two canonical layers:

```text
CONCEPT_CARD    semantic body / attractor / mass-bearing object
OPERATOR_CARD   function acting on concept cards, operators, clauses or contexts
```

The practical form of lingophysics is therefore:

\[
\mathcal{L}_{phys}=(\mathcal{C},\mathcal{O}p,\mathcal{R},\circ,\otimes,\neg,\phi)
\]

where:

- \(\mathcal{C}\) is the library of concept cards,
- \(\mathcal{O}p\) is the library of operator cards,
- \(\mathcal{R}\) is the relation graph,
- \(\circ\) is operator composition,
- \(\otimes\) is structural coupling,
- \(\neg\) is polarity inversion,
- \(\phi\) is semantic phase.

## Concept mass vs operator power

Concepts carry semantic mass:

\[
m_s(c) \ge 0
\]

Operators carry structural power / curvature:

\[
\kappa(Op)=f+structural\_power+ambiguity+composition\_depth+cross\_language\_variance
\]

Thus:

```text
water / woda      -> semantic mass
inside / wewnątrz -> topological operator
have / mieć       -> polymorphic attachment operator
how / jak         -> polyfunctional mapping operator
not / nie         -> phase inversion operator
```

## Sentence as operator application

A sentence is not a bag of words. It is an operator expression over concepts.

```text
The glass contains water.
```

\[
Contains(Glass,Water)
\]

```text
Water is inside the glass.
```

\[
Inside(Water,Glass)
\]

The two expressions are dual:

\[
Contains(y,x) \Leftrightarrow Inside(x,y)
\]

The surface changes, but the topological containment invariant is preserved.

## Required fields for operator cards

Every operator card should define:

```yaml
id: op:core:inside
family: containment
operator_type: spatial_topological
arity: 2
signature: Inside(x, y) -> Relation
argument_types:
  x: [object, substance, person, concept]
  y: [container, place, body, system, concept]
dual: op:core:contain
inverse: op:core:outside
phase_axis: spatial_containment
composition_rules: [...]
surfaces:
  pl: {lemma: wewnątrz, forms: [wewnątrz, w środku, w]}
  en: {lemma: inside, forms: [inside, within, in]}
```

## Rule

```text
Concept cards are masses. Operator cards are forces. Grammar is geometry. Sentences are trajectories.
```
