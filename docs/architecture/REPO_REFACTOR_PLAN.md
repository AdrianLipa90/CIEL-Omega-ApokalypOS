# Repository Refactor Plan

## Status

This file starts repository-geometry refactor phase 1.
The guiding rule is:

> establish the target structure first, then migrate references, then remove legacy duplicates.

This order minimizes semantic drift and reduces the chance of breaking runners, links, indices, and agent workflows.

## Observed structural problems

### 1. Governance is scattered

Governance and coordination files currently exist in the repository root.
That makes them visible, but it also mixes long-lived policy files with product-facing root structure.

### 2. `docs/` is too flat

Architectural documents, operational documents, integration addenda, plans, and micro-audits currently sit side by side.
This makes stable documentation harder to distinguish from transitional or archival material.

### 3. `integration/` mixes data classes

The `integration/` sector currently contains:
- registries,
- live GitHub snapshots,
- couplings,
- indices,
- reports,
- imported runtime sectors,
- Sapiens-facing materials.

That is valid at small scale, but it will become harder to maintain as more machine-readable state accumulates.

### 4. `src/ciel_sot_agent/` is still mostly flat

The executable package already contains several distinct roles:
- repository phase synchronization,
- GitHub coupling,
- orbital bridge,
- Sapiens interaction,
- validation helpers.

Those roles are legible, but they are not yet grouped into explicit internal subpackages.

## Target geometry

### Governance

```text
/governance
  /coordination
  /agents
```

### Documentation

```text
/docs
  /architecture
  /operations
  /integration
  /archive
  /science
  /analogies
```

### Integration data

```text
/integration
  /registries
  /couplings
  /indices
  /upstreams
  /reports
  /Orbital
  /sapiens
```

### Executable code

```text
/src/ciel_sot_agent
  /core
  /github
  /orbital
  /sapiens
  /validation
```

## Migration invariants

1. Do not silently change repo role.
   `CIEL-_SOT_Agent` remains an integration repository, not the canonical theory repo and not merely a UI shell.

2. Prefer additive migration before destructive migration.
   In early phases, copying into target sectors is safer than deleting legacy paths immediately.

3. Preserve existing operational entrypoints until replacements are verified.
   This includes scripts, workflows, and machine-readable indices.

4. Keep human-readable and machine-readable layers coupled.
   When a document becomes canonical in a new location, indices must eventually follow.

5. Separate stable docs from transient coordination and audit artifacts.

## Phase plan

### Phase 1 — establish target sectors

- create `governance/`
- create structured documentation subdirectories
- copy stable documents into their target homes
- keep legacy files intact temporarily

### Phase 2 — normalize references

- update README paths
- update indices and cross-references
- update any scripts/docs that point to legacy paths

### Phase 3 — machine-readable integration split

- separate registries, couplings, indices, and live snapshots into dedicated subdirectories
- preserve report paths only when required for compatibility

### Phase 4 — package refactor

- split `src/ciel_sot_agent/` into explicit subpackages
- keep launcher compatibility
- move tests toward matching domain structure

### Phase 5 — cleanup

- remove legacy duplicates
- collapse stale transitional paths
- declare canonical path set in README and local docs

## Phase-1 actions already started

- created `governance/`
- created `governance/coordination/`
- created `docs/architecture/`
- copied core governance and architecture material into target sectors

## Immediate next actions

1. Create `docs/operations/` and move/copy operational docs.
2. Create `docs/integration/` and move/copy integration addenda.
3. Create `docs/archive/` and relocate transitional plans and micro-audits.
4. Begin compatibility notes for future relocation of machine-readable integration files.
