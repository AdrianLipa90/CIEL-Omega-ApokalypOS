# Orbital Architecture Binding

## Purpose

This file binds the imported orbital integration layer to the full source orbital architecture.

It exists so that future edits inside `integration/Orbital/` preserve the correct interpretation of this sector.

## Layer distinction

### Full source architecture

The full source orbital architecture lives in:
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/`

### Imported runtime snapshot

The imported integration-facing orbital runtime lives in:
- `integration/Orbital/`
- `integration/Orbital/main/`

## Binding rule

The imported layer must be interpreted as a projection of the source architecture, not as an independent redesign.

That means:
- preserve imported status,
- preserve explicit manifests,
- preserve executable coherence of `integration/Orbital/main/`,
- preserve launcher synchronization,
- preserve distinction from native SOT integration code.

## Protected local rules

1. Imported orbital files remain marked as imported or integration-facing.
2. `integration/Orbital/main/` remains a small coherent executable package.
3. Prefer explicit diagnostic artifacts over hidden mutation.
4. Orbital runners must not silently rewrite non-orbital registry layers.
5. If the imported layer changes structurally, update the import manifest or addendum.
6. If launchers change, update local documentation and manifest notes together.

## Interpretation of diagnostic output

The orbital layer may emit explicit reports and generated runtime manifests for an orbital pass.
That is compatible with the source architecture.

What must be avoided is broad or silent write-back into unrelated integration sectors.

## Refactor consequence

`integration/Orbital/` is a protected import sector during repository refactor.

It may be documented more clearly and indexed more coherently,
but it should not be flattened into generic package refactor work or silently absorbed into `src/ciel_sot_agent/`.
