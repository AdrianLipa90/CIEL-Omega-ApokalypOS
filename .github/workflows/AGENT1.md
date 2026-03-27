# AGENT1.md

## Folder role

`.github/workflows/` stores executable GitHub Actions workflows for the SOT integration layer.

These files define scheduled or manual automation behavior.

---

## Agent 1 scope in this folder

Agent 1 may use this folder for:

- scheduled synchronization workflows,
- manual dispatch workflows,
- automation that updates integration state artifacts,
- future validation workflows tied to registry coherence.

---

## Current workflow objects

- `gh_repo_coupling.yml` — scheduled and manual workflow that runs the live GitHub coupling routine and commits refreshed integration state artifacts.

---

## Rules

- Workflow behavior should be traceable to `scripts/` and `src/`.
- If a workflow writes repository state, the written files should already be declared in docs or registries.
- Workflow names should reflect one clear operational task.
