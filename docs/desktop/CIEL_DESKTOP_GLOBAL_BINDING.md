# CIEL-Desktop Global Binding

## Binding statement

`CIEL-Desktop` is a downstream operator-facing desktop layer bound to `CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold` as upstream Source of Truth.

## Dependency order

The intended dependency order is:

`CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold` -> repository truth / bridge reduction / packet state / validation outputs -> `CIEL-Desktop`

The reverse dependency must not become structurally dominant.

## Allowed desktop role

The desktop layer may:

- render state
- organize state
- navigate reports and indices
- expose explicit operator actions
- display provenance and epistemic status
- trigger bounded write-back operations that land in SoT-visible artifact space

The desktop layer must not:

- redefine orbital truth
- invent repo-phase truth
- become a hidden second engine
- silently replace Sapiens packet logic
- hide uncertainty behind UI polish

## Artifact binding

Explicit operator actions from the desktop side should bind into artifacts visible to the SoT system, for example under engine report locations.

This preserves auditability and keeps downstream action visible upstream.

## Why the binding is needed

A desktop shell without explicit global binding tends to drift toward product autonomy.
That may be ergonomically attractive but epistemically dangerous.

The system should remain clear that presentation follows truth, not the other way around.

## Long-term target

The desktop layer should become thinner over time by consuming a smaller and more explicit contract from the engine side.
That means more explicit SoT exports and less broad import reach from the desktop repo.
