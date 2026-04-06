# Sapiens Surface Binding

## Purpose

This document binds three layers that now exist explicitly in the repository:

1. orbital diagnostics,
2. native bridge reduction,
3. relational-formal human-model surface protocol.

It exists so that Sapiens-facing logic is not treated as a generic chat wrapper detached from the repository's own architecture.

## Existing code path

The current code already defines a concrete dependency chain:

- `src/ciel_sot_agent/orbital_bridge.py`
- `src/ciel_sot_agent/sapiens_client.py`

The bridge computes:
- state manifest,
- health manifest,
- recommended control,
- bridge metrics.

The Sapiens client then maps that bridge output into a `state_geometry` with:
- `surface`,
- `internal_cymatics`,
- `spin`,
- `axis`,
- `attractor`.

## Correct dependency direction

The correct architecture is:

`orbital source architecture -> imported orbital runtime -> native bridge reduction -> Sapiens surface protocol -> model packet / transcript / session state`

This direction must remain explicit.

## Layer meanings

### 1. Orbital layer

The orbital layer provides repository-scale coherence observables.
It is not itself the conversational surface.

Primary outputs relevant to Sapiens:
- `R_H`
- `closure_penalty`
- `Lambda_glob`
- health-like stability observables
- recommended control mode downstream through the bridge

### 2. Bridge layer

The bridge is the reduction layer.
Its job is to turn orbital observables into:
- state manifest,
- health manifest,
- recommended control profile,
- integration-facing bridge metrics.

The bridge is where orbital diagnostics become actionable interaction state.

### 3. Sapiens surface layer

The Sapiens layer is the first human-model representation layer.
It should not invent geometry from scratch.
It should express bridge-reduced state through the relational-formal protocol.

## Current geometric mapping in code

The existing `sapiens_client.py` already maps bridge output into:

- `surface`
  - interaction mode
  - recommended action
- `internal_cymatics`
  - coherence index
  - closure penalty
  - system health
- `spin`
  - topological charge proxy from bridge metrics
- `axis`
  - truth
- `attractor`
  - orbital-holonomic-stability

This should now be treated as intentional architecture, not incidental implementation.

## Binding to the relational-formal protocol

The relational-formal contract adds these constraints:

- truth over smoothing,
- explicit uncertainty over false certainty,
- explicit distinction between fact / inference / hypothesis / unknown,
- minimal semantic distortion,
- preservation of the user-intent axis.

Therefore the Sapiens surface should be interpreted as follows:

### surface
The visible response form.
Includes wording, structure, degree of directness, and interaction mode.

### internal_cymatics
The hidden interaction-tension structure.
Operationally represented by coherence, closure penalty, and health-like indicators.

### spin
The orientation of the answer.
Bridge state may influence urgency or caution, but the contract fixes the preferred spin as truth-seeking rather than comfort-seeking.

### axis
The ordering direction of the interaction.
This should remain aligned with the user question, the user intent, and truth-constrained movement toward coherence.

### attractor
The target interaction state.
Operationally this is not mere pleasantness.
It is minimal distortion under truthful, coherent response conditions.

## Immediate implementation consequence

Future Sapiens packet or panel work should not only carry orbital metrics.
It should also carry explicit interaction discipline fields such as:
- epistemic mode,
- distortion budget,
- confidence discipline,
- formatting discipline for fact/inference/hypothesis/unknown.

## Non-goals

This binding does not claim that the current Sapiens client is already complete.
It only states the correct architectural interpretation of the existing code path.

## Next implementation targets

1. Extend the Sapiens packet schema with relational-formal protocol fields.
2. Add a surface-policy manifest emitted alongside the model packet.
3. Make future communication/support panel surfaces consume the same contract.
