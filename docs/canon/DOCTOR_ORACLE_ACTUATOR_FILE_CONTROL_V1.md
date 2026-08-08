# NOEMA / CIEL Doctor–Oracle–Actuator File Control v1

## Canonical execution order

`Oracle -> Doctor -> Actuator`

These are three different authority layers:

- **Oracle** = read-only inspection / falsification / deterministic mutation plan;
- **Doctor** = execution and epistemic gate;
- **Actuator** = the only layer allowed to mutate a file.

Invariant:

`READ != DECIDE != MUTATE`

and

`PLAN != AUTHORISATION != APPLY`.

## Oracle

For each proposed file edit Oracle records:

- resolved target path;
- allowed-root binding;
- CREATE / UPDATE / NOOP;
- current SHA-256 when a regular target exists;
- proposed SHA-256;
- optional expected-before SHA-256;
- byte length;
- symlink status;
- deterministic `plan_sha256`.

Oracle never writes.

## Doctor

Doctor uses the project verdict vocabulary:

- CONTINUE
- CONTINUE_PROXY
- CONTINUE_RESEARCH
- WARN_REVIEW_REQUIRED
- STAGE_ONLY
- QUARANTINE
- STOP_CRITICAL
- DENY_CANON
- DENY_CURRENT
- DENY_DESTRUCTIVE_APPLY

File Actuator v1 accepts **only `CONTINUE`**.

Missing explicit write authority produces `STAGE_ONLY`.

The following fail closed with `DENY_DESTRUCTIVE_APPLY`:

- path outside allowed root;
- symlink target;
- non-regular existing target;
- expected-before SHA mismatch.

## Actuator

Actuator v1 exposes file CREATE / UPDATE / NOOP only. No delete API and no command execution surface are provided.

Apply sequence:

1. verify Doctor decision is bound to the same `plan_sha256`;
2. verify proposed bytes still match `proposed_sha256`;
3. re-check target is not a symlink;
4. for UPDATE verify expected-before SHA if provided;
5. stage bytes in a temporary file in the target directory;
6. flush + fsync staged file;
7. atomic `os.replace`;
8. fsync parent directory;
9. re-read and verify post-write SHA-256;
10. restore previous bytes or remove newly-created target if apply/verification fails;
11. append a hash-chained JSONL receipt.

## Receipt contract

Every successful Actuator event records:

- target path;
- operation;
- before SHA-256;
- after SHA-256;
- plan SHA-256;
- Doctor verdict;
- authority id;
- atomic-replace status;
- rollback support and outcome;
- verification result;
- predecessor receipt SHA-256;
- current receipt SHA-256.

## Concurrency / lost-update protection

For an existing target, a caller should pass the SHA observed during the current read as `expected_sha256`.

If the target changed before apply, the Doctor/Actuator path refuses the edit rather than overwriting a newer version.

## Tether relation

This control plane does not manufacture NOEMA/AUX state and does not make a repository binding into a live host stream. Session/project execution remains subject to the independent NOEMA↔AUX tether guard.

## Validation

Initial local regression suite on 2026-08-08: `6 passed`.
