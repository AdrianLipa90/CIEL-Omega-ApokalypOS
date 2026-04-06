from __future__ import annotations

from pathlib import Path

import pytest

from src.ciel_sot_agent.sapiens_client import (
    EPISTEMIC_SEPARATION,
    SapiensIdentity,
    SapiensSession,
    append_turn,
    build_model_packet,
    initialize_session,
    run_sapiens_client,
)


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


# ---------------------------------------------------------------------------
# SapiensIdentity defaults
# ---------------------------------------------------------------------------

def test_sapiens_identity_defaults() -> None:
    identity = SapiensIdentity()
    assert identity.sapiens_id == 'sapiens'
    assert identity.relation_label == 'human-model'
    assert identity.preferred_mode == 'guided'
    assert identity.truth_axis == 'truth'
    assert identity.memory_policy == 'session-first'


def test_sapiens_identity_custom_fields() -> None:
    identity = SapiensIdentity(sapiens_id='alice', relation_label='researcher-model', preferred_mode='deep')
    assert identity.sapiens_id == 'alice'
    assert identity.relation_label == 'researcher-model'
    assert identity.preferred_mode == 'deep'


# ---------------------------------------------------------------------------
# EPISTEMIC_SEPARATION constant
# ---------------------------------------------------------------------------

def test_epistemic_separation_constant_has_four_layers() -> None:
    assert EPISTEMIC_SEPARATION == ['fact', 'inference', 'hypothesis', 'unknown']


# ---------------------------------------------------------------------------
# append_turn
# ---------------------------------------------------------------------------

def test_append_turn_adds_turn_to_memory() -> None:
    session = _session()
    initial_count = len(session.memory)
    session = append_turn(session, 'user', 'Hello there')
    assert len(session.memory) == initial_count + 1
    last = session.memory[-1]
    assert last.role == 'user'
    assert last.content == 'Hello there'


def test_append_turn_records_orbital_mode() -> None:
    session = _session()
    append_turn(session, 'sapiens', 'Response text')
    assert session.memory[-1].orbital_mode == 'guided'


def test_append_turn_updates_updated_at() -> None:
    session = _session()
    append_turn(session, 'user', 'ping')
    # updated_at is a non-empty ISO timestamp string
    assert session.updated_at
    assert isinstance(session.updated_at, str)


def test_append_turn_multiple_turns() -> None:
    session = _session()
    append_turn(session, 'user', 'First')
    append_turn(session, 'sapiens', 'Second')
    append_turn(session, 'user', 'Third')
    assert len(session.memory) == 3
    assert [t.role for t in session.memory] == ['user', 'sapiens', 'user']


# ---------------------------------------------------------------------------
# initialize_session
# ---------------------------------------------------------------------------

def test_initialize_session_returns_session_with_geometry() -> None:
    root = Path(__file__).resolve().parents[1]
    session = initialize_session(root)
    assert 'internal_cymatics' in session.state_geometry
    assert 'surface' in session.state_geometry


def test_initialize_session_memory_is_empty() -> None:
    root = Path(__file__).resolve().parents[1]
    session = initialize_session(root)
    assert session.memory == []


def test_initialize_session_uses_provided_identity() -> None:
    root = Path(__file__).resolve().parents[1]
    identity = SapiensIdentity(sapiens_id='custom-id')
    session = initialize_session(root, identity=identity)
    assert session.identity.sapiens_id == 'custom-id'


def test_initialize_session_default_identity() -> None:
    root = Path(__file__).resolve().parents[1]
    session = initialize_session(root)
    assert session.identity.sapiens_id == 'sapiens'


# ---------------------------------------------------------------------------
# run_sapiens_client
# ---------------------------------------------------------------------------

def test_run_sapiens_client_returns_v2_schema() -> None:
    root = Path(__file__).resolve().parents[1]
    result = run_sapiens_client(root, 'Hello, CIEL.')
    assert result['schema'] == 'ciel-sot-agent/sapiens-client-run/v0.2'


def test_run_sapiens_client_contains_packet_and_paths() -> None:
    root = Path(__file__).resolve().parents[1]
    result = run_sapiens_client(root, 'Test run')
    assert 'packet' in result
    assert 'paths' in result


def test_run_sapiens_client_packet_has_surface_policy() -> None:
    root = Path(__file__).resolve().parents[1]
    result = run_sapiens_client(root, 'Surface policy check')
    packet = result['packet']
    assert packet['surface_policy']['truth_over_smoothing'] is True


def test_run_sapiens_client_custom_sapiens_id() -> None:
    root = Path(__file__).resolve().parents[1]
    result = run_sapiens_client(root, 'Custom ID test', sapiens_id='bob')
    assert result['packet']['identity']['sapiens_id'] == 'bob'
