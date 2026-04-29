# Local CIEL Test Surface

This document defines the **canonical local test surface** for CIEL/Ω inside
`CIEL-_SOT_Agent`.

## Purpose
One stable local entrypoint for:
- handshake
- status
- process
- JSON payload communication

without calling internal Omega files directly from ad hoc commands.

## Hierarchy
`CielEngine -> CIELOrchestrator -> CIELClient -> LocalCielSurface`

## Entry points
### Packaged CLI
```bash
python -m src.ciel_sot_agent.local_ciel_surface --surface client --mode handshake
```

### Thin wrapper
```bash
python scripts/run_ciel_local_surface.py --surface client --mode handshake
```

## Supported surfaces
- `client`
- `orchestrator`

## Supported modes
- `handshake`
- `status`
- `process --text "..."`
- `json --json-payload '{"action":"process","text":"..."}'`

## Rationale
This surface exists so that local testing does not depend on remembering the
internal Omega file layout. It also gives one stable place to evolve minimal
communication semantics.
