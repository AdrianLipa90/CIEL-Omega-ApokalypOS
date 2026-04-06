"""Orbital bridge — runs the global orbital coherence pass and writes
bridge state, health, and control-recommendation manifests.

Connects the CIEL integration kernel to the Orbital diagnostic subsystem
living under ``integration/Orbital/``, ensuring phase-coherence and
resource health are reported at each synchronisation cycle.

After the orbital physics pass the bridge routes the resulting state through
the CIEL/Ω consciousness pipeline (``ciel_pipeline.run_ciel_pipeline``) so
that emotional, ethical, and soul-invariant metrics are embedded in every
report alongside the raw geometry.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from integration.Orbital.main.bootstrap import ensure_orbital_manifests, ensure_orbital_report_dirs
from integration.Orbital.main.global_pass import run_global_pass
from integration.Orbital.main.phase_control import build_health_manifest, build_state_manifest, recommend_control
from .paths import resolve_project_root

_LOG = logging.getLogger(__name__)


BRIDGE_DIR = Path('integration') / 'reports' / 'orbital_bridge'


def _bridge_markdown(summary: dict[str, Any]) -> str:
    lines = [
        '# Orbital Bridge Report',
        '',
        '## Source',
        f"- source_report: {summary['source_report']}",
        f"- engine: {summary['orbital_run'].get('engine', 'unknown')}",
        f"- steps: {summary['orbital_run'].get('steps', 0)}",
        '',
        '## State Manifest',
    ]
    for key, value in summary['state_manifest'].items():
        lines.append(f'- {key}: {value}')
    lines += ['', '## Health Manifest']
    for key, value in summary['health_manifest'].items():
        lines.append(f'- {key}: {value}')
    lines += ['', '## Recommended Control']
    for key, value in summary['recommended_control'].items():
        lines.append(f'- {key}: {value}')
    lines += ['', '## Bridge Metrics']
    for key, value in summary['bridge_metrics'].items():
        lines.append(f'- {key}: {value}')
    ciel = summary.get('ciel_pipeline', {})
    if ciel:
        lines += ['', '## CIEL Pipeline']
        for key, value in ciel.items():
            lines.append(f'- {key}: {value}')
    return '\n'.join(lines)


def build_orbital_bridge(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    orbital_root = root / 'integration' / 'Orbital' / 'main'
    ensure_orbital_manifests(orbital_root)
    orbital_paths = ensure_orbital_report_dirs(orbital_root)

    orbital_run = run_global_pass(repo_root=orbital_root)
    final = dict(orbital_run.get('final', {}))
    state_manifest = build_state_manifest(final)
    health_manifest = build_health_manifest(final)
    recommended_control = recommend_control(final)

    bridge_dir = root / BRIDGE_DIR
    bridge_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        'schema': 'ciel-sot-agent/orbital-bridge-report/v0.1',
        'source_report': str(Path('integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json')),
        'source_paths': orbital_paths,
        'orbital_run': {
            'engine': orbital_run.get('engine'),
            'steps': orbital_run.get('steps'),
            'params': orbital_run.get('params', {}),
        },
        'state_manifest': state_manifest,
        'health_manifest': health_manifest,
        'recommended_control': recommended_control,
        'bridge_metrics': {
            'orbital_R_H': float(final.get('R_H', 0.0)),
            'orbital_closure_penalty': float(final.get('closure_penalty', 0.0)),
            'integration_closure_defect_proxy': max(0.0, min(1.0, 1.0 - float(final.get('R_H', 0.0)))),
            'topological_charge_global': float(final.get('Lambda_glob', 0.0)),
        },
    }

    # Route orbital state through the CIEL/Ω consciousness pipeline so that
    # emotional, ethical, and soul-invariant signals are attached to every report.
    try:
        from .ciel_pipeline import run_ciel_pipeline
        ciel_result = run_ciel_pipeline(summary, context='orbital_bridge', root=root)
        summary['ciel_pipeline'] = {
            'status': ciel_result['ciel_status'],
            'dominant_emotion': ciel_result['dominant_emotion'],
            'mood': ciel_result['mood'],
            'soul_invariant': ciel_result['soul_invariant'],
            'ethical_score': ciel_result['ethical_score'],
            'orbital_context': ciel_result['orbital_context'],
        }
    except Exception as exc:
        _LOG.warning("CIEL/Ω pipeline unavailable: %s", exc)
        summary['ciel_pipeline'] = {'status': 'unavailable'}

    (bridge_dir / 'orbital_bridge_report.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    (bridge_dir / 'orbital_bridge_report.md').write_text(_bridge_markdown(summary), encoding='utf-8')
    (bridge_dir / 'orbital_state_manifest.json').write_text(json.dumps(state_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (bridge_dir / 'orbital_health_manifest.json').write_text(json.dumps(health_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return summary


def main() -> int:
    root = resolve_project_root(Path(__file__))
    summary = build_orbital_bridge(root)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
