# AGENT1.md

## Folder role

`.github/` stores GitHub-native automation and repository control surfaces.

This folder is operational infrastructure.
It is not a theory layer and not the place for hidden semantic claims.

---

## Agent 1 scope in this folder

Agent 1 may use `.github/` for:

- repository automation,
- workflow orchestration,
- commit/update routines tied to integration state,
- future issue or PR automation if explicitly introduced.

---

## Rules

- GitHub automation must reflect documented repository behavior.
- Any workflow that mutates tracked files should point to explicit code in `src/` or `scripts/`.
- Automation should remain auditable and avoid creating undocumented state transitions.
