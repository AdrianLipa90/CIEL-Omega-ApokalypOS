# Orbital Many-Body TODO Ledger

## Phase 1 — Card schema v0.2 ✅
## Phase 2 — Systemic privacy and internal cards ✅
## Phase 3 — Horizon/leak policy formalization ✅
## Phase 4 — Synchronization scaffolding ✅
- [x] define board/subsystem aggregation object
- [x] define `tau_local`, `tau_orbit`, `tau_system`
- [x] connect cards to synchronization metadata
- [x] define how internal subsystem state condenses into exportable half-conclusions
- [x] define first subsystem synchronization law (board / metronome style)

## Phase 5 — Runtime integration ✅
- [x] feed richer cards into orbital runtime bridge
- [x] feed richer cards into bridge reports
- [x] feed privacy constraints into export boundaries
- [x] project runtime gating into sapiens packets
- [x] add runtime integration regression tests

## Phase 6 — Verification ⏳
- [x] add dedicated verification script
- [x] wire verification into catalog hook chain
- [ ] rerun catalog hook end-to-end on branch
- [ ] rerun DB library build end-to-end on branch
- [ ] verify no recursion reintroduced
- [ ] verify deterministic rerun stability
- [ ] verify internal cards are not exported directly
- [ ] verify horizon projection only exports allowed fields
- [ ] verify runtime gating artifacts are emitted on rerun
- [ ] finalize docs / audit summary
