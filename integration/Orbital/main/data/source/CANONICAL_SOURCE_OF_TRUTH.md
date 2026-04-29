# Canonical source of truth

The duplicated `CIEL_OMEGA_COMPLETE_SYSTEM` mirror that previously lived here was removed.

Canonical code root:
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega`

Mirror-only files needed by the runtime or tooling were consolidated into the canonical tree.
Legacy tooling should resolve against the canonical `src/` path, not against a local mirror copy.
