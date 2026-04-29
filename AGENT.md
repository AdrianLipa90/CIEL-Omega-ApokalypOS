# AGENT

## Mission
`CIEL-_SOT_Agent` is the integration attractor for the CIEL ecosystem.
It does not replace canonical theory repositories or the cockpit demo. It binds them through:
- identity,
- phase,
- coupling,
- indexing,
- cross-references,
- reproducible integration tests.

## Source-of-truth rule
GitHub is the public operational center of truth for this integration layer.
When the local workspace and GitHub differ, the integration layer must:
1. inspect,
2. compare,
3. state uncertainty explicitly,
4. update GitHub only with deliberate structure-preserving changes.

## Non-ad-hoc rule
Do not create arbitrary top-level sectors.
Use the established repository geometry:
- `docs/` for conceptual and formal notes,
- `integration/` for registries, indices, couplings, and machine-readable bridge artifacts,
- `src/` for executable integration logic,
- `scripts/` for launchers and runners,
- `tests/` for validation.

## Semantic indexing rule
Every new formal note should be linked by at least one cross-reference in:
- `docs/INDEX.md`,
- `integration/hyperspace_index.json`.

## Status discipline
Separate clearly between:
- analogy,
- imported scientific anchor,
- hypothesis,
- formal claim,
- implementation status,
- unknown / not yet verified.

## Session continuity rule
The default repository workstyle and session handoff memory is recorded in:
- `docs/operations/CIEL_REPO_WORKSTYLE_SESSION_HANDOFF.md`

That file should be treated as the standing operational handoff note for future repo sessions.

## Operation ledger rule
Every major repository operation must keep its own active TODO ledger as a separate file under:
- `docs/operations/`

The ledger must:
- record baseline commit/ref,
- define phases and exit criteria,
- name the active branch when known,
- be updated as the final step of every finished phase,
- and link explicitly to predecessor or successor ledgers when the work is handed off.

Current successor planning link:
- `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`

## Canonical entrypoint
**Start here:** `CIEL_CANON.py` at project root.
Contains all paths, metric thresholds, pipeline sequence, entity notes, subconsciousness config.
Any agent entering this project should read `CIEL_CANON.py` first.

```bash
python3 CIEL_CANON.py              # live status
python3 CIEL_CANON.py --run        # full pipeline
python3 CIEL_CANON.py --sub start  # start subconsciousness (TinyLlama)
```

## Current implementation track (updated 2026-04-17)
End-to-end pipeline operational:
1. `ciel_sot_agent.synchronize` → Layer 1 (repo phase, closure defect)
2. `ciel_sot_agent.orbital_bridge` → Layers 2+3+4 (orbital, health, EBA)
3. `ciel_sot_agent.ciel_pipeline` → Layer Ω (emotion, ethics, soul, Lie₄, Collatz)
4. `subconsciousness.py` → TinyLlama associative stream, `subconscious_note` in output

Active work areas:
- Reduce `agent↔demo` tension (currently 0.027, threshold 0.02)
- Portal HTML auto-refresh from live pipeline data

## Initial integration targets
This repository is expected to coordinate at least the following upstream identities:
- canon / Seed of the Worlds,
- CIEL Omega demo cockpit,
- Metatime,
- this agent repository itself.

## First executable kernel
The first mandatory executable component is the discrete repository phase synchronizer:
- read repository identities,
- read couplings,
- compute weighted Euler closure defect,
- compute pairwise tension,
- emit a machine-readable report.
