# Operator Taxonomy

CIEL-LNS/Ω v0.9 divides functional words into cataloguable operator families.

| Family | Canonical function | Examples PL | Examples EN | Formal sketch |
|---|---|---|---|---|
| identity | identity / being | jest, to, być | is, be | `Be(x)`, `Equals(x,y)` |
| possession | attachment / ownership / property | ma, posiada | has, owns | `Have(x,y)` |
| containment | interior / inclusion | w, wewnątrz, zawiera | in, inside, contains | `Inside(x,y)`, `Contains(y,x)` |
| spatial | relative position | na, pod, nad, obok | on, under, above, near | `SpatialRel(x,y)` |
| temporal | order in time | przed, po, kiedy | before, after, when | `TemporalRel(e1,e2)` |
| logical | logic gates | i, albo, nie, jeśli | and, or, not, if | `And`, `Or`, `Not`, `IfThen` |
| causal | causality | bo, ponieważ, przez | because, due to, by | `Cause(x,y)` |
| modal | possibility / necessity | może, musi, powinien | may, must, should | `Modal(Op)` |
| comparison | similarity / role / pattern | jak, jako, niż | how, like, as, than | `Like(x,y)`, `As(x,y)` |
| transformation | state change | staje się, tworzy, niszczy | becomes, creates, destroys | `Transform(x,y)` |
| epistemic | knowledge status | wie, sądzi, wątpi | knows, believes, doubts | `EpiState(agent,p)` |
| affective | affective relation | kocha, boi się, ufa | loves, fears, trusts | `Affect(agent,target)` |
| consensus | agreement / dispute | zgadza się, przeczy | agrees, denies | `ConsensusRel(q,p)` |

## Arity classes

\[
Op^{(0)}, Op^{(1)}, Op^{(2)}, Op^{(3)}, Op^{(n)}, Op^{(Op)}
\]

- nullary: interjections, impulses,
- unary: `Not(x)`, `Must(T)`, `Very(P)`,
- binary: `Inside(x,y)`, `Contains(x,y)`,
- ternary: `Give(agent,object,recipient)`,
- higher-order: adverbs and modals acting on operators.

## Polymorphic operators

Some surfaces map to multiple formal modes. These must be represented as operator families, not single flat entries.

Example:

```text
ma / has
```

\[
Have(x,y) \rightarrow \{Own, HasPart, HasProperty, HasState, HasRelation\}
\]

Example:

```text
jak / how / like / as
```

\[
Jak \rightarrow \{How, Like, AsRole, PatternMap, WhenIf\}
\]
