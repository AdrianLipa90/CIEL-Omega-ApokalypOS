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

## Current implementation track
The current implementation track after documentation cleanup is:
1. harden semantic boundaries between analogy / science / runtime,
2. make `phased_state.py` contracts explicit,
3. separate identity phase from selection relevance,
4. specify Orbital Dynamics Law v0 formally,
5. implement the runtime law path,
6. repair runtime bottlenecks after semantics are stable.

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
