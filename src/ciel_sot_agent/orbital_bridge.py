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
DEFINITIONS_DIR = Path('integration') / 'registries' / 'definitions'


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        _LOG.warning("Could not load %s: %s", path, exc)
        return None


def _build_sync_manifest(root: Path) -> dict[str, Any]:
    defs_root = root / DEFINITIONS_DIR
    sync_registry = _load_json_if_exists(defs_root / 'subsystem_sync_registry.json') or {}
    sync_report = _load_json_if_exists(defs_root / 'subsystem_sync_report.json') or {}
    orbital_report = _load_json_if_exists(defs_root / 'orbital_assignment_report.json') or {}
    horizon_policy = _load_json_if_exists(defs_root / 'horizon_policy_matrix.json') or {}
    nonlocal_cards = _load_json_if_exists(defs_root / 'nonlocal_cards_registry.json') or {}

    boards = sync_registry.get('records', [])
    board_preview = [
        {
            'board_card_id': board.get('board_card_id'),
            'tau_orbit': board.get('tau_orbit'),
            'tau_system': board.get('tau_system'),
            'member_count': board.get('member_count'),
            'board_export_result': board.get('board_export_result'),
            'aggregation_model': board.get('aggregation_model'),
        }
        for board in boards[:5]
    ]
    classes = (horizon_policy.get('classes') or {})
    export_boundary_policy = {
        horizon_class: {
            'privacy_constraint': payload.get('privacy_constraint'),
            'leak_channel_mode': payload.get('leak_channel_mode'),
            'leak_budget_class': payload.get('leak_budget_class'),
            'exportable_fields': payload.get('exportable_fields', []),
        }
        for horizon_class, payload in classes.items()
    }
    nonlocal_records = nonlocal_cards.get('records', [])
    nonlocal_card_manifest = {
        'registry_present': bool(nonlocal_cards),
        'card_count': len(nonlocal_records),
        'active_statuses': sorted({rec.get('active_status') for rec in nonlocal_records if rec.get('active_status')}),
        'classes': sorted({rec.get('class') for rec in nonlocal_records if rec.get('class')}),
        'card_ids': [rec.get('card_id') for rec in nonlocal_records],
    }

    return {
        'schema': 'ciel-sot-agent/subsystem-sync-manifest/v0.1',
        'sync_registry_present': bool(sync_registry),
        'sync_report_present': bool(sync_report),
        'board_count': sync_report.get('board_count', len(boards)),
        'avg_members_per_board': sync_report.get('avg_members_per_board', 0.0),
        'tau_orbit_count': sync_report.get('tau_orbit_count', 0),
        'tau_system_count': sync_report.get('tau_system_count', 0),
        'sync_law_counts': sync_report.get('sync_law_counts', {}),
        'condensation_operator_counts': sync_report.get('condensation_operator_counts', {}),
        'sync_scope_counts': sync_report.get('sync_scope_counts', {}),
        'privacy_constraint_counts': orbital_report.get('privacy_constraint_counts', {}),
        'horizon_class_counts': orbital_report.get('horizon_class_counts', {}),
        'export_boundary_policy': export_boundary_policy,
        'nonlocal_card_manifest': nonlocal_card_manifest,
        'board_preview': board_preview,
    }


def _build_runtime_gating(sync_manifest: dict[str, Any]) -> dict[str, Any]:
    privacy_counts = sync_manifest.get('privacy_constraint_counts', {}) or {}
    horizon_counts = sync_manifest.get('horizon_class_counts', {}) or {}
    board_count = int(sync_manifest.get('board_count', 0) or 0)
    tau_system_count = int(sync_manifest.get('tau_system_count', 0) or 0)
    dominant_privacy = max(privacy_counts.items(), key=lambda kv: kv[1])[0] if privacy_counts else 'UNKNOWN'
    dominant_horizon = max(horizon_counts.items(), key=lambda kv: kv[1])[0] if horizon_counts else 'UNKNOWN'
    return {
        'schema': 'ciel-sot-agent/runtime-gating/v0.1',
        'dominant_privacy_constraint': dominant_privacy,
        'dominant_horizon_class': dominant_horizon,
        'export_boundary_mode': 'PROJECTED_ONLY',
        'private_state_export_allowed': False,
        'board_sync_ready': board_count > 0,
        'system_tau_coherent': tau_system_count <= 1,
        'requires_projection_operator': True,
    }


def _bridge_markdown(summary: dict[str, Any]) -> str:
    lines = [
        '# Orbital Bridge Report', '', '## Source',
        f"- source_report: {summary['source_report']}",
        f"- engine: {summary['orbital_run'].get('engine', 'unknown')}",
        f"- steps: {summary['orbital_run'].get('steps', 0)}", '', '## State Manifest',
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
    sync_manifest = summary.get('subsystem_sync_manifest', {})
    if sync_manifest:
        lines += ['', '## Subsystem Sync Manifest']
        for key in ['board_count', 'avg_members_per_board', 'tau_orbit_count', 'tau_system_count']:
            lines.append(f'- {key}: {sync_manifest.get(key)}')
        nonlocal_cards = sync_manifest.get('nonlocal_card_manifest', {})
        if nonlocal_cards:
            lines.append(f"- nonlocal_card_count: {nonlocal_cards.get('card_count')}")
            lines.append(f"- nonlocal_card_classes: {', '.join(nonlocal_cards.get('classes', []))}")
    runtime_gating = summary.get('runtime_gating', {})
    if runtime_gating:
        lines += ['', '## Runtime Gating']
        for key, value in runtime_gating.items():
            if key != 'schema':
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
    entity_orbital = orbital_run.get('entity_orbital', {})
    sync_manifest = _build_sync_manifest(root)
    runtime_gating = _build_runtime_gating(sync_manifest)

    bridge_dir = root / BRIDGE_DIR
    bridge_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        'schema': 'ciel-sot-agent/orbital-bridge-report/v0.2',
        'source_report': str(Path('integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json')),
        'source_paths': orbital_paths,
        'orbital_run': {'engine': orbital_run.get('engine'), 'steps': orbital_run.get('steps'), 'params': orbital_run.get('params', {})},
        'state_manifest': {},
        'health_manifest': {},
        'recommended_control': {},
        'subsystem_sync_manifest': sync_manifest,
        'runtime_gating': runtime_gating,
        'bridge_metrics': {
            'orbital_R_H': float(final.get('R_H', 0.0)),
            'orbital_closure_penalty': float(final.get('closure_penalty', 0.0)),
            'integration_closure_defect_proxy': max(0.0, min(1.0, 1.0 - float(final.get('R_H', 0.0)))),
            'topological_charge_global': float(final.get('Lambda_glob', 0.0)),
            'subsystem_board_count': int(sync_manifest.get('board_count', 0) or 0),
            'tau_system_count': int(sync_manifest.get('tau_system_count', 0) or 0),
            'nonlocal_card_count': int((sync_manifest.get('nonlocal_card_manifest') or {}).get('card_count', 0) or 0),
        },
        'entity_orbital': entity_orbital,
    }

    control_view = dict(final)
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
            'phi_ab_mean': ciel_result.get('phi_ab_mean', 0.0),
            'phi_berry_mean': ciel_result.get('phi_berry_mean', 0.0),
            'eba_defect_mean': ciel_result.get('eba_defect_mean', 0.0),
            'nonlocal_coherent_fraction': ciel_result.get('nonlocal_coherent_fraction', 0.0),
            'bridge_closure_score': ciel_result.get('bridge_closure_score', 0.0),
            'bridge_target_phase': ciel_result.get('bridge_target_phase', 0.0),
            'nonlocal_card_count': ciel_result.get('nonlocal_card_count', 0),
            'nonlocal_card_ids': ciel_result.get('nonlocal_card_ids', []),
            'phase_R_H': ciel_result.get('phase_R_H', 0.0),
            'collatz_seed': ciel_result.get('collatz_seed', 0),
            'lie4_trace': ciel_result.get('lie4_trace', 0.0),
        }
        control_view.update({
            'nonlocal_phi_ab_mean': ciel_result.get('phi_ab_mean', 0.0),
            'nonlocal_phi_berry_mean': ciel_result.get('phi_berry_mean', 0.0),
            'nonlocal_eba_defect_mean': ciel_result.get('eba_defect_mean', 0.0),
            'nonlocal_coherent_fraction': ciel_result.get('nonlocal_coherent_fraction', 0.0),
            'euler_bridge_closure_score': ciel_result.get('bridge_closure_score', 0.0),
            'euler_bridge_target_phase': ciel_result.get('bridge_target_phase', 0.0),
        })

        # --- Local Nonlocality Fallback ---
        # If canonical coherent_fraction is below threshold, run PC-state EBA
        # and merge the better observables into the pipeline result.
        canonical_cf = ciel_result.get('nonlocal_coherent_fraction', 0.0)
        try:
            from .local_nonlocality_fallback import (
                run_local_nonlocality_fallback,
                merge_with_canonical,
                save_report,
            )
            fallback_result = run_local_nonlocality_fallback(
                canonical_coherent_fraction=canonical_cf,
                root=root,
            )
            save_report(fallback_result, root=root)
            fallback_obs = fallback_result['observables']
            canonical_obs = {
                'nonlocal_coherent_fraction': canonical_cf,
                'eba_defect_mean': ciel_result.get('eba_defect_mean', 1.0),
                'phi_ab_mean': ciel_result.get('phi_ab_mean', 0.0),
                'phi_berry_mean': ciel_result.get('phi_berry_mean', 0.0),
            }
            merged = merge_with_canonical(canonical_obs, fallback_obs)
            # Update summary and control_view with merged observables
            summary['ciel_pipeline'].update({
                'nonlocal_coherent_fraction': merged['nonlocal_coherent_fraction'],
                'eba_defect_mean': merged['eba_defect_mean'],
                'phi_ab_mean': merged['phi_ab_mean'],
                'phi_berry_mean': merged['phi_berry_mean'],
                'local_nonlocality_fallback': {
                    'active': fallback_result.get('fallback_active', False),
                    'fallback_coherent_fraction': fallback_obs.get('nonlocal_coherent_fraction', 0.0),
                    'merged_coherent_fraction': merged['nonlocal_coherent_fraction'],
                },
            })
            control_view.update({
                'nonlocal_coherent_fraction': merged['nonlocal_coherent_fraction'],
                'nonlocal_eba_defect_mean': merged['eba_defect_mean'],
                'nonlocal_phi_ab_mean': merged['phi_ab_mean'],
                'nonlocal_phi_berry_mean': merged['phi_berry_mean'],
            })
        except Exception as fb_exc:
            _LOG.warning("Local nonlocality fallback unavailable: %s", fb_exc)

    except Exception as exc:
        _LOG.warning("CIEL/Ω pipeline unavailable: %s", exc)
        summary['ciel_pipeline'] = {'status': 'unavailable'}

    state_manifest = build_state_manifest(control_view)
    health_manifest = build_health_manifest(control_view)
    recommended_control = recommend_control(control_view)
    summary['state_manifest'] = state_manifest
    summary['health_manifest'] = health_manifest
    summary['recommended_control'] = recommended_control

    (bridge_dir / 'orbital_bridge_report.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    (bridge_dir / 'orbital_bridge_report.md').write_text(_bridge_markdown(summary), encoding='utf-8')
    (bridge_dir / 'orbital_state_manifest.json').write_text(json.dumps(state_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (bridge_dir / 'orbital_health_manifest.json').write_text(json.dumps(health_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (bridge_dir / 'subsystem_sync_manifest.json').write_text(json.dumps(sync_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (bridge_dir / 'runtime_gating.json').write_text(json.dumps(runtime_gating, ensure_ascii=False, indent=2), encoding='utf-8')

    # Mirror key reports to unified SQLite state store — single transaction
    try:
        from .state_db import save_bridge_snapshot
        ciel_pipe = summary.get('ciel_pipeline', {})
        save_bridge_snapshot(summary, runtime_gating, health_manifest, state_manifest, ciel_pipe)
    except Exception:
        pass  # SQLite write never blocks pipeline

    return summary


def main() -> int:
    root = resolve_project_root(Path(__file__))
    summary = build_orbital_bridge(root)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
