# Markdown Audit Notes

Status: **working audit note** after repository markdown inspection and cleanup.

## What was inspected

Inspected markdown classes:
- repo-level scope and mechanism docs
- embedded runtime READMEs
- orbital subsystem docs
- vocabulary / memory / bridge subsystem READMEs
- audit reports and generated summaries
- manual upload reference markdown files

## Main findings

### 1. Canon drift
Several markdown files describe the same system from different phases of the project.
Main risk:
- future / aspirational architecture stated as if already implemented
- old marketing language treated as runtime fact

### 2. Implementation drift
The embedded runtime is healthy and testable, but some markdown files overstated current integration status.
Most important example:
- the orbital subsystem is implemented and functional as a diagnostic engine,
- but it is not yet documented as fully closing the runtime decision loop.

### 3. Historical files remain valuable
Older documents preserve design intent and architecture lineage, but need explicit status labels so they are not mistaken for current build truth.

## Updates applied in this audit round

### Updated
- `README.md`
- `docs/DOCUMENTATION_CANON.md` (new)
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/README.md`
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/README.md`
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/README_old.md`
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/README.md`

### Intent of edits
- reduce false certainty
- distinguish canonical vs historical documents
- align test counts and implementation claims with the audited workspace
- keep conceptual language, but mark non-implemented layers honestly

## Current documentation posture

### Confirmed
- repository mechanism scope
- current testable state of the embedded runtime
- orbital subsystem exists and runs as analysis / diagnostics
- package imports and CLI smoke path are healthy in this workspace

### Partial
- active coupling of orbital metrics into runtime decision policy
- full end-to-end autonomy layer
- product-level cockpit / native control interface

### Not yet proven here
- final metric closure
- final `D_f`
- final `J(epsilon)`
- complete productization of the orbital architecture

## Recommendation

When editing or extending docs, preserve this distinction:
- **implemented**
- **partially implemented**
- **planned / conceptual**
