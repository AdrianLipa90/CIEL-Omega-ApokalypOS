# Documentation Index — Refactor V2

This file is the phase-2 navigation index aligned with the new repository geometry.

It exists because the legacy `docs/INDEX.md` still points to several flat paths from the pre-refactor layout.
During migration, this file should be treated as the preferred navigation surface.

## Core architecture
- `docs/architecture/ARCHITECTURE.md` — repository role, topology, upstream bindings, and integration position.
- `docs/architecture/REPO_REFACTOR_PLAN.md` — target repository geometry, migration phases, and invariants.
- `docs/architecture/ORBITAL_ARCHITECTURE_CANON.md` — canonical architectural interpretation of the full orbital source sector.
- `governance/AGENT.md` — repository-wide operational rules for the integration attractor.

## Operations
- `docs/operations/OPERATIONS.md` — operational layer, workflow chain, launch surfaces, and automation visibility.

## Integration architecture
- `docs/integration/CIEL_OMEGA_DEMO_INTEGRATION.md` — shell-level integration bridge to `AdrianLipa90/ciel-omega-demo`.
- `docs/integration/ORBital_INTEGRATION_ADDENDUM.md` — human-readable orbital integration addendum.
- `docs/integration/ORBITAL_INFRASTRUCTURE_RULES.md` — protected-sector rules for orbital infrastructure during refactor.
- `integration/Orbital/ARCHITECTURE_BINDING.md` — binding between the imported orbital layer and the full orbital source architecture.

## Scientific and semantic notes
- `docs/analogies/RELATIONAL_ANALOGIES.md` — analogies and comparisons, explicitly marked as analogical and non-probative.
- `docs/science/HYPOTHESES.md` — scientific hypotheses and formal working claims.
- `docs/science/DERIVATION_NOTES.md` — compact derivation notes and bridges to imported anchors.

## Integration state
- `integration/repository_registry.json` — upstream repositories and local identities.
- `integration/couplings.json` — pairwise coupling strengths and relation types.
- `integration/hyperspace_index.json` — machine-readable cross-reference registry.
- `integration/upstreams/ciel_omega_demo_shell_map.json` — imported shell object map for `ciel-omega-demo`.
- `integration/upstreams/ciel_omega_demo_inventory.json` — pinned inventory snapshot of known shell-facing upstream paths.

## Orbital source and imported runtime
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/README.md` — canonical source statement for the global orbital coherence engine.
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/model.py` — orbital system state objects.
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/registry.py` — manifest-driven load layer.
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/global_pass.py` — repository-scale orbital diagnostic pass.
- `integration/Orbital/README.md` — imported runtime snapshot overview.
- `integration/Orbital/main/AGENT1.md` — local executable import rules.

## Executable native layer
- `src/ciel_sot_agent/repo_phase.py` — discrete phase-state model and Euler closure metrics.
- `src/ciel_sot_agent/synchronize.py` — CLI entrypoint for repository synchronization report.
- `src/ciel_sot_agent/index_validator.py` — machine registry validator for path, reference, placeholder, shell-map, and inventory coherence.
- `src/ciel_sot_agent/orbital_bridge.py` — native bridge layer that reduces orbital outputs into actionable integration state.

## Validation
- `tests/test_repo_phase.py` — numerical sanity tests for phase closure and pairwise tension.
- `tests/test_gh_coupling.py` — coupling and GitHub-upstream related validation.
- `tests/test_index_validator.py` — shell-map and inventory validation tests.
- `tests/test_orbital_runtime.py` — orbital runtime validation.

## Structural conclusions

1. The orbital source sector is canonical for orbital architecture.
2. The imported orbital layer is a protected integration-facing projection of that source architecture.
3. The native SOT bridge layer is downstream of orbital diagnostics and must remain distinct.
4. Repository refactor should follow this direction:
   source orbital architecture -> imported orbital runtime -> native bridge/control layer.
