# Documentation Index

## Core architecture
- `docs/ARCHITECTURE.md` — repository role, geometry, upstream bindings, and initial execution plan.
- `docs/CIEL_OMEGA_DEMO_INTEGRATION.md` — explicit shell-level integration bridge to `AdrianLipa90/ciel-omega-demo`.
- `AGENT.md` — operational rules for the integration attractor.

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

## Executable layer
- `src/ciel_sot_agent/repo_phase.py` — discrete phase-state model and Euler closure metrics.
- `src/ciel_sot_agent/synchronize.py` — CLI entrypoint for repository synchronization report.
- `src/ciel_sot_agent/index_validator.py` — machine registry validator for path, reference, placeholder, shell-map, and inventory coherence.

## Validation
- `tests/test_repo_phase.py` — numerical sanity tests for phase closure and pairwise tension.
- `tests/test_gh_coupling.py` — coupling and GitHub-upstream related validation.
- `tests/test_index_validator.py` — shell-map and inventory validation tests.

## Cross-reference anchors
- Analogies about metronomic convergence, moving substrate, and shared rhythm are connected to `docs/science/HYPOTHESES.md#h1-shared-substrate-phase-synchronization`.
- The GH-as-attractor integration strategy is connected to `docs/ARCHITECTURE.md#github-as-operational-attractor`.
- The first implementation target is connected to `docs/ARCHITECTURE.md#first-executable-component` and `src/ciel_sot_agent/repo_phase.py`.
- The shell-level bridge to `ciel-omega-demo` is connected to `docs/CIEL_OMEGA_DEMO_INTEGRATION.md`, `integration/upstreams/ciel_omega_demo_shell_map.json`, and `integration/upstreams/ciel_omega_demo_inventory.json`.
