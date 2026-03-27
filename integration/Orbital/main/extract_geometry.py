from __future__ import annotations

import json
from pathlib import Path

DEFAULT_SECTORS = {
    'constraints': {
        'orbital_level': 1,
        'orbital_type': 'constraint',
        'dominant_spin': 'up',
        'theta': 0.52,
        'phi': 0.00,
        'rhythm_ratio': 1.00,
        'amplitude': 0.55,
        'coherence_weight': 1.00,
        'info_mass': 1.00,
        'q_target': 1,
        'damping': 0.18,
        'preference': 0.85,
    },
    'fields': {
        'orbital_level': 2,
        'orbital_type': 'field',
        'dominant_spin': 'up',
        'theta': 0.90,
        'phi': 0.60,
        'rhythm_ratio': 1.08,
        'amplitude': 0.62,
        'coherence_weight': 0.92,
        'info_mass': 0.95,
        'q_target': 2,
        'damping': 0.17,
        'preference': 0.78,
    },
    'runtime': {
        'orbital_level': 2,
        'orbital_type': 'runtime',
        'dominant_spin': 'up',
        'theta': 1.05,
        'phi': 1.25,
        'rhythm_ratio': 1.12,
        'amplitude': 0.68,
        'coherence_weight': 0.96,
        'info_mass': 0.98,
        'q_target': 2,
        'damping': 0.16,
        'preference': 0.82,
    },
    'memory': {
        'orbital_level': 4,
        'orbital_type': 'memory',
        'dominant_spin': 'down',
        'theta': 1.75,
        'phi': 2.10,
        'rhythm_ratio': 0.94,
        'amplitude': 0.74,
        'coherence_weight': 0.90,
        'info_mass': 1.02,
        'q_target': 4,
        'damping': 0.19,
        'preference': 0.76,
    },
    'bridge': {
        'orbital_level': 2,
        'orbital_type': 'bridge',
        'dominant_spin': 'up',
        'theta': 1.18,
        'phi': 2.80,
        'rhythm_ratio': 1.03,
        'amplitude': 0.60,
        'coherence_weight': 0.88,
        'info_mass': 0.86,
        'q_target': 2,
        'damping': 0.18,
        'preference': 0.74,
    },
    'vocabulary': {
        'orbital_level': 1,
        'orbital_type': 'semantic',
        'dominant_spin': 'down',
        'theta': 0.70,
        'phi': 3.60,
        'rhythm_ratio': 0.98,
        'amplitude': 0.52,
        'coherence_weight': 0.84,
        'info_mass': 0.80,
        'q_target': 1,
        'damping': 0.20,
        'preference': 0.70,
    },
}

DEFAULT_COUPLINGS = {
    'constraints': {'fields': 0.92, 'runtime': 0.95, 'memory': 0.70, 'bridge': 0.82, 'vocabulary': 0.76},
    'fields': {'runtime': 0.88, 'memory': 0.72, 'bridge': 0.79, 'vocabulary': 0.68},
    'runtime': {'memory': 0.80, 'bridge': 0.90, 'vocabulary': 0.66},
    'memory': {'bridge': 0.71, 'vocabulary': 0.78},
    'bridge': {'vocabulary': 0.74},
}


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parent


def _manifests_dir(repo_root: Path) -> Path:
    return repo_root / 'manifests'


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def build(repo_root: Path) -> dict:
    manifests_dir = _manifests_dir(repo_root)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    sectors_path = manifests_dir / 'sectors_global.json'
    couplings_path = manifests_dir / 'couplings_global.json'

    sectors_data = _load_json(sectors_path)
    couplings_data = _load_json(couplings_path)

    sectors = sectors_data if sectors_data and 'sectors' in sectors_data else {'sectors': DEFAULT_SECTORS}
    couplings = couplings_data if couplings_data and 'couplings' in couplings_data else {'couplings': DEFAULT_COUPLINGS}

    return {
        'repo_root': str(repo_root),
        'geometry_source': 'manifests' if sectors_data and couplings_data else 'default_minimal_geometry',
        'sectors': sectors,
        'couplings': couplings,
    }
