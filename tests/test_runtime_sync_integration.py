from __future__ import annotations

import json
from pathlib import Path

from src.ciel_sot_agent.orbital_bridge import _build_runtime_gating, _build_sync_manifest
from src.ciel_sot_agent.sapiens_client import SapiensIdentity, SapiensSession, _surface_policy, build_model_packet


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def test_runtime_sync_manifest_loads_registry_and_policy(tmp_path: Path) -> None:
    defs_dir = tmp_path / 'integration' / 'registries' / 'definitions'
    _write_json(defs_dir / 'subsystem_sync_registry.json', {
        'schema': 'ciel/subsystem-sync-registry/v0.1',
        'count': 1,
        'records': [{
            'board_card_id': 'file:src/example.py',
            'tau_orbit': 'tau-orbit:file:src/example.py',
            'tau_system': 'tau-system:GLOBAL_ATTRACTOR',
            'member_count': 2,
            'board_export_result': 'BOARD<DYNAMIC>',
            'aggregation_model': 'BOARD_METRONOME_COUPLING',
        }],
    })
    _write_json(defs_dir / 'subsystem_sync_report.json', {
        'schema': 'ciel/subsystem-sync-report/v0.1',
        'board_count': 1,
        'avg_members_per_board': 2.0,
        'tau_orbit_count': 1,
        'tau_system_count': 1,
        'sync_law_counts': {'sync-law:METRONOME_BOARD_COUPLING': 1},
        'condensation_operator_counts': {'CONDENSE_HALF_CONCLUSIONS': 1},
        'sync_scope_counts': {'BOARD_ROOT': 1, 'BOARD_MEMBER': 2},
    })
    _write_json(defs_dir / 'orbital_assignment_report.json', {
        'privacy_constraint_counts': {'BROKER_GATED_DISCLOSURE': 2},
        'horizon_class_counts': {'TRANSMISSIVE': 2},
    })
    _write_json(defs_dir / 'horizon_policy_matrix.json', {
        'schema': 'ciel/horizon-policy-matrix/v0.1',
        'classes': {
            'TRANSMISSIVE': {
                'privacy_constraint': 'BROKER_GATED_DISCLOSURE',
                'leak_channel_mode': 'HAWKING_EULER_BROKERED',
                'leak_budget_class': 'BROKERED_LEAK_BUDGET',
                'exportable_fields': ['export_state', 'export_result'],
            }
        },
    })

    manifest = _build_sync_manifest(tmp_path)
    assert manifest['board_count'] == 1
    assert manifest['tau_orbit_count'] == 1
    assert manifest['tau_system_count'] == 1
    assert manifest['privacy_constraint_counts']['BROKER_GATED_DISCLOSURE'] == 2
    assert manifest['export_boundary_policy']['TRANSMISSIVE']['leak_channel_mode'] == 'HAWKING_EULER_BROKERED'

    gating = _build_runtime_gating(manifest)
    assert gating['export_boundary_mode'] == 'PROJECTED_ONLY'
    assert gating['private_state_export_allowed'] is False
    assert gating['board_sync_ready'] is True
    assert gating['system_tau_coherent'] is True


def test_sapiens_packet_carries_runtime_gating_and_sync_manifest() -> None:
    session = SapiensSession(
        identity=SapiensIdentity(),
        created_at='2026-04-07T00:00:00+00:00',
        updated_at='2026-04-07T00:00:00+00:00',
        state_geometry={
            'surface': {'mode': 'guided', 'export_boundary_mode': 'PROJECTED_ONLY'},
            'internal_cymatics': {'coherence_index': 0.9, 'closure_penalty': 0.1, 'system_health': 0.8, 'board_count': 2, 'tau_system_count': 1},
            'spin': 0.5,
            'axis': 'truth',
            'attractor': 'orbital-holonomic-stability',
        },
        control_profile={'mode': 'guided'},
        bridge_runtime={
            'runtime_gating': {
                'export_boundary_mode': 'PROJECTED_ONLY',
                'private_state_export_allowed': False,
                'requires_projection_operator': True,
            },
            'subsystem_sync_manifest': {
                'board_count': 2,
                'tau_system_count': 1,
                'sync_law_counts': {'sync-law:METRONOME_BOARD_COUPLING': 2},
            },
        },
        memory=[],
    )

    surface_policy = _surface_policy(session)
    assert surface_policy['private_state_export_allowed'] is False
    assert surface_policy['requires_projection_operator'] is True

    packet = build_model_packet(session, 'test message')
    assert packet['runtime_gating']['export_boundary_mode'] == 'PROJECTED_ONLY'
    assert packet['subsystem_sync_manifest']['board_count'] == 2
    assert packet['inference_contract']['projection_required'] is True
    assert packet['inference_contract']['private_state_export_allowed'] is False
    assert packet['inference_contract']['sync_law_counts']['sync-law:METRONOME_BOARD_COUPLING'] == 2
