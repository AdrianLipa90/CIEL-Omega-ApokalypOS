from pathlib import Path
import json

from src.ciel_sot_agent.sapiens_client import SapiensIdentity, SapiensSession, build_model_packet, persist_session


def _session() -> SapiensSession:
    identity = SapiensIdentity(sapiens_id='persist-test')
    state_geometry = {
        'surface': {'mode': 'guided', 'recommended_action': 'guided interaction'},
        'internal_cymatics': {
            'coherence_index': 0.77,
            'closure_penalty': 0.09,
            'system_health': 0.93,
        },
        'spin': 0.12,
        'axis': 'truth',
        'attractor': 'orbital-holonomic-stability',
    }
    control_profile = {'mode': 'guided', 'intensity': 'moderate'}
    return SapiensSession(
        identity=identity,
        created_at='2026-03-27T00:00:00+00:00',
        updated_at='2026-03-27T00:00:00+00:00',
        state_geometry=state_geometry,
        control_profile=control_profile,
        memory=[],
    )


def test_persist_session_writes_surface_policy_and_packet_artifacts(tmp_path: Path):
    session = _session()
    packet = build_model_packet(session, 'Persist this turn')
    paths = persist_session(tmp_path, session, packet)

    session_path = tmp_path / paths['session_json']
    packet_path = tmp_path / paths['latest_packet_json']
    policy_path = tmp_path / paths['surface_policy_json']
    transcript_path = tmp_path / paths['transcript_md']

    assert session_path.exists()
    assert packet_path.exists()
    assert policy_path.exists()
    assert transcript_path.exists()

    persisted_packet = json.loads(packet_path.read_text(encoding='utf-8'))
    persisted_policy = json.loads(policy_path.read_text(encoding='utf-8'))
    transcript = transcript_path.read_text(encoding='utf-8')

    assert persisted_packet['schema'] == 'ciel-sot-agent/sapiens-client-packet/v0.2'
    assert persisted_packet['surface_policy']['truth_over_smoothing'] is True
    assert persisted_policy['explicit_uncertainty'] is True
    assert persisted_policy['epistemic_separation'] == ['fact', 'inference', 'hypothesis', 'unknown']
    assert '# Sapiens Session Transcript' in transcript
    assert 'Persist this turn' in transcript
