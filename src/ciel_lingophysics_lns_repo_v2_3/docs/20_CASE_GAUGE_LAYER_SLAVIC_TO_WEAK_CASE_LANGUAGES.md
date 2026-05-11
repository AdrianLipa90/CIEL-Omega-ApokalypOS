# 20. Case Gauge Layer: Mapping Slavic Cases to Weak-Case Languages

## Core claim

Slavic case morphology is not just “word form decoration”. In CIEL-LNS it is a **local gauge of semantic role**: a noun form carries an operator that helps identify agency, patienthood, possession/source, recipienthood, instrumentality, location/topic, or direct address.

Universal Dependencies treats `Case` as an inflectional feature that helps specify the role of a noun phrase, while fixed-word-order languages often distinguish similar functions by position. UD also analyzes adpositions with the `case` dependency so that adpositional phrases and morphological case can be treated in a more uniform cross-linguistic way.

## Formal model

For a Slavic language `l_s`:

```text
Surface_l_s(token_with_case) -> CaseRole(token, role)
```

For a weak-case language `l_w`:

```text
CaseRole(token, role) -> Surface_l_w(token, word_order, adposition, clitic, agreement, valency)
```

The mapping is therefore not:

```text
case = preposition
```

but rather:

```text
case = hidden role-operator
preposition/word-order/clitic = target-language realization strategy
```

## Polish case operators

| Case | Polish | CIEL operator | Weak-case realization |
|---|---|---|---|
| Nom | mianownik | `SubjectOrIdentity(x)` | subject position, nominative pronoun residue |
| Acc | biernik | `DirectPatient(x)` | direct object position, object pronoun/clitic |
| Gen | dopełniacz | `OfPossessionSourcePartitive(x,y)` | `of`, possessive, `de`, partitive, negation/absence constructions |
| Dat | celownik | `RecipientBeneficiaryTarget(x)` | `to/for`, `à`, `a/para`, indirect object clitics |
| Ins | narzędnik | `InstrumentMeansComitativeRole(x)` | `with/by/using/as`, `mit/durch/von/als`, etc. |
| Loc | miejscownik | `LocationTopicFrame(x)` | `in/on/at/about`, `dans/sur/à`, `en/sobre`, selected by operator |
| Voc | wołacz | `Address(x)` | comma, intonation, address particles |

## Important warning

A case is often polyfunctional and governed by lexical valency. Therefore each mapping needs:

```text
case + governing operator + noun type + clause role + context
```

Without valency, mapping is noisy. For example Polish genitive may encode possession, absence under negation, source, measure, or partitive structure. A single English preposition cannot cover all of it.

## CIEL rule

```text
Slavic case endings are compressed role operators.
Weak-case languages reconstruct those operators with syntax, adpositions, clitics, and context.
```

That is the cross-language gauge map.
