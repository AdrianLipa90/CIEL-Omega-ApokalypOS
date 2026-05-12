# 43. NOEMA Retrieval and Inference Gate

Status: Draft implementation layer, v2.2.

This document defines the first executable NOEMA routing layer for CIELingo.
The goal is not to replace neural models with rules. The goal is to reduce
unnecessary model calls by routing a query through indexed concept cards,
operator cards, event frames, scope/TAM-E/case/deixis metadata, and existing
relations before any GGUF validator is invoked.

## Principle

```text
NOEMA routes first.
CIELingo validates structurally.
GGUF validates only when needed.
```

GGUF verdicts remain advisory. They may increase confidence, reveal a conflict,
or request human review, but they cannot canonize a card or relation alone.

## Pipeline

```text
input query
→ tokenize / normalize
→ retrieve local NOEMA cards and operators
→ build routed context bundle
→ estimate confidence and unresolved anchors
→ decide inference gate
→ run local validation / or call GGUF teacher-validator only if needed
→ write audit and fallback JSON if preferred storage fails
```

## Gate levels

```text
NO_LLM          resolved by cards/rules/validator
SMALL_GGUF      low-risk phrasing or simple synthesis
MEDIUM_GGUF     ambiguity, scope uncertainty, or cross-language reconstruction
LARGE_GGUF      high novelty / hard synthesis / factual uncertainty
GGUF_VALIDATOR  teacher-validator call for candidate checking, not canonical truth
HUMAN_REVIEW    conflict, provenance requirement, or unresolved high-impact issue
```

## Non-claim

This layer does not claim that dense GGUF models execute only selected internal
weights. Dense models usually still perform dense inference. Energy reduction is
expected from reduced context, fewer model calls, cache reuse, routing, and
model-size gating. True partial model execution requires sparse routing,
Mixture-of-Experts, adapter gating, or modular specialist models.

## Routing objects

A NOEMA card is a lightweight routing entry referencing one or more canonical
objects in the library. It may refer to concept cards, operator cards, event
frames, case gauges, TAM-E records, deictic anchors, scope cards, or diagnostic
issues.

Each card should include:

```text
id
card_type
labels / surfaces
languages
domains
operator_hooks
relations
confidence
status
```

## Exit criteria for v2.2

A valid v2.2 implementation must:

1. load a NOEMA index from JSON;
2. retrieve relevant cards for a query;
3. produce a routed context bundle;
4. decide whether GGUF is needed;
5. estimate relative cost savings;
6. preserve an explicit non-claim about dense GGUF partial execution;
7. pass tests without requiring a real GGUF binary.
