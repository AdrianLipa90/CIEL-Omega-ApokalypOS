# 25. Ontological Aspect and Being Operators

This patch adds an ontological-aspect layer for distinctions such as Japanese `koto/mono` and Spanish `ser/estar`.

These are not mere vocabulary quirks. They are language-specific operators for objecthood, conceptuality, identity-being, state-being, location, and event/fact nominalization.

## Koto / Mono

Japanese `mono` tends toward concrete or object-like thinghood:

```text
Mono(x) -> ConcreteOrObjectLikeThing(x)
```

Japanese `koto` tends toward abstract event, fact, situation, or proposition:

```text
Koto(p/e) -> AbstractEventFactOrProposition(p/e)
```

This is a koto-mono axis:

```text
object-like thing <-> event/fact/concept-like matter
```

## Ser / Estar

Spanish splits English/Polish `be` into at least two major operators:

```text
Ser(x,y)   -> IdentityBe(x,y)
Estar(x,s) -> StateBe(x,s,t?) or LocationBe(x,l,t?)
```

Important precision: `ser` is not simply permanent and `estar` is not simply temporary. The better split is identity/class/role/origin versus state/location/result condition.

## Cross-language mapping

English and Polish often collapse these distinctions into one surface `be/być`. CIELingo therefore treats them as polyfunctional operators that must be resolved by complement type, case, adjective, preposition, event frame, and context.

```text
EnglishBe -> Resolve(IdentityBe | StateBe | LocationBe | ExistenceBe)
PolishByć -> Resolve(IdentityBe | StateBe | LocationBe | ExistenceBe)
SpanishSer -> IdentityBe
SpanishEstar -> StateBe | LocationBe
JapaneseKoto -> AbstractEventFact
JapaneseMono -> ConcreteThing
```

## Core rule

```text
being is not one operator; being is an operator family.
```

That family must be catalogued before translation, otherwise identity and state get collapsed into one flat semantic puddle.
