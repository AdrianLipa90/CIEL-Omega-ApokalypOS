# CIEL-Desktop Fixed Attribute

## Status

`CIEL-Desktop` is declared as a **fixed attribute** of `CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold`.

## Meaning

This does not mean that the desktop repository replaces the integration manifold.
It means the desktop surface is treated as a stable, explicit subsystem bound to the agent layer.

It also does **not** mean that desktop runtime behavior is proven by this repository alone.
This repository can declare and bind the desktop surface, but desktop boot, GUI behavior, audio paths, and local-model runtime claims must be audited where those runtime paths actually execute.

## Canonical declaration

The machine-readable declaration lives at:

- `integration/fixed_attributes/ciel_desktop_fixed_attribute.json`

## Binding rule

- source repository: `AdrianLipa90/CIEL-Desktop`
- target repository: `AdrianLipa90/CIEL-_SOT_Agent`
- binding mode: `fixed-attribute`
- subsystem role: `desktop-surface`

## Follow-up

A later registry refactor should fold this declaration into:
- `integration/repository_registry.json`
- `integration/couplings.json`
- `integration/gh_upstreams.json`

Until then, this file and its paired JSON declaration are the canonical statement that Desktop is a fixed attribute in SOT_Agent.

## Audit boundary

Inside `CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold`, the desktop layer is auditable as:
- fixed-attribute declaration,
- downstream dependency direction,
- SoT-visible artifact contract.

Inside `CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold`, the desktop layer is **not** automatically auditable as:
- proven desktop boot,
- proven GUI responsiveness,
- proven audio I/O,
- proven STT or TTS runtime,
- proven GGUF-backed runtime.

Those claims require runtime evidence from `CIEL-Desktop` or from a test environment that actually runs those paths.
