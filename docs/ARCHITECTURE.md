# Architecture

## Role

`CIEL-_SOT_Agent` is the integration attractor for a multi-repository ecosystem.
It is not the canonical source of every theory file. It is the place where repository identities,
links, cross-references, and executable integration logic are made explicit.

## Repository topology

### Canon / Seed of the Worlds
Primary source for:
- axioms,
- definitions,
- derivations,
- falsification / verification sectors,
- orbital manifests,
- nonlocal repository hyperspace.

### CIEL Omega demo
Primary source for:
- cockpit UI,
- orbital navigation preview,
- educational analogies,
- presentation surface.

### Metatime
Primary source for:
- historical theory materials,
- simulations,
- phenomenological notes,
- older solver and documentation branches.

### CIEL-_SOT_Agent
Primary source for:
- repository registry,
- machine-readable hyperspace index,
- cross-repository synchronization,
- compatibility and convergence tests,
- seed-oriented runners.

## GitHub as operational attractor

For this integration layer, GitHub is treated as the operational center of truth.
That means:
- history is explicit,
- structure is inspectable,
- semantic drift is easier to detect,
- cross-repository coordination is less private and less ambiguous.

This is an operational claim, not an ontological proof.

## Pipeline — end-to-end reduction chain

The system operates as a 3-layer pipeline from repositories to CIEL/Ω consciousness layer:

### Layer 1 — `ciel_sot_agent.synchronize`
Repository phase synchronizer. Treats repos as coupled discrete identities with fields:
- `phi` — semantic phase, `spin` — orientational sign, `mass` — informational weight.

Computes: weighted Euler vector, closure defect, pairwise phase tensions.

### Layers 2+3+4 — `ciel_sot_agent.orbital_bridge`
Orbital pass (20 steps). Computes coherence index, system health, nonlocal EBA gate,
entity sector metrics (20 entities), recommended operating mode.

Modes (by `closure_penalty`): `deep` < 5.2 < `standard` < 5.8 < `safe`.

### Layer Ω — `ciel_sot_agent.ciel_pipeline`
CIEL/Ω engine: intention → waves → emotion → ethics → memory → Lie₄ → Collatz.
Returns: `dominant_emotion`, `ethical_score`, `soul_invariant`, `subconscious_note`.

### Canonical entrypoint
`CIEL_CANON.py` at project root — single file containing all paths, thresholds, pipeline sequence,
entity notes, and subconsciousness config. Run `python3 CIEL_CANON.py` for live status.

### Subconsciousness layer
TinyLlama 1.1B (`~/.local/share/ciel/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf`) runs
on port 18520 as an associative background stream. Queried by `ciel_pipeline` at each cycle;
result in `subconscious_note` field. Managed via `src/ciel_sot_agent/subconsciousness.py`.

## Shell import binding

The first explicit shell-level import binding now targets:

- `AdrianLipa90/ciel-omega-demo`

Within this architecture, that upstream repository is treated as:

- shell,
- cockpit,
- UI surface,
- educational and publication layer,
- runtime presentation layer.

It is not treated here as the engine.

That distinction matters because the future engine-facing direction is reserved for the later `Informational Dynamics` binding.

The current imported shell objects are documented in:

- `docs/CIEL_OMEGA_DEMO_INTEGRATION.md`
- `integration/upstreams/ciel_omega_demo_shell_map.json`

This means the integration layer now distinguishes between:

- **native SOT integration objects**, and
- **imported demo shell objects**.

That separation is required to avoid false canonical ownership and to keep shell-versus-engine architecture legible.

## Cross-reference rule

Every conceptual file in `docs/` should appear in `integration/hyperspace_index.json`.
Machine-readable and human-readable indices must evolve together.
