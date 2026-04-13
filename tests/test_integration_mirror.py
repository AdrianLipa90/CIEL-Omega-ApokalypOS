from __future__ import annotations

import json
from pathlib import Path

from src.ciel_sot_agent.integration_mirror import _merge_values, sync_integration_mirrors


def test_merge_values_merges_dicts_and_prefers_nonempty_target_values() -> None:
    left = {'a': 1, 'nested': {'x': 1}, 'list': [{'k': 1}], 'empty': 'legacy'}
    right = {'b': 2, 'nested': {'y': 2}, 'list': [{'k': 1}, {'k': 2}], 'empty': ''}
    merged = _merge_values(left, right)

    assert merged['a'] == 1
    assert merged['b'] == 2
    assert merged['nested'] == {'x': 1, 'y': 2}
    assert merged['list'] == [{'k': 1}, {'k': 2}]
    assert merged['empty'] == 'legacy'


def test_merge_values_merges_dict_list_by_id_without_duplicate_entries() -> None:
    left = [{'id': 'A', 'value': 1}, {'id': 'B', 'value': 2}]
    right = [{'id': 'A', 'status': 'canonical-v2'}, {'id': 'C', 'value': 3}]

    merged = _merge_values(left, right)

    assert len(merged) == 3
    by_id = {item['id']: item for item in merged}
    assert by_id['A'] == {'id': 'A', 'value': 1, 'status': 'canonical-v2'}
    assert by_id['B'] == {'id': 'B', 'value': 2}
    assert by_id['C'] == {'id': 'C', 'value': 3}


def test_sync_integration_mirrors_merges_pair_and_writes_both_files(tmp_path: Path) -> None:
    legacy = tmp_path / 'integration' / 'repository_registry.json'
    target = tmp_path / 'integration' / 'registries' / 'repository_registry.json'
    legacy.parent.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    legacy.write_text(json.dumps({'repositories': [{'key': 'agent'}]}), encoding='utf-8')
    target.write_text(json.dumps({'repositories': [{'key': 'demo'}]}), encoding='utf-8')

    # seed remaining mapped pairs as already-synced minimal objects
    mapped_pairs = [
        ('integration/couplings.json', 'integration/couplings/repository_couplings.json'),
        ('integration/hyperspace_index.json', 'integration/indices/hyperspace_index.json'),
        ('integration/index_registry.yaml', 'integration/registries/index_registry.yaml'),
        ('integration/gh_upstreams.json', 'integration/upstreams/gh_upstreams.json'),
        ('integration/gh_live_registry.json', 'integration/upstreams/gh_live_registry.json'),
        ('integration/gh_coupling_state.json', 'integration/couplings/gh_coupling_state.json'),
        ('integration/hyperspace_index_orbital.json', 'integration/indices/hyperspace_index_orbital.json'),
        ('integration/index_registry_orbital.yaml', 'integration/registries/index_registry_orbital.yaml'),
    ]
    for left_rel, right_rel in mapped_pairs:
        left = tmp_path / left_rel
        right = tmp_path / right_rel
        left.parent.mkdir(parents=True, exist_ok=True)
        right.parent.mkdir(parents=True, exist_ok=True)
        if left.suffix == '.json':
            payload = {'schema': 'test'}
            left.write_text(json.dumps(payload), encoding='utf-8')
            right.write_text(json.dumps(payload), encoding='utf-8')
        else:
            payload = 'schema: test\n'
            left.write_text(payload, encoding='utf-8')
            right.write_text(payload, encoding='utf-8')

    results = sync_integration_mirrors(tmp_path)

    merged = json.loads(legacy.read_text(encoding='utf-8'))
    mirrored = json.loads(target.read_text(encoding='utf-8'))
    assert merged == mirrored
    assert merged['repositories'] == [{'key': 'agent'}, {'key': 'demo'}]
    assert any(result.updated for result in results)
