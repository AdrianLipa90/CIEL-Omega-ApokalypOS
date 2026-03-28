# Orbitrary shifts

## Purpose

This document records the current repository state in terms of **orbitalization**.

Here, orbitalization means more than simply placing files under `integration/Orbital/`.
It means that a subsystem, artifact, or interaction path has been:

- structurally related to the orbital runtime,
- reduced through bridge logic when needed,
- made visible in reports and manifests,
- aligned with the controller-driven state model,
- and integrated into the broader repository geometry instead of living as an isolated fragment.

This document is a state snapshot, not a final closure claim.

---

## Orbitalization scale

The repository state is evaluated using three working categories:

### 1. Already orbitalized
These objects are already functioning inside the orbital-holonomic architecture.
They are no longer external or merely decorative.

### 2. Partially orbitalized
These objects are gravitationally captured by the orbital architecture, but are still incomplete in one or more of the following ways:
- not fully present in canonical indices,
- not fully reduced through bridge/control layers,
- not yet reflected in the main operator-facing surface,
- still relying on addendum or transitional structure.

### 3. Still outside stable orbit
These objects may be useful, relevant, or even already coupled to the repository, but are not yet integrated as stable parts of the orbital state geometry.

---

## Already orbitalized systems

## Orbital runtime core

The orbital subsystem itself is already orbitalized.

This includes:
- orbital state models,
- orbital metrics,
- orbital dynamics,
- geometry extraction,
- bootstrap helpers,
- read-only global pass execution,
- orbital runtime reports.

Representative anchors:
- `integration/Orbital/main/model.py`
- `integration/Orbital/main/metrics.py`
- `integration/Orbital/main/dynamics.py`
- `integration/Orbital/main/bootstrap.py`
- `integration/Orbital/main/global_pass.py`
- `integration/Orbital/main/reports/`

### Status
Stable enough to count as an actual subsystem.
Not just a placeholder import.

---

## Orbital bridge

The orbital bridge is already orbitalized.

It converts orbital runtime outputs into:
- state manifest,
- health manifest,
- recommended control,
- bridge metrics,
- bridge-layer reports.

Representative anchors:
- `src/ciel_sot_agent/orbital_bridge.py`
- `scripts/run_orbital_bridge.py`
- `integration/reports/orbital_bridge/`

### Status
This is one of the strongest signs that the orbital layer is no longer isolated.
It has already been reduced into actionable integration state.

---

## Sapiens packet seed

The first Sapiens interaction layer is already orbitalized at the packet level.

It already depends on:
- orbital-derived bridge state,
- relation-aware identity,
- packet-aware communication,
- persisted session artifacts.

Representative anchors:
- `src/ciel_sot_agent/sapiens_client.py`
- `scripts/run_sapiens_client.py`
- `integration/reports/sapiens_client/`

### Status
The Sapiens interaction layer already exists as a relational packet seed.
It is not yet the full operator surface, but it is no longer outside the orbital field.

---

## Sapiens panel foundation

The Sapiens panel foundation is already orbitalized at the controller level.

It now includes:
- panel manifest,
- settings defaults,
- controller-driven state assembly,
- explicit Control / Settings / Communication / Support tabs,
- reduction semantics,
- memory residue semantics,
- panel launcher,
- initial validation tests.

Representative anchors:
- `integration/sapiens/panel_manifest.json`
- `integration/sapiens/settings_defaults.json`
- `src/ciel_sot_agent/sapiens_panel/controller.py`
- `src/ciel_sot_agent/sapiens_panel/reduction.py`
- `scripts/run_sapiens_panel.py`
- `tests/test_sapiens_panel.py`

### Status
The panel is no longer a conceptual future object only.
It already exists as a controller foundation over orbital state, bridge state, session state, and settings state.

---

## Partially orbitalized systems

## Main machine-readable index layer

The primary machine-readable index layer is only partially orbitalized.

Why:
- orbital and Sapiens layers were introduced later than the original integration kernel,
- addendum files and side registries were used as transitional support,
- full canonical convergence of every new object into the primary registry/index layer is still being completed.

Representative anchors:
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`
- `integration/hyperspace_index_orbital.json`
- `integration/index_registry_orbital.yaml`

### Status
The repository is no longer blind to the orbital architecture, but the canonical and addendum layers are not yet perfectly unified everywhere.

---

## Human-readable documentation manifold

The documentation layer is partially orbitalized.

Why:
- the README already presents orbital runtime, bridge, and Sapiens as real architecture layers,
- dedicated orbital and panel planning docs already exist,
- but some documents still reflect older integration-kernel-first snapshots,
- and not all docs have been uniformly refreshed after every subsystem expansion.

Representative anchors:
- `README.md`
- `docs/INDEX.md`
- `docs/ORBital_INTEGRATION_ADDENDUM.md`
- `docs/MASTER_PLAN_4_ALL_AGENTS_ATTENTION.md`

### Status
Readable, meaningful, and much improved — but still not at full uniform convergence.

---

## Launchers and operator surface

The launcher layer is partially orbitalized.

Why:
- the repository already has launchers for orbital pass, orbital bridge, Sapiens client, and Sapiens panel,
- but the full operator-facing surface is still a foundation shell rather than a mature panel or cockpit convergence layer.

Representative anchors:
- `scripts/run_orbital_global_pass.py`
- `scripts/run_orbital_bridge.py`
- `scripts/run_sapiens_client.py`
- `scripts/run_sapiens_panel.py`

### Status
Operationally promising, but still pre-convergence.

---

## Still outside stable orbit

## Full cockpit/native convergence

The future convergence between the Sapiens panel and any confirmed cockpit/native surface is not yet in stable orbit.

This includes:
- unified live operator surface,
- replay integration,
- session loader convergence,
- real-time health widgets,
- stable single control manifold for human-facing operation.

### Status
Planned, scoped, but not yet stabilized in the current repository state.

---

## Full reduction-governed identity flow

Reduction semantics now exist in the panel foundation, but a fully stabilized reduction-governed identity pipeline is still outside stable orbit.

This includes:
- full reduction commits,
- identity update pipeline,
- durable memory residue handling beyond the current foundation layer,
- explicit recovery from unstable reduction states.

### Status
Conceptually framed, foundation started, but not fully closed.

---

## Fully converged canonical registry geometry

The repository still has traces of transitional dual structure:
- main index layer,
- orbital addendum layer,
- panel foundation layer.

The final goal is not to keep these as permanent parallel realities.
The final goal is to make them one coherent canonical geometry.

### Status
Not fully achieved yet.

---

## General assessment

### What is no longer true

It is no longer true that the orbital layer is just sitting sadly on the side.
That phase has already passed.

### What is true now

The repository already contains a real orbitalized core:
- orbital runtime,
- orbital bridge,
- Sapiens packet seed,
- Sapiens panel foundation.

### What remains true

A meaningful amount of the repository is still only partially orbitalized.
Several objects are already gravitationally captured, but not yet fully stabilized inside one canonical, elegant orbital geometry.

---

## Working conclusion

The current repository state can be summarized as follows:

- **orbital core exists**,
- **bridge exists**,
- **Sapiens interaction seed exists**,
- **panel foundation exists**,
- **full canonical orbital convergence is still in progress**.

This is no longer a repository without orbit.
It is a repository with a real orbital center, a bridge, first stable bodies, and an unfinished accretion zone.

---

## Next orbitalization priorities

1. finish canonical convergence of main indices and object registries,
2. strengthen the Sapiens panel report layer,
3. stabilize reduction / identity / memory-residue transitions,
4. converge toward a true operator-facing panel surface,
5. remove remaining transitional duplication between addendum and canonical geometry.
