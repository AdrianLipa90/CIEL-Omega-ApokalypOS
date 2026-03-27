# Post-Merge Reconciliation

## Purpose

This note reconciles the repository state after the merge of the repo-geometry phase1 branch into `main`.

Its role is to distinguish:
- what is now actually present in the repository,
- from what older readiness/checklist files still describe as pending.

## What is now present after merge

The merged repository now includes:
- canonical root surface preparation (`README_CANONICAL_V2.md`),
- canonical docs index preparation (`docs/INDEX_CANONICAL_V2.md`),
- canonical runtime entrypoint surface (`docs/operations/V2_RUNTIME_ENTRYPOINTS_CANONICAL.md`),
- machine authority declaration (`integration/MACHINE_AUTHORITY_V2.md`),
- legacy machine mirror policy (`docs/architecture/LEGACY_MACHINE_MIRROR_POLICY.md`),
- machine authority human-readable surface (`docs/integration/MACHINE_AUTHORITY_SURFACE.md`),
- final in-place switch package (`docs/architecture/FINAL_IN_PLACE_SWITCH_PACKAGE.md` and companion replacement/checklist files).

## What this means

The following milestones are now satisfied at the preparation level:
- canonical surface preparation exists,
- canonical runtime surface preparation exists,
- machine authority direction is declared,
- legacy machine files are documentation-level demoted,
- final in-place switch materials exist.

## What is still not done

The following actions still remain unfinished:
- `README.md` has not yet been overwritten in place,
- `docs/INDEX.md` has not yet been overwritten in place,
- `integration/hyperspace_index.json` has not yet been overwritten in place,
- `integration/index_registry.yaml` has not yet been overwritten in place,
- some older readiness/checklist files still describe pre-merge state and should be interpreted historically unless refreshed.

## Interpretation rule

After this merge, older readiness or checklist files that still mark canonical preparation as absent should be read as stale state snapshots rather than current truth.

The current truth is:
- preparation is present,
- authority direction is declared,
- destructive in-place switch is still pending.

## Recommended next move

The next move should be one of:
1. refresh the checklist/readiness files in place when tooling permits,
2. or execute the final in-place switch using the prepared replacement package and then validate via v2 runtime entrypoints.
