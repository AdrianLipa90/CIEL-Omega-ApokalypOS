# CIEL-LNS/Ω v1.4: TAM-E Layer

TAM-E means **Tense, Aspect, Mood, Modality, and Evidentiality**.

After predicate valency tells us which roles a predicate licenses, TAM-E tells us how the event is placed in time, how it unfolds, whether it is asserted, commanded, imagined, required, possible, inferred, witnessed, reported, or unknown.

In CIEL-LNS/Ω, TAM-E is not surface grammar decoration. It is a phase and truth-status operator layer.

```text
EventFrame + CaseGauge + TAM-E = grammatical event state
```

## Core distinction

```text
tense        locates event time
aspect       shapes event internal contour
mood         sets assertion/command/condition/hypothesis mode
modality     sets possibility/necessity/permission/obligation
 evidentiality marks the source/status of knowledge
```

## Formal state

For an event `E`, define:

```text
TAME(E) = (Tense, Aspect, Mood, Modality, Evidentiality)
```

A full event state becomes:

```text
EventState = PredicateFrame(roles) + CaseGauge(surface roles) + TAME(E)
```

Or:

```text
Ψ_event = Frame(P, roles) ⊗ CaseGauge ⊗ TAME ⊗ Context ⊗ Memory
```

## Why this matters

The following are not equivalent:

```text
She writes.
She wrote.
She has written.
She would write.
She must write.
Apparently, she wrote.
I saw that she wrote.
```

The predicate may remain `Write(Agent, Content?)`, but TAM-E changes the event phase, epistemic status, and purpose/operator trajectory.

## Cross-language mapping

Languages distribute TAM-E differently:

- English uses auxiliaries and word order heavily.
- Polish encodes aspect lexically/morphologically through perfective and imperfective verb pairs.
- Spanish separates `ser/estar` and uses rich tense/mood morphology.
- French uses auxiliary constructions and mood distinctions.
- German uses auxiliaries, modal verbs, and clause structure.

Thus TAM-E is a cross-language gauge layer, not merely a list of tenses.

## CIEL rule

```text
TAM-E operators modify the phase of an event, not merely its surface form.
```

A tense/aspect/mood mismatch can preserve the same concept and predicate while breaking event equivalence.

## Event equivalence with TAM-E

Two event statements are equivalent only if their predicate roles and TAM-E signatures match within a permitted transformation:

```text
Equiv_event(S1,S2) ⇔
  Frame(S1) ≅ Frame(S2)
  ∧ Roles(S1) ≅ Roles(S2)
  ∧ TAME(S1) ≈ TAME(S2)
  ∧ Polarity(S1) = Polarity(S2)
```

## TAM-E as phase operator

Let each TAM-E dimension contribute a phase:

```text
φ_event = φ_tense + φ_aspect + φ_mood + φ_modality + φ_evidentiality
```

Then:

```text
E_state = E_core · exp(i φ_event)
```

This allows CIELingo to detect that two sentences share the same predicate but differ in event phase.
