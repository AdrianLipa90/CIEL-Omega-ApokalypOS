# Operator Composition Rules

## Duality

A dual operator pair preserves a core invariant while reversing orientation or focus.

\[
Inside(x,y) \Leftrightarrow Contains(y,x)
\]

\[
Before(x,y) \Leftrightarrow After(y,x)
\]

\[
From(x,y) \Leftrightarrow To(y,x)
\]

## Inversion and negation

Negation is not always the same as inverse.

\[
Not(Inside(x,y)) \neq Outside(x,y)
\]

because `not inside` may mean outside, on boundary, unknown location, partial containment, or impossible containment depending on context.

CIEL therefore distinguishes:

```text
dual       orientation-preserving invariant pair
inverse    opposite relation in the same semantic axis
negation   logical denial or polarity inversion
```

## Higher-order operators

Adverbs and modals act on operators rather than objects:

\[
Quickly(Run(x))
\]

\[
Must(Do(agent,action))
\]

## Composition safety

Composition must preserve argument typing:

\[
Op_2(Op_1(x,y)) \text{ is valid only if } codomain(Op_1) \subset domain(Op_2)
\]

## Euler phase constraints

Synonymic operator variants should be phase-aligned on their semantic axis:

\[
Syn_\xi(a,b) \Rightarrow |e^{i(\phi_a^\xi-\phi_b^\xi)}-1|<\epsilon
\]

Antonymic or inverse operators should be in approximate counterphase:

\[
Ant_\xi(a,b) \Rightarrow |e^{i(\phi_a^\xi-\phi_b^\xi)}+1|<\epsilon
\]
