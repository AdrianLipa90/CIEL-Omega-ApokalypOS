# CIEL-Desktop Bootstrap on SOT

## Purpose

This document bootstraps the desktop-layer work into `CIEL-_SOT_Agent` without turning the desktop repository into a second engine.

The goal is architectural clarity:

- the desktop layer exists
- it has a defined role
- that role is visible from the Source-of-Truth side
- the dependency direction remains explicit

## What is being bootstrapped

The desktop repository currently contains:

- a minimal bootstrap shell
- a richer native GUI surface
- a canonical native GUI entrypoint
- launcher policy and reviewer-facing documentation
- runtime/test guidance
- an explicit adapter bridge into the local `CIEL-_SOT_Agent` checkout

## What is not being bootstrapped

This is not a migration of GUI code into `CIEL-_SOT_Agent`.
That would be architecturally worse.

The desktop code remains in `CIEL-Desktop`.
What is being added here is the SoT-facing binding layer that states what the desktop surface is allowed to be and how it depends on upstream truth.

## Why this matters

Without an SoT-side bootstrap, the desktop repository can look like an isolated product branch.
That would weaken global coherence.

The Source-of-Truth side must explicitly name:

- the desktop layer's role
- the truth direction
- the allowed coupling mode
- the intended integration path

## Intended relation

`CIEL-_SOT_Agent` -> truth, reports, bridge state, packets, validation -> `CIEL-Desktop`

not the reverse.

## Human reading

A clean human reading of the ecosystem is:

- `CIEL-_SOT_Agent` = integration kernel / bridge host / actionable truth source
- `CIEL-Desktop` = operator shell / presentation / controlled execution surface

## Audit implication

This bootstrap is an SoT-side binding statement, not a substitute for a desktop runtime certification.

Therefore an audit in this repository may certify:

- that the desktop layer is named explicitly,
- that dependency direction stays downstream,
- that SoT-visible artifact binding is part of the architecture.

It may not, without external runtime evidence, certify:

- desktop boot success,
- GUI responsiveness,
- audio, STT, or TTS behavior,
- GGUF or no-GGUF runtime behavior in the desktop surface.

## Merge implication

Any future merge or review of desktop-layer work should be judged from this relation first:

- does the desktop layer stay downstream?
- does it expose operator actions honestly?
- does it bind artifacts back into the SoT-visible system?
- does it avoid silently replacing engine logic?

If the answer stays yes, the bootstrap is healthy.
