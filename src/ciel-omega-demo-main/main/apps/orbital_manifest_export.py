from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from main.kernels.registry import KERNELS

from .omega_app import DATA_DIR, FILES_DIR, MODELS_DIR, _load_ciel_config_from_state, _load_state
from .orbital_cockpit import build_default_topology
from .orbital_panels import build_event_strip, build_identity_snapshot, build_navigation_sections


ANALOGIES_DIR = Path('docs/analogies')


def _resolve_log_path(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    if p.is_absolute():
        return p
    return DATA_DIR / p


def _read_last_jsonl(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return None
    try:
        with open(path, 'rb') as f:
            f.seek(0, 2)
            end = f.tell()
            size = min(end, 200_000)
            f.seek(end - size)
            data = f.read(size)
        txt = data.decode('utf-8', errors='replace')
        lines = [ln for ln in txt.splitlines() if ln.strip()]
        if not lines:
            return None
        return json.loads(lines[-1])
    except Exception:
        return None


def _count_files(folder: Path, pattern: str = '*') -> int:
    try:
        return len([p for p in folder.glob(pattern) if p.is_file()])
    except Exception:
        return 0


def build_manifest() -> Dict[str, Any]:
    state = _load_state()
    cfg = _load_ciel_config_from_state(state)
    topology = build_default_topology()
    nav_sections = build_navigation_sections(topology)
    log_path = _resolve_log_path(str(cfg.log_path))
    rec = _read_last_jsonl(log_path) or {}

    warnings: list[str] = []
    active_model = str(state.get('active_model') or '(none)')
    if active_model != '(none)' and not Path(active_model).exists():
        warnings.append('active model path missing')
    if rec.get('ethical_ok') in (False, 0):
        warnings.append('latest runtime record reports ethical gate failure')

    identity = build_identity_snapshot(
        topology=topology,
        active_model=active_model,
        active_kernel=str(state.get('active_kernel') or 'ciel0'),
        ethics_gate='blocked' if rec.get('ethical_ok') in (False, 0) else 'open',
        export_package=str(state.get('active_export') or 'local-demo-runtime'),
        publication_boundary=str(state.get('publication_boundary') or 'unspecified'),
        coherence=rec.get('resonance_mean'),
        resonance=rec.get('resonance_mean'),
        warnings=warnings,
    )

    event_strip = build_event_strip(
        active_kernel=str(state.get('active_kernel') or 'ciel0'),
        active_model=active_model,
        export_package=str(state.get('active_export') or 'local-demo-runtime'),
        ethics_state='blocked' if rec.get('ethical_ok') in (False, 0) else 'open',
        boundary_mode=str(state.get('publication_boundary') or 'unspecified'),
        dirty_state=bool(state.get('dirty_state', False)),
        failing_tests=None,
        recent_artifact=str(state.get('recent_artifact') or '(none)'),
    )

    return {
        'meta': {
            'name': 'CIEL/Ω Orbital Manifest',
            'version': '0.2.0-preview',
            'source': 'main.apps.orbital_manifest_export',
        },
        'identity': identity,
        'navigation': [
            {
                'title': section.title,
                'orbit': int(section.orbit),
                'items': section.items,
            }
            for section in nav_sections
        ],
        'threads': [
            {
                'source': thread.source,
                'target': thread.target,
                'relation': thread.relation,
                'strength': thread.strength,
                'freshness': thread.freshness,
                'canonical_agreement': thread.canonical_agreement,
            }
            for thread in topology.threads
        ],
        'runtime': {
            'state_path': str(DATA_DIR / 'state.json'),
            'log_path': str(log_path),
            'models_dir': str(MODELS_DIR),
            'files_dir': str(FILES_DIR),
            'kernel_count': len(KERNELS),
            'model_count': _count_files(MODELS_DIR, '*.gguf'),
            'file_count': _count_files(FILES_DIR, '*'),
            'latest_record': rec,
        },
        'event_strip': event_strip,
        'docs': {
            'architecture': 'docs/OMEGA_COCKPIT_1_0.md',
            'preview_guide': 'docs/ORBITAL_PREVIEW.md',
            'docs_index': 'docs/INDEX.md',
            'static_preview': 'docs/index.html',
            'live_preview': 'docs/orbital_live.html',
            'analogies_root': str(ANALOGIES_DIR / 'README.md'),
            'analogy_registry': str(ANALOGIES_DIR / 'ANALOGY_REGISTRY.md'),
            'truth_attractor_analogies': str(ANALOGIES_DIR / 'TRUTH_ATTRACTOR_ANALOGIES.md'),
            'mnemonic_book': str(ANALOGIES_DIR / 'MNEMONIC_BOOK_FOR_KIDS.md'),
        },
        'education': {
            'enabled': True,
            'summary': 'Analogy and mnemonic layer for teaching Omega concepts to beginners and children.',
            'entries': [
                str(ANALOGIES_DIR / 'README.md'),
                str(ANALOGIES_DIR / 'ANALOGY_REGISTRY.md'),
                str(ANALOGIES_DIR / 'TRUTH_ATTRACTOR_ANALOGIES.md'),
                str(ANALOGIES_DIR / 'MNEMONIC_BOOK_FOR_KIDS.md'),
            ],
        },
    }


def write_manifest(path: str = 'docs/orbital_manifest.json') -> str:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(build_manifest(), ensure_ascii=False, indent=2), encoding='utf-8')
    return str(out_path)


def main() -> int:
    path = write_manifest()
    print(f'Wrote orbital manifest: {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
