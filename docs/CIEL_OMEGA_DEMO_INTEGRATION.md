# CIEL Omega Demo Integration

## Role

This document defines the first explicit integration bridge between:

- `AdrianLipa90/CIEL-_SOT_Agent`
- `AdrianLipa90/ciel-omega-demo`

The purpose is not to absorb the demo repository into SOT.
The purpose is to make the upstream shell objects of the demo repository legible and traceable inside the SOT integration layer.

---

## Structural rule

For current integration purposes, `ciel-omega-demo` is treated as:

- **cockpit shell**,
- **UI / publication / educational surface**,
- **runtime presentation layer**.

It is **not** treated here as the engine.

The engine direction is reserved for the future `Informational Dynamics` layer under the larger shell-versus-engine architecture.

That distinction must remain explicit.

---

## Imported shell objects currently tracked

The first imported shell bindings cover these upstream files from `ciel-omega-demo`:

1. `AGENT.md`
2. `docs/INDEX.md`
3. `docs/orbital_manifest.json`
4. `main/apps/omega_app.py`
5. `main/apps/omega_orbital_app.py`
6. `main/apps/object_cards.py`
7. `main/apps/orbital_manifest_export.py`

These were chosen because together they define:

- shell governance,
- shell entry navigation,
- shell manifest state,
- legacy runtime surface,
- orbital runtime surface,
- shell epistemic object layer,
- shell manifest generation.

---

## Integration meaning

Inside `CIEL-_SOT_Agent`, these imported objects should be read as:

- upstream shell-facing surfaces,
- not canonical theory,
- not engine internals,
- not native SOT derivations.

Their job is to tell the integration layer:

- what the shell exposes,
- how the shell currently organizes runtime and epistemic surfaces,
- which shell objects should later bind to deeper engine-facing objects.

---

## Machine-readable companion

The machine-readable companion file is:

- `integration/upstreams/ciel_omega_demo_shell_map.json`

That file is the authoritative first-pass mapping of imported demo shell objects inside this repository.

---

## Immediate next step after this file

The correct next integration step is not random expansion.
It is:

1. keep the shell map current,
2. preserve shell-versus-engine distinction,
3. later identify which `Informational Dynamics` folder becomes the engine target,
4. then bind shell objects to engine objects explicitly.

---

## Summary

This document marks the beginning of integration,
not the completion of it.

What is now established is simple and important:

> `ciel-omega-demo` is already a tracked upstream shell.
>
> `CIEL-_SOT_Agent` now begins to index and bind that shell explicitly,
> while keeping engine semantics separate.
