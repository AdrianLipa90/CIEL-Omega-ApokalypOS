# SAT-NOEMA-FILESENSE-0001 — NOEMA File Sense Layer

## Identity

- id: `SAT-NOEMA-FILESENSE-0001`
- layer: satellite subsystem
- status: draft
- canonical code: `src/ciel_sot_agent/noema_file_sense.py`
- orchestrator surface: `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/ciel_orchestrator.py`
- outputs:
  - `integration/registries/file_sense_registry.json`
  - `integration/reports/file_sense_report.json`

## Role

Semantic inspection layer for repository files.
Transforms raw path inventory into NOEMA-readable records about:
- what a file is,
- where it belongs,
- what it does,
- how authoritative it is,
- whether it looks active, generated, legacy, or reference-like.

## May

- classify files by type, location, subsystem, purpose, and authority,
- expose filtered inspection through the canonical orchestrator axis,
- support cleanup planning without deleting anything,
- emit machine-readable registry/report artifacts.

## Must not

- mutate or move files by itself,
- become a fourth orchestrator surface,
- override contracts, cards, or runtime authority,
- mark canonical code as safe to delete.

## Boundary invariant

```text
inspect first → classify second → decide later
```

## Cleanup function

The subsystem is a semantic pre-cleaning layer.
It exists to answer:

```text
co / gdzie / z czym / kiedy / po co / w jakich warunkach
```

before any destructive or structural cleanup action is attempted.
