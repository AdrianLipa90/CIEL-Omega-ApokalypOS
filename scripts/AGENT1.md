# AGENT1.md

## Folder role

`scripts/` stores thin executable launchers for the SOT integration layer.

These scripts should stay small and explicit.
They are not the place for large logic blocks or hidden architecture decisions.

---

## Agent 1 scope in this folder

Agent 1 may use `scripts/` for:

- manual runners,
- convenience entrypoints,
- automation-facing launchers,
- thin wrappers around `src/ciel_sot_agent/` modules.

---

## Current objects

- `run_gh_repo_coupling.py` — thin launcher for the live GitHub coupling workflow.

---

## Rules

- Keep scripts as wrappers, not as the primary implementation layer.
- If a script becomes structurally meaningful, document the real logic in `src/` and `docs/`.
- Script names should map clearly to one operational task.
- Any script used by CI or GitHub Actions should stay stable and legible.
