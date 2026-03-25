# AGENT1.md

## Folder role

`tests/` stores executable checks for Agent 1 integration logic.

## Agent 1 scope

Agent 1 uses this folder for:
- numerical sanity tests,
- registry consistency checks,
- upstream mapping checks,
- later shell-versus-engine boundary checks.

## Rules

- If a tested object is still placeholder or provisional, the test layer should not hide that fact.
- Tests should verify integration claims, not merely file existence when deeper structure is claimed.
- New integration modules should gain corresponding tests whenever practical.
