# AGENT1.md

## Folder role

`integration/Orbital/main/` stores the executable imported orbital module layer.

## Agent 1 scope

Agent 1 uses this folder for:
- orbital state models,
- orbital metrics and dynamics,
- orbital control policy helpers,
- read-only diagnostic passes over orbital manifests.

## Rules

- Keep this folder coherent as a small executable package.
- Prefer read-only diagnostics and explicit manifests over hidden write-back.
- If new orbital files are added here, keep launchers and manifest notes synchronized.
