# AGENT1.md

## Folder role

`src/ciel_sot_agent/` is the main Python package for Agent 1 implementation work.

## Agent 1 scope

Agent 1 uses this package for:
- repository phase modeling,
- upstream coupling logic,
- synchronization runners,
- later shell-to-engine interface code.

## Rules

- Every major module here should remain connected to docs, registry objects, and tests.
- This package may model repository relations, but must not pretend to be the engine itself.
- If imported shell objects are consumed here, the shell status should remain explicit.
