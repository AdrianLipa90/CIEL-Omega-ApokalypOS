# LOCAL INFERENCE SURFACE

Canonical orbital-ethical inference surface for local tests.

Hierarchy:
- CIELOrchestrator prepares canonical Omega state
- InformationFlow carries state and inference seed only
- CIELInferenceSurface performs orbital-ethical gating
- GGUF, when present, is subordinate to that gate

Supported modes:
- handshake
- status
- process
- json

Dry-run is the default. GGUF-wrapped execution is optional and only attempted when a backend is configured.

Repo-local wrapper:
- `python scripts/run_ciel_inference_surface.py --mode handshake`
