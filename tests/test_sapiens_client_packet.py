from src.ciel_sot_agent.sapiens_client import SapiensIdentity, SapiensSession, build_model_packet


def _session() -> SapiensSession:
    identity = SapiensIdentity(sapiens_id='test-sapiens')
    state_geometry = {
        'surface': {'mode': 'guided', 'recommended_action': 'guided interaction'},
        'internal_cymatics': {
            'coherence_index': 0.82,
            'closure_penalty': 0.11,
            'system_health': 0.91,
        },
        'spin': 0.24,
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


def test_build_model_packet_includes_surface_policy():
    session = _session()
    packet = build_model_packet(session, 'Test input')
    assert packet['schema'] == 'ciel-sot-agent/sapiens-client-packet/v0.2'
    assert 'surface_policy' in packet
    assert packet['surface_policy']['truth_over_smoothing'] is True
    assert packet['surface_policy']['explicit_uncertainty'] is True
    assert packet['surface_policy']['mode'] == 'guided'


def test_build_model_packet_extends_inference_contract():
    session = _session()
    packet = build_model_packet(session, 'Test input')
    contract = packet['inference_contract']
    assert contract['relation_before_identity'] is True
    assert contract['identity_before_memory'] is True
    assert contract['truth_axis'] == 'truth'
    assert contract['epistemic_separation'] == ['fact', 'inference', 'hypothesis', 'unknown']


def test_build_model_packet_appends_memory_excerpt():
    session = _session()
    packet = build_model_packet(session, 'Test input')
    assert packet['latest_user_turn'] == 'Test input'
    assert len(packet['memory_excerpt']) == 1
    turn = packet['memory_excerpt'][0]
    assert turn['role'] == 'sapiens'
    assert turn['content'] == 'Test input'
    assert turn['orbital_mode'] == 'guided'
