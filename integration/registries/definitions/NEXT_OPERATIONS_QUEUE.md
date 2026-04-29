# NEXT OPERATIONS QUEUE — POST ORBITAL CARD SYSTEM

## Queue policy
This file is the queued-operations ledger that begins **after** the active operation `ORBITAL CARD SYSTEM`.

Execution rule:
- queued operations do **not** start before the active operation reaches an explicit closure / gate decision
- each queued operation must be copied into an active execution ledger before execution begins
- before starting any queued operation:
  - read its full plan
  - confirm predecessor status
  - confirm blockers / prerequisites
- after closing any queued operation:
  - update this queue file as the final step

Reporting protocol:
- unchanged
- progress, blockers, problem ⇄ solution, artifact deltas, and state updates remain mandatory

---

# QUEUED OPERATION 01 — AGI CIEL CONSOLIDATION

## Status
- [ ] QUEUED
- [ ] NOT ACTIVE
- [ ] blocked until `ORBITAL CARD SYSTEM` reaches explicit closure / gate decision

## Origin
This operation is derived from the architectural proposal `AGI_CIEL_CONSOLIDATION_PROTOCOL.md`.

## Objective
Consolidate the routing, memory, web augmentation, model routing, security, and orchestration layers into a coherent AGI/CIEL data-consolidation stack.

## Declared architectural drivers
- measured orbital routing speedup and preserved precision
- identified bottlenecks in synchronous dynamics and per-query coherence
- proposed layered consolidation architecture L0-L6
- proposed sector→model routing and local/cloud orchestration
- proposed web consolidation path and strengthened security layer

## Required predecessor conditions
- [ ] `ORBITAL CARD SYSTEM` completed or explicitly gated
- [ ] fresh orbital card layer validated and understood in runtime
- [ ] current benchmark baseline preserved and archived

## CONS-Phase A — Preflight / Baseline Capture
### Goal
Establish the measurable baseline and current implementation gap before touching consolidation architecture.

### A1. Evidence capture
- [ ] collect current benchmark artifacts
- [ ] collect current routing/runtime timings
- [ ] collect current model orchestration paths
- [ ] collect current memory integration status

### A2. Gap map
- [ ] map declared L0-L6 architecture to current codebase
- [ ] identify which declared layers already exist partially
- [ ] identify which declared layers are absent
- [ ] identify synchronous bottlenecks and cache gaps

### A3. Exit criteria
- [ ] baseline captured
- [ ] declared-vs-implemented gap map exists

## CONS-Phase B — Core Routing / Coherence Consolidation
### Goal
Address the routing/coherence bottlenecks first.

### B1. Routing improvements
- [ ] inspect dynamics step execution model
- [ ] inspect coherence caching status
- [ ] inspect batch/vectorized phase computation status
- [ ] decide minimal safe refactor path

### B2. Prototype plan
- [ ] define async / cache / batch strategy
- [ ] define rollback-safe checkpoints
- [ ] define performance success metrics

### B3. Exit criteria
- [ ] routing/coherence consolidation plan is implementation-ready

## CONS-Phase C — Multi-LLM / Model Routing Layer
### Goal
Formalize and evaluate sector→model routing and smallest-sufficient-model strategy.

### C1. Mapping audit
- [ ] audit current model/router code
- [ ] compare with declared sector→model map
- [ ] identify missing local-vs-cloud routing logic

### C2. Implementation plan
- [ ] define model-selection contract
- [ ] define routing inputs: complexity / context / token budget / sector
- [ ] define safety fallback behavior

### C3. Exit criteria
- [ ] model routing layer plan is explicit and bounded

## CONS-Phase D — Web / Memory Consolidation Layer
### Goal
Connect memory, web augmentation, and orbital filtering into one coherent selection path.

### D1. Memory integration audit
- [ ] inspect M0-M9 current status
- [ ] identify which memory tiers are implemented vs declared
- [ ] identify where memory is currently disconnected from orbital routing

### D2. Web consolidation audit
- [ ] inspect current web/RAG ingestion path
- [ ] inspect where chunk routing / ranking / token budgeting already exists
- [ ] identify missing async consolidation logic

### D3. Exit criteria
- [ ] memory/web consolidation gap map exists

## CONS-Phase E — Security / Contract Hardening
### Goal
Check the declared security hardening plan against current code reality.

### E1. Declared issues
- [ ] verify compute_phase modulo state
- [ ] verify info_fidelity enforcement state
- [ ] verify input sanitization state
- [ ] verify rate limiting state
- [ ] verify contract coverage state

### E2. Hardening plan
- [ ] classify P0 / P1 / P2 gaps
- [ ] define safe implementation order

### E3. Exit criteria
- [ ] security consolidation backlog is explicit

## CONS-Phase F — Consolidation Decision Gate
### Goal
Produce a decision whether AGI_CIEL consolidation is ready for implementation as the next active project.

### Required outputs
- [ ] declared-vs-implemented matrix
- [ ] baseline performance record
- [ ] bottleneck record
- [ ] phased implementation recommendation

### Exit criteria
- [ ] operation marked either:
  - [ ] READY_TO_ACTIVATE
  - [ ] BLOCKED_BY_PREDECESSOR
  - [ ] BLOCKED_BY_ARCHITECTURAL_GAP
  - [ ] BLOCKED_BY_SECURITY_GAP

---

# QUEUED OPERATION 02 — DOCUMENTATION CONSISTENCY & COVERAGE

## Status
- [ ] QUEUED
- [ ] NOT ACTIVE
- [ ] blocked until predecessor operation status is explicit

## Objective
Update, complete, and audit documentation; compare declared documentation claims against the actual implemented system; identify what is documented but not implemented, and what is implemented but not documented.

## Required predecessor conditions
- [ ] `ORBITAL CARD SYSTEM` status explicit
- [ ] if `AGI CIEL CONSOLIDATION` is activated first, its scope decision recorded

## DOC-Phase A — Documentation Inventory
### Goal
Build a map of all relevant documentation artifacts.

### A1. Inventory scope
- [ ] README hierarchy
- [ ] AGENT / protocol files
- [ ] operations docs
- [ ] runtime entrypoint docs
- [ ] architectural design docs
- [ ] security docs
- [ ] packaging / deployment docs
- [ ] generated reports that function as living documentation

### A2. Exit criteria
- [ ] documentation inventory exists

## DOC-Phase B — Declared-vs-Implemented Audit
### Goal
Compare the documentation claims to actual system state.

### B1. Claims extraction
- [ ] extract declared components
- [ ] extract declared commands / entrypoints
- [ ] extract declared schemas / operators / subsystems
- [ ] extract declared runtime / packaging / deployment behavior

### B2. Code / runtime comparison
- [ ] mark each claim as:
  - [ ] IMPLEMENTED
  - [ ] PARTIALLY_IMPLEMENTED
  - [ ] DOCUMENTED_ONLY
  - [ ] IMPLEMENTED_BUT_UNDOCUMENTED
  - [ ] UNKNOWN / NEEDS_RUNTIME_CHECK

### B3. Exit criteria
- [ ] declared-vs-implemented matrix exists

## DOC-Phase C — Documentation Repair Plan
### Goal
Prepare the actual documentation repair / expansion sequence.

### C1. Repair classes
- [ ] missing docs for existing systems
- [ ] stale docs with outdated claims
- [ ] docs that overclaim beyond implementation
- [ ] duplicated / conflicting docs
- [ ] docs missing operational steps

### C2. Priority map
- [ ] define P0: dangerous mismatches
- [ ] define P1: runtime / operator confusion
- [ ] define P2: completeness / readability gaps

### C3. Exit criteria
- [ ] documentation repair backlog exists

## DOC-Phase D — Documentation Update Execution
### Goal
Apply documentation repairs in a controlled order.

### D1. High-priority updates
- [ ] correct false claims
- [ ] align runtime instructions with actual system
- [ ] align schema/version docs with actual emitted artifacts
- [ ] document real limitations explicitly

### D2. Coverage updates
- [ ] add missing docs for implemented features
- [ ] add missing operational runbooks
- [ ] add architectural cross-links

### D3. Exit criteria
- [ ] documentation is materially aligned with implementation state

## DOC-Phase E — Final Documentation Audit Gate
### Goal
Establish whether documentation is trustworthy enough to be treated as current system reference.

### Required outputs
- [ ] documentation inventory
- [ ] declared-vs-implemented matrix
- [ ] repair log
- [ ] unresolved documentation gap list

### Exit criteria
- [ ] operation marked either:
  - [ ] READY_TO_CLOSE
  - [ ] BLOCKED_BY_IMPLEMENTATION_DRIFT
  - [ ] BLOCKED_BY_UNVERIFIED_RUNTIME_BEHAVIOR

---

# Queue closure conditions
- [ ] queued operation 01 status explicit
- [ ] queued operation 02 status explicit
- [ ] this queue updated after any activation / closure event
