# OPERATION DOCUMENTATION CONSISTENCY & COVERAGE — ACTIVE TODO LEDGER

## Operational law
Before starting any phase:
- [ ] read this file in full
- [ ] confirm current repo/ref and active objective
- [ ] confirm previous phase state

After finishing any phase:
- [ ] update this file as the final step
- [ ] record completed work
- [ ] record blockers / unresolved issues
- [ ] record changed files
- [ ] record next phase readiness

Reporting protocol:
- unchanged
- progress, blockers, problem ⇄ solution, and state updates remain mandatory

---

## Project objective
Update, complete, and audit repository documentation so that documentation claims match the actual implementation state.

The operation is complete only when:
- documentation inventory is explicit,
- declaration-versus-implementation mismatches are mapped,
- high-priority stale claims are corrected,
- missing human/machine repo maps are added where needed,
- and final documentation can be treated as a trustworthy operator reference.

---

## Active input package
Primary audit seed for this operation:
- `/mnt/data/FULL_REPO_REVIEW_2026-04-07.zip`

Derived local review root:
- `/mnt/data/review_docs/FULL_REPO_REVIEW_2026-04-07`

Key seed artifacts:
- `AUDIT_FULL_PL.md`
- `CHANGESET_MANIFEST.md`
- `DECLARATION_IMPLEMENTATION_MATRIX.csv`
- `DOC_REFERENCE_GAPS.csv`
- `FILE_INVENTORY.csv`
- `HUMAN_REPO_GUIDE.md`
- `MODULE_SURFACE.json`
- `AGI_REPO_MANIFEST.json`
- `AGI_REPO_MANIFEST.yaml`
- `PROPOSED_CHANGES.patch`
- `PROPOSED_REPO_FILES/...`

---

## Current project state
- [x] operation branch created from refreshed `main`
- [x] full review package identified as primary input
- [x] documentation inventory validated against current `main`
- [x] declaration-versus-implementation matrix validated against current `main`
- [x] high-priority stale docs repaired
- [x] machine-readable repo map landed in repo
- [ ] final documentation audit gate passed

### Current branch and important heads
- operation branch: `operation/documentation-consistency-and-coverage-20260407`
- branch start baseline from refreshed `main`: `13cc0ba932c2441943ca105f30edb2c9079e8df6`
- current documentation operation head after README rewrite: `14b006290976fcd02a9e38aef6a2d8c87e55ccc4`

### Problem ⇄ solution log
- **problem:** branch drifted during the operation because `main` was merged into the operation branch while a README commit had been created on an older parent.
- **solution:** the README rewrite was replayed onto the new branch head instead of force-moving or rewriting history.

---

# PHASE A — INVENTORY / INPUT VALIDATION

## Goal
Validate the review package against the current `main` and establish the documentation surface inventory.

## A1. Branch and baseline
- [x] create active operation branch
- [x] confirm refreshed `main` baseline
- [x] identify primary input package
- [x] record exact branch head used for operation start

## A2. Input package validation
- [x] unpack full review package locally
- [x] inspect review artifact structure
- [x] verify package relevance against current `main`
- [x] identify which proposed files are safe to land immediately
- [x] identify which proposed files require fresh re-audit before landing

## A3. Documentation inventory
- [x] validate docs inventory against current repo
- [x] validate workflow documentation surface
- [x] validate packaging documentation surface
- [x] validate embedded/imported sector documentation coverage

## A4. Phase exit criteria
- [x] input package validated against current repo
- [x] inventory baseline explicit

## Phase A completion notes
- [x] the review package was accepted as a real operational seed, not as a blind merge bundle
- [x] high-risk files (`README.md`, `docs/INDEX.md`, `docs/OPERATIONS.md`) were treated as re-audit targets rather than auto-imports
- [x] safe supporting artifacts were landed first

---

# PHASE B — DECLARATION VS IMPLEMENTATION AUDIT

## Goal
Turn the review package into a current declaration/implementation truth map for the repo.

## B1. Claim extraction
- [x] map top-level README claims
- [x] map docs/INDEX claims
- [x] map docs/OPERATIONS claims
- [x] map workflow docs claims
- [x] map packaging docs claims

## B2. Status classification
- [x] classify each key claim as IMPLEMENTED
- [x] classify each key claim as IMPLEMENTED_TRANSITIONAL
- [x] classify each key claim as INCOMPLETE_DOC
- [x] classify each key claim as STALE_DOC
- [x] classify each key claim as DECLARED_FUTURE

## B3. Phase exit criteria
- [x] current declaration/implementation matrix is explicit

## Phase B completion notes
- [x] `docs/DECLARATION_IMPLEMENTATION_MATRIX.md` added to the repo
- [x] stale claims were mapped before rewrite work, not after
- [x] the main stale classes identified were launcher drift, core-only path drift, underdocumented workflow coverage, packaging overclaims, and underdocumented hybrid repo geometry

---

# PHASE C — HIGH-PRIORITY DOCUMENT REPAIRS

## Goal
Land the safest, highest-value documentation fixes first.

## C1. New supporting docs
- [x] add human repo guide
- [x] add declaration/implementation matrix doc
- [x] add workflow README
- [x] add machine-readable repo maps

## C2. High-risk stale claims
- [x] correct Sapiens client surface claims
- [x] correct core-only tooling path claims
- [x] correct workflow coverage claims
- [x] correct hybrid/native/embedded repo geometry claims

## C3. Phase exit criteria
- [x] highest-priority stale claims repaired

## Phase C completion notes
- [x] added `docs/REPOSITORY_GUIDE_HUMAN.md`
- [x] added `integration/indices/REPOSITORY_MACHINE_MAP.json`
- [x] added `integration/registries/REPOSITORY_MACHINE_MAP.yaml`
- [x] expanded `.github/workflows/README.md` from a too-narrow single-workflow description to the current workflow surface set

---

# PHASE D — PRIMARY DOC REWRITES

## Goal
Apply controlled rewrites to top-level and navigation docs after audit alignment.

## D1. Candidate rewrites
- [x] `README.md`
- [x] `docs/INDEX.md`
- [x] `docs/OPERATIONS.md`

## D2. Control checks
- [x] no path regressions introduced
- [x] no stale entrypoint references introduced
- [x] no overclaim beyond implementation state introduced

## D3. Phase exit criteria
- [x] top-level documentation aligned with current repo geometry

## Phase D completion notes
- [x] `docs/INDEX.md` no longer points to non-existent `scripts/run_sapiens_client.py`
- [x] `docs/OPERATIONS.md` now reflects scripts, core-only tools, workflows, and packaging as distinct operational layers
- [x] `packaging/README.md` now distinguishes scripted installers, Debian package behavior, and Android build surface behavior
- [x] `packaging/deb/README.md` now explicitly states that model download remains a post-install step
- [x] `README.md` was rewritten as an integration/repository overview rather than a too-monolithic system description

---

# PHASE E — FINAL DOCUMENTATION AUDIT GATE

## Goal
Decide whether documentation is trustworthy enough to be treated as current system reference.

## E1. Required outputs
- [x] inventory baseline
- [x] declaration/implementation matrix
- [ ] changed-file log
- [ ] unresolved gap list

## E2. Final decision states
- [ ] READY_TO_CLOSE
- [ ] BLOCKED_BY_IMPLEMENTATION_DRIFT
- [ ] BLOCKED_BY_UNVERIFIED_RUNTIME_BEHAVIOR
- [ ] BLOCKED_BY_STALE_REVIEW_PACKAGE

## E3. Phase exit criteria
- [ ] final operation status recorded

## Current unresolved / next audit targets
- [ ] prepare explicit changed-file log for all landed documentation commits in this operation
- [ ] prepare unresolved gap list after current rewrite wave
- [ ] decide whether any remaining folder-level READMEs or AGENT-like docs still underdescribe the current repo geometry
- [ ] run final documentation truth pass against branch head `14b006290976fcd02a9e38aef6a2d8c87e55ccc4`

---

## Current active phase
- [x] Phase A — Inventory / Input Validation
- [x] Phase B — Declaration vs Implementation Audit
- [x] Phase C — High-Priority Document Repairs
- [x] Phase D — Primary Doc Rewrites
- [ ] Phase E — Final Documentation Audit Gate
