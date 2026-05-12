# Dynamic Deixis Resolution Algorithms

Version: v1.2 local patch

## Pipeline

```text
surface form
-> detect dynamic deictic operator
-> determine operator family
-> attach variable anchor
-> inspect grammar/case/preposition gauge
-> inspect tense/aspect/modal scope
-> inspect context and memory
-> resolve or preserve unresolved state
```

## Spatial indefinite

```text
Somewhere(E) -> ∃x∈Place : Located(E,x) ∧ resolution(x)<1
```

If context contains a bounded spatial frame, e.g. `in the house`, the anchor becomes constrained:

```text
Somewhere(E) + InFrame(house) -> ∃x∈Interior(house)
```

## Temporal indefinite

```text
Sometime(E) -> ∃t∈Time : Occurs(E,t) ∧ resolution(t)<1
```

`kiedyś` is especially important because it may point backward or forward depending on tense, aspect, memory, and intention:

```text
Kiedyś to zrobiłem.  -> past memory anchor
Kiedyś to zrobimy.  -> future goal anchor
```

## Negative dynamic anchors

Negative deictics collapse the existential anchor under active domain:

```text
Nowhere(E) -> ¬∃x∈Place : Located(E,x)
Never(E)   -> ¬∃t∈Time  : Occurs(E,t)
```

The domain must be explicit. `Nigdy` without a domain can be rhetorical, existential, autobiographical, legal, or local to a conversation.

## Free-choice dynamic anchors

```text
Anywhere(E) -> free-choice x∈Place
Anytime(E)  -> free-choice t∈Time
```

These interact with modal operators such as `can`, `may`, `must`, `allowed`, and `possible`.

## Preservation rule

If context cannot resolve the anchor, CIEL-LNS must preserve it as unresolved rather than hallucinating precision.

```text
UnresolvedAnchor is a valid semantic state.
```
