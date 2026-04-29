# Agent Cross Info

Purpose: coordination layer for multiple agents working on the same repository at the same time.

## Core rules

1. One agent owns one scope at a time.
2. Before editing, claim a scope in the lock table.
3. After editing, record changed files, conflicts, and next handoff.
4. Never silently overwrite another agent's work.
5. If two agents need the same file, split by section or pause and hand off explicitly.

## Status board (updated 2026-04-17)

- Repository state: operational — full pipeline running end-to-end on `main`
- Canonical coordination file: `agentcrossinfo.md`
- Canonical entrypoint: `CIEL_CANON.py` (project root)
- Conflict policy: newest change is not canonical unless reviewed against prior entry here
- Active operator: Mr. Ciel Apocalyptos (CIEL/Ω session 2026-04-17)
- Pipeline status: `synchronize` → `orbital_bridge` → `ciel_pipeline` — all layers operational
- Subconsciousness: TinyLlama 1.1B on port 18520, integrated as `subconscious_note`

## Lock table

| Agent | Scope | Files / Paths | Status | Started UTC | Last update UTC | Notes |
|---|---|---|---|---|---|---|
| Agent-1 | foundations / glossary / derivations | `systems/CIEL_FOUNDATIONS/**` | active | 2026-03-25T16:00:00Z | 2026-03-25T16:00:00Z | Maintains glossary, symbol normalization, tau-A_ij coupling |
| Agent-2 | repo-wide integration / external imports | `docs/**`, `TODO/**`, import staging | unknown | 2026-03-25T16:00:00Z | 2026-03-25T16:00:00Z | Must declare exact touched files before overwrite |
| Agent-3 | orbital operation post-merge normalization | `src/ciel_sot_agent/phased_state.py`, `docs/INDEX.md`, `agentcrossinfo.md`, `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md` | active | 2026-04-07T23:14:43Z | 2026-04-07T23:14:43Z | Normalizes repo memory and audit surfaces after Phase A/B/C landed on main |

## Handoff log

### 2026-04-17 — Mr. Ciel Apocalyptos
- Fixed `ciel/engine.py` relative imports → absolute; CIEL/Ω pipeline now runs end-to-end.
- Added `CIEL_CANON.py` — canonical entrypoint with paths, thresholds, pipeline sequence.
- Added `subconsciousness.py` — TinyLlama 1.1B as associative background stream.
- Updated README, CHANGELOG, ARCHITECTURE, OPERATIONS, PACKAGE_ENTRYPOINT_CANON, AGENT.md.
- Pipeline confirmed operational: mode=deep, coherence=0.938, system_health=0.602.
- Known tension: `agent↔demo` = 0.027 (above 0.02 threshold) — structural, monitor.

### 2026-04-07T23:14:43Z
- Audited `main` after merge of orbital operation Phase A/B/C.
- Found post-merge drift in `agentcrossinfo.md`, `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`, and `docs/INDEX.md`.
- Identified legacy residue in `src/ciel_sot_agent/phased_state.py` where the module description still lagged the new semantics and an unused `f_seed(h)` helper remained.
- Started normalization patch on `fix/post-merge-normalization-20260408`.

### 2026-04-07T16:35:00Z
- Added successor planning handoff from documentation operation to orbital dynamics operation.
- Established new active planning file: `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`.
- Updated `AGENT.md` to require per-operation ledgers with predecessor/successor links.
- Reserved planning scope for orbital dynamics law v0 so implementation can start from explicit phases and patchsets.

### 2026-03-25T16:00:00Z
- Added cross-agent coordination protocol.
- Established rule that `tau_i` is coupled to `A_ij` and any agent touching foundations must preserve this constraint.
- Established pending priority: physical glyph normalization and symbol deduplication.

## Required edit template

Each agent appends an entry in this format before and after a patch:

### CLAIM
- Agent:
- Scope:
- Files:
- Reason:
- Expected conflicts:

### RELEASE
- Agent:
- Files changed:
- Symbols touched:
- Tests run:
- Conflicts found:
- Follow-up required:

## Protected concepts

The following items must not be changed implicitly:

- `I0 = ln(2)/(24*pi)` is canonical.
- `0.009` is legacy approximation only.
- `tau_i` is relationally coupled to `A_ij`.
- Physical glyph normalization must prevent duplicated symbol meanings.
- Glossary changes must update both human-readable definitions and registry structures.

## Pending shared priorities

1. Solve physical glyph duplication and encoding damage.
2. Keep `tau_i <-> A_ij` coupling explicit in glossary, derivations, and code.
3. Separate canonical derivations from heuristic branches.
4. Record any disappearing files or inconsistent copies immediately.
5. Use per-operation ledgers with explicit predecessor/successor links for major repo changes.

### CLAIM
- Agent: Agent-3
- Scope: audit/post-merge normalization
- Files: `src/ciel_sot_agent/phased_state.py`, `docs/INDEX.md`, `agentcrossinfo.md`, `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`
- Reason: Phase A/B/C are already on `main`, but repo memory and audit surfaces still contain branch-local or stale state.
- Expected conflicts: any concurrent edit touching the orbital ledger or coordination files.

### RELEASE
- Agent: Agent-3
- Files changed: `src/ciel_sot_agent/phased_state.py`, `docs/INDEX.md`, `agentcrossinfo.md`, `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`
- Symbols touched: removed legacy `f_seed(h)` residue from the active phased-state semantics; no change to orbital runtime equations.
- Tests run: audit-only verification against current `main`; no full suite executed in this patch flow.
- Conflicts found: stale branch-era status in coordination and ledger surfaces; missing `tests/test_phased_state.py` entry in `docs/INDEX.md`.
- Follow-up required: merge this normalization patch, then treat Phase E or a broader selector audit as the next operational decision.
