from __future__ import annotations

from src.ciel_sot_agent.gh_coupling import propagate_phase_changes
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
