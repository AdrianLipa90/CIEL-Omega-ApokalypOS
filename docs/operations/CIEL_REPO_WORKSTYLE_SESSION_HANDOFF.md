# CIEL Repo Workstyle — Session Handoff

## Purpose
This file preserves the working logic used for repository operations so the next session can continue without losing method, rigor, or sequencing.

---

## Core working principles

### 1. Truth over smoothing
- Never guess.
- If something is unknown, say it explicitly.
- If something can be verified from the repo, verify it first.
- Separate clearly:
  - **fact**
  - **logical inference**
  - **hypothesis**
  - **unknown**

### 2. Repo-first, not memory-first
- Before changing anything, inspect the **current repo state**.
- Use the actual current `main` or active branch as source of truth.
- Do not rely on earlier assumptions if the branch may have moved.
- Refresh head before major decisions.

### 3. No hidden blockers
- Every blocker, error, mismatch, or failed write-path must be reported immediately.
- Do not conceal tool failures.
- Distinguish:
  - semantic problem
  - repo conflict
  - toolchain failure
  - branch drift
  - stale documentation
  - unresolved implementation gap

### 4. Small coherent patchsets
- Prefer small, semantically coherent patchsets over giant mixed commits.
- Each patchset should have one main purpose.
- Order matters more than speed.

### 5. Documentation and implementation must stay coupled
- If execution surfaces change, docs must follow.
- If docs are rewritten, they must be checked against the actual code and package surfaces.
- Machine-readable maps and human-readable docs should stay aligned.

### 6. Relation-aware workflow
- The user is not only a reviewer but also a valid execution tool when direct repo write access or tooling becomes the blocker.
- If the model cannot reliably perform the last write step, reduce the problem to the smallest exact manual action for the user.

---

## Mandatory repo workflow

### Before starting any operation
1. Refresh `main` or the target branch.
2. Read the active TODO/ledger **in full**.
3. Confirm the current head/branch.
4. Confirm the predecessor operation state.
5. State the current active phase.

### During an operation
1. Work in explicit phases.
2. Use dedicated branch names.
3. Keep patchsets ordered and named.
4. Report progress continuously.
5. Report every problem and the chosen solution.
6. Prefer real verification over assumption.

### After finishing a phase
1. Update the active TODO/ledger **as the final step**.
2. Record:
   - what was completed
   - what remains
   - blockers
   - changed files
   - next phase readiness
3. If handing off, link predecessor and successor operations explicitly.

### User rule that must be preserved
- **Each TODO read starts action.**
- **Each TODO update ends action.**

---

## Operation ledger standard

Every major repo operation should have its own file under:
- `docs/operations/`

Each ledger should include:
- operation title
- baseline commit/ref
- active branch name
- project objective
- phases
- checklists
- exit criteria
- problem ⇄ solution log
- current active phase
- predecessor link
- successor link when needed

### Ledger rule
- Never bury the operation state inside chat only.
- The repo should contain the operational memory.

---

## Branching style

### General pattern
- Use a dedicated branch per operation or patchset.
- Keep branch intent explicit in the name.

### Preferred naming
- `operation/<operation-name>-<date>`
- `patchset/<letter>-<topic>`
- `fix/<specific-followup>`

### Branch discipline
- Refresh from current `main` before opening a new operation branch.
- If `main` moves during work, do not fake continuity.
- State branch drift explicitly and replay commits if needed.

---

## Patchset logic

### Preferred order
1. semantic boundary / formal separation
2. contract clarification
3. selector/meaning repair
4. spec layer
5. runtime implementation
6. performance repair
7. semantic tests / benchmarks
8. geometry refactor last

### Why
Because semantics must stabilize before performance or structural refactor.

---

## Reporting style

### Must include
- current phase
- progress estimate
- what was just verified
- what was found
- what will be done next
- whether the issue is semantic, architectural, runtime, or tooling

### Preferred structure
- concise progress update
- one or two concrete findings
- next action

### Never do
- pretend a write succeeded when the tool failed
- imply certainty without verification
- smooth over broken assumptions

---

## Documentation rules

### Hard separation must be preserved
Keep clear boundaries between:
- `docs/analogies/`
- `docs/science/`
- `docs/operations/`
- runtime / code / executable claims

### Interpretation rule
- Analogy is not executable spec.
- Hypothesis is not implementation.
- Architecture is not proof.
- Runtime behavior must be validated from code/tests, not from rhetoric.

### When rewriting docs
Always check against:
- actual package entrypoints
- existing scripts
- workflows
- packaging surfaces
- integration registries
- active machine-readable maps

---

## Validation rules

### When touching code
- inspect the real file first
- identify exact contract assumptions
- check tests that already exist
- add or update boundary tests if contracts change

### When touching docs
- verify the implementation surface first
- then rewrite docs
- then update indices/maps if needed

### When touching machine-readable maps
- keep human docs and machine docs aligned
- update any tests that assert schema/version/state

---

## Handling blockers

### If the blocker is semantic
- stop and clarify the model
- do not patch around undefined meaning

### If the blocker is runtime/tooling
- isolate the exact failing step
- report whether it is:
  - code
  - CI
  - packaging
  - GitHub tool failure
  - branch drift

### If the blocker is the model's write path
- prepare exact manual instructions for the user
- reduce the manual action to the smallest deterministic edit
- keep the rest of the logic explicit

---

## Preferred implementation philosophy for this repo

### First fix meaning, then mechanics
For orbital / semantic systems:
1. define what the variables mean
2. define the contracts
3. define the selector logic
4. only then extend the runtime law
5. only then optimize

### Current preferred sequence for orbital work
1. semantic boundary hardening
2. phased-state contract clarification
3. identity phase vs selection relevance separation
4. orbital dynamics spec v0
5. runtime law path
6. performance repair
7. semantic benchmarks
8. package geometry refactor later

---

## Handoff rule for next session

The next session should:
1. refresh current `main`
2. read the active operation ledger in `docs/operations/`
3. confirm whether predecessor/successor links are still current
4. continue from the recorded active phase
5. update the ledger as the last step of the next finished phase

If the next session lacks repo write access or a tool fails, it should still preserve this logic and reduce any manual action to exact file edits.

---

## Short version for direct prompting

Use this repo workstyle:
- refresh the real repo state first
- read the active TODO before starting
- work in explicit phases and small coherent patchsets
- report every blocker immediately
- separate fact / inference / hypothesis / unknown
- never guess
- update the TODO as the final step of each completed phase
- keep predecessor/successor operation links explicit
- treat documentation, machine-readable maps, and implementation as one coupled system
- when blocked by tooling, reduce the remaining work to exact manual edits instead of hiding the failure
