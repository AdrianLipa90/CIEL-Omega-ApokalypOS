# Post-Merge Conflict Audit

## Purpose

This audit distinguishes between:
- real post-merge conflicts,
- transitional but intentional dual-surface states,
- and stale status files that should not be treated as current truth.

## Real conflicts found

### 1. Root README remains legacy-first in place
Current status:
- `README.md` still reflects the older integration surface rather than the prepared canonical-v2 root surface.

Conflict type:
- surface-level in-place switch still pending

Severity:
- medium

Reason:
- canonical preparation exists, but the root in-place replacement has not yet been executed.

### 2. docs index remains legacy-first in place
Current status:
- `docs/INDEX.md` still points primarily to older flat paths and pre-v2 navigation assumptions.

Conflict type:
- surface-level in-place switch still pending

Severity:
- medium

### 3. legacy operational note is incomplete relative to canonical runtime surface
Current status:
- `docs/operations/V2_RUNTIME_ENTRYPOINTS.md` does not fully reflect the synchronization runtime,
- while `docs/operations/V2_RUNTIME_ENTRYPOINTS_CANONICAL.md` does.

Conflict type:
- legacy note stale relative to canonical note

Severity:
- low

### 4. original canonical checklist is stale relative to current truth
Current status:
- `integration/CANONICAL_SWITCH_CHECKLIST.yaml` still describes pre-merge preparation state,
- while `integration/CANONICAL_SWITCH_CHECKLIST_CURRENT.yaml` records current truth.

Conflict type:
- stale status snapshot still present

Severity:
- low

## Transitional states that are intentional and not bugs

### A. Canonical files exist without in-place overwrite
This is intentional while the final in-place switch is still pending.
Examples:
- `README_CANONICAL_V2.md`
- `docs/INDEX_CANONICAL_V2.md`

### B. Legacy machine files still exist as mirrors
This is intentional and documented.
Examples:
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`

### C. Legacy runtime entrypoints still exist
This is intentional and documented as compatibility behavior.

## Current truth rule

If two files disagree, the preferred truth order is:

1. post-merge reconciliation and progress notes,
2. canonical-v2 surfaces,
3. refreshed current checklist,
4. older readiness/checklist files,
5. legacy in-place surfaces.

## Recommended next move

The next corrective action should be the actual in-place switch of the remaining legacy-first surface files, followed by runtime validation.
