"""Extended tests for sapiens panel sub-modules that have no existing coverage.

Covers:
  - sapiens_panel/support.py      (build_support_view)
  - sapiens_panel/render_schema.py (to_render_dict)
  - sapiens_panel/communication.py (build_communication_view)
  - sapiens_panel/reduction.py    (build_reduction_state)
"""
from __future__ import annotations

from src.ciel_sot_agent.sapiens_client import SapiensIdentity, SapiensSession
from src.ciel_sot_agent.sapiens_panel.communication import build_communication_view
from src.ciel_sot_agent.sapiens_panel.models import (
    PanelSessionSummary,
    PanelSettings,
    PanelState,
    PanelTabState,
)
from src.ciel_sot_agent.sapiens_panel.reduction import build_reduction_state
from src.ciel_sot_agent.sapiens_panel.render_schema import to_render_dict
from src.ciel_sot_agent.sapiens_panel.support import build_support_view


def _bridge_summary() -> dict:
    return {
        'schema': 'ciel-sot-agent/orbital-bridge-report/v0.2',
        'state_manifest': {
            'coherence_index': 0.75,
            'phase_alignment': 'moderate',
        },
        'health_manifest': {
            'closure_penalty': 0.12,
            'system_health': 0.88,
            'recommended_action': 'guided interaction',
        },
        'recommended_control': {
            'mode': 'guided',
            'intensity': 'moderate',
        },
        'source_paths': {
            'sectors': 'integration/Orbital/main/sectors.json',
        },
        'bridge_metrics': {
            'orbital_R_H': 0.91,
            'topological_charge_global': 0.03,
        },
    }


def _session() -> SapiensSession:
    identity = SapiensIdentity(sapiens_id='panel-test')
    state_geometry = {
        'surface': {'mode': 'guided', 'recommended_action': 'guided interaction'},
        'internal_cymatics': {
            'coherence_index': 0.75,
            'closure_penalty': 0.12,
            'system_health': 0.88,
        },
        'spin': 0.07,
        'axis': 'truth',
        'attractor': 'orbital-holonomic-stability',
    }
    return SapiensSession(
        identity=identity,
        created_at='2026-04-01T00:00:00+00:00',
        updated_at='2026-04-01T00:00:00+00:00',
        state_geometry=state_geometry,
        control_profile={'mode': 'guided'},
        memory=[],
    )


def test_build_support_view_contains_health_manifest() -> None:
    view = build_support_view(_bridge_summary())
    assert 'health_manifest' in view
    assert view['health_manifest']['system_health'] == 0.88


def test_build_support_view_contains_recommended_control() -> None:
    view = build_support_view(_bridge_summary())
    assert view['recommended_control']['mode'] == 'guided'


def test_build_support_view_contains_source_paths() -> None:
    view = build_support_view(_bridge_summary())
    assert 'source_paths' in view


def test_build_support_view_includes_artifact_paths_when_provided() -> None:
    paths = {'session_json': '/tmp/session.json'}
    view = build_support_view(_bridge_summary(), paths=paths)
    assert view['artifact_paths'] == paths


def test_build_support_view_artifact_paths_empty_when_not_provided() -> None:
    view = build_support_view(_bridge_summary())
    assert view['artifact_paths'] == {}


def test_build_support_view_includes_recommended_actions_list() -> None:
    view = build_support_view(_bridge_summary())
    assert isinstance(view['recommended_actions'], list)
    assert len(view['recommended_actions']) > 0


def _panel_state() -> PanelState:
    tab = PanelTabState(title='Control', summary={'key': 'value'}, actions=['Act'])
    session_summary = PanelSessionSummary(
        sapiens_id='tester',
        relation_label='human-model',
        preferred_mode='guided',
        created_at='2026-04-01T00:00:00+00:00',
        updated_at='2026-04-01T00:00:00+00:00',
        turn_count=0,
    )
    return PanelState(
        control=tab,
        settings=PanelTabState(title='Settings'),
        communication=PanelTabState(title='Communication'),
        support=PanelTabState(title='Support'),
        session=session_summary,
    )


def test_to_render_dict_returns_dict() -> None:
    result = to_render_dict(_panel_state())
    assert isinstance(result, dict)


def test_to_render_dict_contains_all_tabs() -> None:
    result = to_render_dict(_panel_state())
    for key in ('control', 'settings', 'communication', 'support'):
        assert key in result


def test_to_render_dict_control_title_preserved() -> None:
    result = to_render_dict(_panel_state())
    assert result['control']['title'] == 'Control'


def test_to_render_dict_session_fields_present() -> None:
    result = to_render_dict(_panel_state())
    assert result['session']['sapiens_id'] == 'tester'
    assert result['session']['turn_count'] == 0


def test_build_communication_view_returns_packet() -> None:
    session = _session()
    view = build_communication_view(session, 'Hello from test')
    assert 'packet' in view
    assert view['packet']['schema'] == 'ciel-sot-agent/sapiens-client-packet/v0.3'


def test_build_communication_view_latest_user_turn() -> None:
    session = _session()
    view = build_communication_view(session, 'My message')
    assert view['latest_user_turn'] == 'My message'


def test_build_communication_view_memory_excerpt_present() -> None:
    session = _session()
    view = build_communication_view(session, 'Turn one')
    assert isinstance(view['memory_excerpt'], list)
    assert len(view['memory_excerpt']) >= 1


def test_build_communication_view_turn_count_is_positive() -> None:
    session = _session()
    view = build_communication_view(session, 'A turn')
    assert view['turn_count'] >= 1


def test_build_reduction_state_returns_schema() -> None:
    session = _session()
    from src.ciel_sot_agent.sapiens_client import build_model_packet
    packet = build_model_packet(session, 'test')
    result = build_reduction_state(_bridge_summary(), session, packet)
    assert result['schema'] == 'ciel-sot-agent/sapiens-reduction-state/v0.1'


def test_build_reduction_state_readiness_score_in_unit_interval() -> None:
    session = _session()
    from src.ciel_sot_agent.sapiens_client import build_model_packet
    packet = build_model_packet(session, 'test')
    result = build_reduction_state(_bridge_summary(), session, packet)
    score = result['reduction_state']['readiness_score']
    assert 0.0 <= score <= 1.0


def test_build_reduction_state_reduction_ready_is_bool() -> None:
    session = _session()
    from src.ciel_sot_agent.sapiens_client import build_model_packet
    packet = build_model_packet(session, 'test')
    result = build_reduction_state(_bridge_summary(), session, packet)
    assert isinstance(result['reduction_state']['reduction_ready'], bool)


def test_build_reduction_state_memory_residue_has_identity_anchor() -> None:
    session = _session()
    from src.ciel_sot_agent.sapiens_client import build_model_packet
    packet = build_model_packet(session, 'test')
    result = build_reduction_state(_bridge_summary(), session, packet)
    anchor = result['memory_residue']['identity_anchor']
    assert anchor['sapiens_id'] == 'panel-test'
    assert anchor['truth_axis'] == 'truth'


def test_build_reduction_state_uses_custom_threshold() -> None:
    session = _session()
    from src.ciel_sot_agent.sapiens_client import build_model_packet
    packet = build_model_packet(session, 'test')
    result = build_reduction_state(
        _bridge_summary(), session, packet,
        settings={'reduction_policy': {'readiness_threshold': 0.99}},
    )
    assert result['reduction_state']['readiness_threshold'] == 0.99


def test_build_reduction_state_orchestration_state_present() -> None:
    session = _session()
    from src.ciel_sot_agent.sapiens_client import build_model_packet
    packet = build_model_packet(session, 'test')
    result = build_reduction_state(_bridge_summary(), session, packet)
    orch = result['orchestration_state']
    assert 'orbital_mode' in orch
    assert 'coherence_index' in orch
    assert 'system_health' in orch
