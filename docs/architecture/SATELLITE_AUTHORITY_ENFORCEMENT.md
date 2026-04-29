# Satellite Authority Enforcement

This pass moves satellite authority from passive documentation into active code surfaces.

Enforced surfaces:
- NOEMA export (`scripts/export_orbital_registry_to_noema.py`)
- Sapiens interaction (`src/ciel_sot_agent/sapiens_client.py`)
- Audio orbital probe (`scripts/run_audio_orbital_probe.py`)

Rule:
- runtime canon remains upstream
- satellite surfaces may project, interact, or probe only within their declared class
- satellite surfaces must not silently become independent sources of truth
