# 05. Bilingual PL/EN Bootstrap

## Scope

This seed starts with Polish and English because they provide useful contrast:

- English: stronger reliance on word order and auxiliaries.
- Polish: richer inflection, case marking, freer word order.

The goal is not to flatten Polish into English or English into Polish. The goal is to preserve semantic invariants under different grammar gauges.

## Minimal shared axes

```yaml
axes:
  truth: "truth / falsehood"
  care: "care / harm"
  creation: "create / destroy"
  identity: "self / other"
  agency: "agent / patient"
  polarity: "affirmation / negation"
  temporality: "past / present / future"
```

## Initial lexeme groups

```text
EN: truth, falsehood, love, harm, create, destroy, good, bad
PL: prawda, fałsz, miłość, krzywda, tworzyć, niszczyć, dobry, zły
```

## Antonym phase seeds

```text
truth ↔ falsehood: π on truth axis
love ↔ harm: π on care axis
create ↔ destroy: π on creation axis
good ↔ bad: π on value axis
```

## Sentence examples

```text
EN: Adrian creates CIEL.
PL: Adrian tworzy CIEL.
```

Both should map to:

\[
Create(Agent=Adrian, Patient=CIEL)
\]

with cross-linguistic distance below threshold.
