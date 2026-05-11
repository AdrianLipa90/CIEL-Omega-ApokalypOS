# 21. Case Gauge Algorithms

## Algorithm 1: decode Slavic case

Input:

```text
token, lemma, morphological_case, governing_operator, context
```

Output:

```text
CaseRole(token, role, confidence)
```

Steps:

1. Read morphological `Case`.
2. Read the governing verb/adposition/operator.
3. Resolve valency.
4. Resolve noun animacy/personhood if relevant.
5. Return canonical CIEL case operator.

## Algorithm 2: encode into weak-case language

Input:

```text
CaseRole(token, role), target_language
```

Output:

```text
surface strategy: word order / preposition / clitic / agreement / punctuation
```

Steps:

1. Select the target language grammar profile.
2. Choose primary realization strategy.
3. Insert adposition or clitic if needed.
4. Place noun phrase according to target syntax.
5. Preserve predicate-argument invariant.

## Algorithm 3: check cross-language equivalence

Two sentences are compatible if:

```text
PredicateArgumentInvariant(S1) == PredicateArgumentInvariant(S2)
CaseRoleInvariant(S1) == CaseRoleInvariant(S2)
Polarity(S1) == Polarity(S2)
CoreFocusDrift(S1,S2) < epsilon_focus
```

Example:

```text
PL: Pies gryzie kota.
EN: The dog bites the cat.
Equation: Bite(Agent=dog, Patient=cat)
```

Polish can move constituents more freely because `pies` and `kota` carry role information. English must lean harder on word order.
