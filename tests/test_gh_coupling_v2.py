from __future__ import annotations

from pathlib import Path

import json

from src.ciel_sot_agent.gh_coupling_v2 import _write_json_with_mirror, propagate_phase_changes, resolve_runtime_paths
from src.ciel_sot_agent.repo_phase import RepositoryState


def test_resolve_runtime_paths_prefers_v2_sectors(tmp_path: Path) -> None:
    (tmp_path / 'integration' / 'registries').mkdir(parents=True)
    (tmp_path / 'integration' / 'couplings').mkdir(parents=True)
    (tmp_path / 'integration' / 'upstreams').mkdir(parents=True)
    (tmp_path / 'integration' / 'reports').mkdir(parents=True)
    (tmp_path / 'integration').mkdir(exist_ok=True)

    (tmp_path / 'integration' / 'registries' / 'repository_registry.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'integration' / 'couplings' / 'repository_couplings.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'integration' / 'upstreams' / 'gh_upstreams.json').write_text('{"upstreams": []}', encoding='utf-8')
    (tmp_path / 'integration' / 'couplings' / 'gh_coupling_state.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'integration' / 'upstreams' / 'gh_live_registry.json').write_text('{}', encoding='utf-8')

    paths = resolve_runtime_paths(tmp_path)
    assert paths['registry'] == tmp_path / 'integration' / 'registries' / 'repository_registry.json'
    assert paths['couplings'] == tmp_path / 'integration' / 'couplings' / 'repository_couplings.json'
    assert paths['upstreams'] == tmp_path / 'integration' / 'upstreams' / 'gh_upstreams.json'
    assert paths['runtime_state'] == tmp_path / 'integration' / 'couplings' / 'gh_coupling_state.json'
    assert paths['live_registry'] == tmp_path / 'integration' / 'upstreams' / 'gh_live_registry.json'


def test_resolve_runtime_paths_falls_back_to_legacy(tmp_path: Path) -> None:
    (tmp_path / 'integration').mkdir(parents=True)
    (tmp_path / 'integration' / 'repository_registry.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'integration' / 'couplings.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'integration' / 'gh_upstreams.json').write_text('{"upstreams": []}', encoding='utf-8')
    (tmp_path / 'integration' / 'gh_coupling_state.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'integration' / 'gh_live_registry.json').write_text('{}', encoding='utf-8')

    paths = resolve_runtime_paths(tmp_path)
    assert paths['registry'] == tmp_path / 'integration' / 'repository_registry.json'
    assert paths['couplings'] == tmp_path / 'integration' / 'couplings.json'
    assert paths['upstreams'] == tmp_path / 'integration' / 'gh_upstreams.json'
    assert paths['runtime_state'] == tmp_path / 'integration' / 'gh_coupling_state.json'
    assert paths['live_registry'] == tmp_path / 'integration' / 'gh_live_registry.json'


def test_propagate_phase_changes_preserves_existing_behavior() -> None:
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


def test_write_json_with_mirror_keeps_legacy_and_v2_in_sync(tmp_path: Path) -> None:
    payload = {'schema': 'test', 'value': 1}
    primary = tmp_path / 'integration' / 'upstreams' / 'gh_live_registry.json'
    mirror = tmp_path / 'integration' / 'gh_live_registry.json'
    primary.parent.mkdir(parents=True)
    mirror.parent.mkdir(parents=True, exist_ok=True)

    _write_json_with_mirror(primary, payload, mirror_path=mirror)

    assert json.loads(primary.read_text(encoding='utf-8')) == payload
    assert json.loads(mirror.read_text(encoding='utf-8')) == payload
