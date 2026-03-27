from __future__ import annotations

from pathlib import Path

from src.ciel_sot_agent.synchronize_v2 import build_sync_report_v2, resolve_sync_paths


def test_resolve_sync_paths_prefers_v2(tmp_path: Path) -> None:
    (tmp_path / 'integration' / 'registries').mkdir(parents=True)
    (tmp_path / 'integration' / 'couplings').mkdir(parents=True)
    (tmp_path / 'integration' / 'registries' / 'repository_registry.json').write_text(
        '{"repositories": []}', encoding='utf-8'
    )
    (tmp_path / 'integration' / 'couplings' / 'repository_couplings.json').write_text(
        '{"couplings": {}}', encoding='utf-8'
    )

    paths = resolve_sync_paths(tmp_path)
    assert paths['registry'] == tmp_path / 'integration' / 'registries' / 'repository_registry.json'
    assert paths['couplings'] == tmp_path / 'integration' / 'couplings' / 'repository_couplings.json'


def test_resolve_sync_paths_falls_back_to_legacy(tmp_path: Path) -> None:
    (tmp_path / 'integration').mkdir(parents=True)
    (tmp_path / 'integration' / 'repository_registry.json').write_text(
        '{"repositories": []}', encoding='utf-8'
    )
    (tmp_path / 'integration' / 'couplings.json').write_text(
        '{"couplings": {}}', encoding='utf-8'
    )

    paths = resolve_sync_paths(tmp_path)
    assert paths['registry'] == tmp_path / 'integration' / 'repository_registry.json'
    assert paths['couplings'] == tmp_path / 'integration' / 'couplings.json'


def test_build_sync_report_v2_includes_path_resolution(tmp_path: Path) -> None:
    (tmp_path / 'integration' / 'registries').mkdir(parents=True)
    (tmp_path / 'integration' / 'couplings').mkdir(parents=True)
    (tmp_path / 'integration' / 'registries' / 'repository_registry.json').write_text(
        '{"repositories": [{"key": "a", "identity": "A", "phi": 0.0, "spin": 0.5, "mass": 1.0, "role": "role", "upstream": "upstream"}]}' ,
        encoding='utf-8'
    )
    (tmp_path / 'integration' / 'couplings' / 'repository_couplings.json').write_text(
        '{"couplings": {"a": {}}}', encoding='utf-8'
    )

    payload = build_sync_report_v2(tmp_path)
    assert payload['schema'] == 'ciel-sot-agent/sync-report/v0.2'
    assert payload['path_resolution']['registry'] == 'integration/registries/repository_registry.json'
    assert payload['path_resolution']['couplings'] == 'integration/couplings/repository_couplings.json'
    assert payload['report']['repository_count'] == 1
