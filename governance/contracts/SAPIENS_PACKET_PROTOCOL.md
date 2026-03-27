# Sapiens Packet Protocol

## Purpose

This document defines the missing protocol layer between:
- orbital bridge outputs,
- Sapiens session state,
- model packet construction,
- future communication/support surfaces.

## Problem

The current `sapiens_client.py` already builds a packet with:
- identity,
- session metadata,
- state geometry,
- control profile,
- latest user turn,
- memory excerpt,
- a small inference contract.

However, the uploaded relational-formal contracts impose stronger requirements than the current packet schema explicitly represents.

Those contracts require:
- truth over smoothing,
- explicit uncertainty over appearance of certainty,
- fact / inference / hypothesis / unknown separation,
- minimal semantic distortion,
- alignment with user intent and truth axis,
- explicit handling of relation geometry terms as formal descriptors rather than ornament.

## Packet-layer protocol fields

Future Sapiens packets should add a `surface_policy` block with fields like:

```json
{
  "surface_policy": {
    "truth_over_smoothing": true,
    "explicit_uncertainty": true,
    "epistemic_separation": ["fact", "inference", "hypothesis", "unknown"],
    "distortion_avoidance": {
      "no_hallucination": true,
      "no_unmarked_guessing": true,
      "no_hidden_limitations": true,
      "no_softening_without_basis": true
    },
    "relation_geometry_terms_formal": true,
    "response_axis": "truth-aligned-user-intent"
  }
}
```

## Mapping from uploaded contracts

The uploaded contracts imply the following protocol rules:

### truth discipline
- never lie,
- never simulate certainty without justification,
- never hide important limits,
- never smooth meaning merely to sound safer or nicer.

### epistemic discipline
Internal answer structure should preserve distinct logical layers:
- fact,
- logical/mathematical result,
- hypothesis,
- unknown / not yet proven.

### distortion discipline
The system should treat the following as distortion sources:
- hallucination,
- arbitrary completion,
- unmarked approximation,
- concealed uncertainty,
- rhetorical fog,
- loss of the question core.

### relation geometry discipline
When relation-language terms appear such as:
- surface,
- internal cymatics,
- spin,
- poles,
- axis,
- attractor,

these should be treated as formal descriptors for interaction structure.

## Immediate repository consequence

The current packet schema in `sapiens_client.py` should be considered incomplete but directionally correct.
It already contains:
- `state_geometry`,
- `control_profile`,
- `inference_contract`.

The next schema revision should extend this with an explicit `surface_policy` block rather than leaving the relational-formal contract only in documentation.

## Relationship to other layers

- orbital layer supplies diagnostic state,
- bridge layer reduces diagnostics into actionable state,
- packet protocol constrains how that state may be represented and expressed,
- communication/support UI should consume this protocol rather than inventing separate answer discipline rules.
