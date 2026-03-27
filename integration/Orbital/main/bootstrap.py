from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .extract_geometry import DEFAULT_COUPLINGS, DEFAULT_SECTORS


def ensure_orbital_manifests(orbital_root: str | Path) -> dict[str, Any]:
    orbital_root = Path(orbital_root)
    manifests_dir = orbital_root / 'manifests'
    manifests_dir.mkdir(parents=True, exist_ok=True)

    sectors_path = manifests_dir / 'sectors_global.json'
    couplings_path = manifests_dir / 'couplings_global.json'

    created_defaults = False

    if not sectors_path.exists():
        sectors_path.write_text(json.dumps({'sectors': DEFAULT_SECTORS}, ensure_ascii=False, indent=2), encoding='utf-8')
        created_defaults = True

    if not couplings_path.exists():
        couplings_path.write_text(json.dumps({'couplings': DEFAULT_COUPLINGS}, ensure_ascii=False, indent=2), encoding='utf-8')
        created_defaults = True

    return {
        'orbital_root': str(orbital_root),
        'manifests_dir': str(manifests_dir),
        'sectors_path': str(sectors_path),
        'couplings_path': str(couplings_path),
        'created_defaults': created_defaults,
    }


def ensure_orbital_report_dirs(orbital_root: str | Path) -> dict[str, str]:
    orbital_root = Path(orbital_root)
    reports_root = orbital_root / 'reports' / 'global_orbital_coherence_pass'
    reports_root.mkdir(parents=True, exist_ok=True)
    return {
        'reports_root': str(reports_root),
        'summary_json': str(reports_root / 'summary.json'),
        'summary_md': str(reports_root / 'summary.md'),
        'real_geometry_json': str(reports_root / 'real_geometry.json'),
    }
