# 24. Predicate Valency and Event Frames

CIELingo v1.3 adds a predicate-valency layer. The point is simple: before case, word order, preposition, clitic, or context realizes a relation, the predicate already constrains what roles may exist.

```text
Predicate -> allowed semantic roles -> language-specific realization
```

A Polish case ending can compress a role. English may reconstruct the same role by word order or a preposition. Spanish and French often use prepositions. German partly preserves case. None of these are identical surfaces, but they can share one event-frame invariant.

## Canonical event frame

```text
Frame = (Predicate, Arity, RequiredRoles, OptionalRoles, RealizationStrategies)
```

Example:

```text
Give(Agent, Theme, Recipient)
```

Polish may realize this as:

```text
Agent-Nom + dać + Recipient-Dat + Theme-Acc
```

English may realize it as:

```text
Agent + give + Recipient + Theme
Agent + give + Theme + to Recipient
```

The invariant is not the surface. The invariant is the valency frame.

## Why this layer matters

Case without valency is underdetermined. Word order without valency is brittle. Prepositions without valency are ambiguous. Valency is the skeleton; case and word order are local skin.

## Core rule

```text
case_gauge(role) must be checked against predicate_valency(predicate)
```

A role is valid only if the predicate frame allows it or the construction explicitly coerces it.
