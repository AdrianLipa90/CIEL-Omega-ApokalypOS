from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from src.ciel_sot_agent.gh_coupling import (
    load_runtime_state,
    load_upstreams,
    propagate_phase_changes,
    wrap_angle,
)
from src.ciel_sot_agent.repo_phase import RepositoryState


def test_changed_source_moves_itself_and_target() -> None:
    states = {
        'a': RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'role', 'upstream'),
        'b': RepositoryState('b', 'B', 0.6, 0.5, 1.0, 'role', 'upstream'),
    }
    couplings = {'a': {'b': 1.0}, 'b': {'a': 1.0}}
    new_states, events = propagate_phase_changes(states, couplings, ['a'], intrinsic_jump=0.2, beta=0.35)
    assert new_states['a'].phi != states['a'].phi
    assert new_states['b'].phi != states['b'].phi
    assert any(e['kind'] == 'intrinsic' for e in events)
    assert any(e['kind'] == 'coupled' for e in events)


def test_no_changes_means_no_events() -> None:
    states = {
        'a': RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'role', 'upstream'),
        'b': RepositoryState('b', 'B', 0.6, 0.5, 1.0, 'role', 'upstream'),
    }
    couplings = {'a': {'b': 1.0}, 'b': {'a': 1.0}}
    new_states, events = propagate_phase_changes(states, couplings, [])
    assert new_states == states
    assert events == []


# ---------------------------------------------------------------------------
# wrap_angle
# ---------------------------------------------------------------------------

def test_wrap_angle_large_positive() -> None:
    value = wrap_angle(4.0)
    assert -math.pi < value <= math.pi


def test_wrap_angle_large_negative() -> None:
    value = wrap_angle(-10.0)
    assert -math.pi < value <= math.pi


def test_wrap_angle_pi_unchanged() -> None:
    assert wrap_angle(math.pi) == pytest.approx(math.pi)


def test_wrap_angle_zero_unchanged() -> None:
    assert wrap_angle(0.0) == 0.0


def test_wrap_angle_two_pi_near_zero() -> None:
    value = wrap_angle(2 * math.pi)
    assert -math.pi < value <= math.pi


# ---------------------------------------------------------------------------
# load_upstreams
# ---------------------------------------------------------------------------

def test_load_upstreams_parses_fields(tmp_path: Path) -> None:
    data = {
        'upstreams': [
            {
                'key': 'u1',
                'repo_full_name': 'org/repo',
                'branch': 'main',
                'enabled': True,
                'source_weight': 1.5,
                'notes': 'primary upstream',
            }
        ]
    }
    path = tmp_path / 'upstreams.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    upstreams = load_upstreams(path)
    assert len(upstreams) == 1
    u = upstreams[0]
    assert u.key == 'u1'
    assert u.repo_full_name == 'org/repo'
    assert u.branch == 'main'
    assert u.enabled is True
    assert u.source_weight == pytest.approx(1.5)
    assert u.notes == 'primary upstream'


def test_load_upstreams_null_repo_full_name(tmp_path: Path) -> None:
    data = {
        'upstreams': [
            {'key': 'u2', 'repo_full_name': None, 'branch': 'dev', 'enabled': False, 'source_weight': 1.0, 'notes': ''}
        ]
    }
    path = tmp_path / 'u.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    upstreams = load_upstreams(path)
    assert upstreams[0].repo_full_name is None


def test_load_upstreams_empty(tmp_path: Path) -> None:
    path = tmp_path / 'u.json'
    path.write_text('{"upstreams": []}', encoding='utf-8')
    assert load_upstreams(path) == []


# ---------------------------------------------------------------------------
# load_runtime_state
# ---------------------------------------------------------------------------

def test_load_runtime_state_missing_file_returns_defaults(tmp_path: Path) -> None:
    state = load_runtime_state(tmp_path / 'nonexistent.json')
    assert state == {'heads': {}, 'last_generated_at': None}


def test_load_runtime_state_existing_file(tmp_path: Path) -> None:
    data = {'heads': {'a': {'sha': 'abc123'}}, 'last_generated_at': '2026-01-01T00:00:00+00:00'}
    path = tmp_path / 'state.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    state = load_runtime_state(path)
    assert state['heads']['a']['sha'] == 'abc123'
    assert state['last_generated_at'] == '2026-01-01T00:00:00+00:00'


# ---------------------------------------------------------------------------
# propagate_phase_changes — source_weights & edge cases
# ---------------------------------------------------------------------------

def test_propagate_phase_changes_source_weights_scale_jump() -> None:
    states = {
        'a': RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'role', 'upstream'),
    }
    couplings: dict = {}
    # weight=2.0 → jump=0.2*2=0.4
    new_states, events = propagate_phase_changes(states, couplings, ['a'], intrinsic_jump=0.2, source_weights={'a': 2.0})
    expected_phi = wrap_angle(0.0 + 0.2 * 2.0)
    assert new_states['a'].phi == pytest.approx(expected_phi)
    assert events[0]['delta_phi'] == pytest.approx(0.4)


def test_propagate_phase_changes_skips_unknown_key() -> None:
    states = {'a': RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'role', 'upstream')}
    new_states, events = propagate_phase_changes(states, {}, ['z'])
    # 'z' not in states — nothing should change
    assert new_states == states
    assert events == []


def test_propagate_phase_changes_no_coupling_event_when_coupling_is_zero() -> None:
    # When coupling == 0, delta = 0 → no coupled event emitted
    states = {
        'a': RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'role', 'upstream'),
        'b': RepositoryState('b', 'B', 1.0, 0.5, 1.0, 'role', 'upstream'),
    }
    couplings = {'a': {'b': 0.0}}
    new_states, events = propagate_phase_changes(states, couplings, ['a'])
    coupled = [e for e in events if e['kind'] == 'coupled']
    assert coupled == []
