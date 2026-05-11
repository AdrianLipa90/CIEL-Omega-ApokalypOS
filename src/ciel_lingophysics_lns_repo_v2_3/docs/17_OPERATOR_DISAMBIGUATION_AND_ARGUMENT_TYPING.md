# Operator Disambiguation and Argument Typing

Operator meaning is selected by context and argument types.

## Example: `have / mieć`

```text
Jan ma psa.           -> Own/AlienablePossession(John,dog)
Jan ma oczy.          -> HasPart(John,eyes)
Woda ma temperaturę.  -> HasProperty(water,temperature)
Jan ma problem.       -> HasState(John,problem)
Ona ma wpływ.         -> HasRelation(she,influence)
```

Formal selection:

\[
Mode(Have,x,y)=\arg\max_m Score(m|type(x),type(y),context)
\]

## Example: `jak / how / as / like`

```text
Jak to działa?             -> How(T) -> Ask(Manner(T))
Działa jak silnik.         -> Like(x,y) -> Sim(x,y)
Pracuje jako lekarz.       -> AsRole(x,role)
Zrób to jak wcześniej.     -> PatternMap(previous -> current)
Jak przyjdziesz, zadzwoń.  -> WhenIf(S1,S2)
```

## Required disambiguation dimensions

- surface form,
- language,
- part of speech,
- argument types,
- local syntax,
- context window,
- semantic axis,
- known dual/inverse operators,
- operator family.

## Minimum implementation

The initial implementation is intentionally rule-based. Statistical disambiguation can be added later as a correction layer, not as the foundation.
