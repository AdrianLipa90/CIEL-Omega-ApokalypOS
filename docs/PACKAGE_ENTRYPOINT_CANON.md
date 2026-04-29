# Package Entrypoint Canon

## Canonical entrypoint (updated 2026-04-17)

**`CIEL_CANON.py`** at project root is the single canonical entry point for any agent.

```bash
python3 CIEL_CANON.py              # status
python3 CIEL_CANON.py --run        # full pipeline
python3 CIEL_CANON.py --sub start  # subconsciousness
```

## Pipeline module sequence

```
ciel_sot_agent.synchronize      # Layer 1
ciel_sot_agent.orbital_bridge   # Layers 2+3+4
ciel_sot_agent.ciel_pipeline    # Layer Ω
```

Run with: `python3 -m <module>` using venv at `../venv/bin/python3`.

## Engine path

`CIEL_CANON.py` → `ciel_pipeline.py` → `_get_engine()` adds
`src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/` to `sys.path` then imports
`from ciel.engine import CielEngine`.

## Legacy note
Previous canonical split (`python -m ciel`, `CielEngine → CIELOrchestrator → CIELClient`)
remains valid for direct engine access but is not the primary operational path.
