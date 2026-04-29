# Agent Cross Info

Purpose: coordination layer for multiple agents working on the same repository at the same time.

## Core rules

1. One agent owns one scope at a time.
2. Before editing, claim a scope in the lock table.
3. After editing, record changed files, conflicts, and next handoff.
4. Never silently overwrite another agent's work.
5. If two agents need the same file, split by section or pause and hand off explicitly.

## Status board

- Repository state: active multi-agent mode
- Canonical coordination file: `governance/coordination/agentcrossinfo.md`
- Legacy compatibility path: `agentcrossinfo.md`
- Conflict policy: newest change is not canonical unless reviewed against prior entry here

## Lock table

| Agent | Scope | Files / Paths | Status | Started UTC | Last update UTC | Notes |
|---|---|---|---|---|---|---|
| Agent-1 | foundations / glossary / derivations | `systems/CIEL_FOUNDATIONS/**` | active | 2026-03-25T16:00:00Z | 2026-03-25T16:00:00Z | Maintains glossary, symbol normalization, tau-A_ij coupling |
| Agent-2 | repo-wide integration / external imports | `docs/**`, `TODO/**`, import staging | unknown | 2026-03-25T16:00:00Z | 2026-03-25T16:00:00Z | Must declare exact touched files before overwrite |

## Handoff log

### 2026-03-25T16:00:00Z
- Added cross-agent coordination protocol.
- Established rule that `tau_i` is coupled to `A_ij` and any agent touching foundations must preserve this constraint.
- Established pending priority: physical glyph normalization and symbol deduplication.

## Phase-1 migration note

This file has been copied into the `governance/coordination/` sector as the start of repository-geometry refactor phase 1.
During migration, both locations may coexist temporarily.

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
