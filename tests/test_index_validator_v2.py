from __future__ import annotations

from pathlib import Path

from src.ciel_sot_agent.index_validator_v2 import (
    DEMO_SHELL_INVENTORY_PATH,
    DEMO_SHELL_MAP_OBJECT_ID,
    DEMO_SHELL_MAP_V2_OBJECT_ID,
    resolve_index_registry_path,
    validate_demo_shell_inventory_data,
    validate_demo_shell_map_data,
    validate_index_registry,
)


def _valid_map_object() -> dict[str, object]:
    return {
        'id': DEMO_SHELL_MAP_OBJECT_ID,
        'path': 'integration/upstreams/ciel_omega_demo_shell_map.json',
        'provenance': ['AdrianLipa90/ciel-omega-demo'],
        'provenance_type': 'imported',
        'tests': ['TST-SOT-0002'],
        'interfaces': ['IF-SOT-0001'],
    }


def _valid_v2_map_object() -> dict[str, object]:
    return {
        'id': DEMO_SHELL_MAP_V2_OBJECT_ID,
        'path': 'integration/upstreams/ciel_omega_demo_shell_map.json',
        'provenance': ['AdrianLipa90/ciel-omega-demo'],
        'provenance_type': 'imported',
        'tests': ['TST-SOT-0002'],
        'interfaces': ['IF-SOT-0001'],
    }


def _registry_ids() -> set[str]:
    return {
        DEMO_SHELL_MAP_OBJECT_ID,
        DEMO_SHELL_MAP_V2_OBJECT_ID,
        'DOC-SOT-0002',
        'REG-SOT-0003',
        'IF-SOT-0001',
        'TST-SOT-0002',
    }


def _valid_inventory() -> dict[str, object]:
    return {
        'schema': 'ciel-sot-agent/upstream-inventory/v0.1',
        'upstream_repo': 'AdrianLipa90/ciel-omega-demo',
        'ref': 'main',
        'ref_sha': '22379536c00d46cf26955ab1c620b521e8a0f5bc',
        'paths': [
            'AGENT.md',
            'docs/orbital_manifest.json',
            'main/apps/omega_app.py',
        ],
    }


def _valid_shell_map() -> dict[str, object]:
    return {
        'schema': 'ciel-sot-agent/demo-shell-map/v0.1',
        'upstream_repo': 'AdrianLipa90/ciel-omega-demo',
        'ref': 'main',
        'role': 'core-shell-cockpit-publication-surface',
        'objects': [
            {
                'id': 'IMP-DEMO-0001',
                'name': 'demo_agent_protocol',
                'kind': 'protocol',
                'upstream_path': 'AGENT.md',
                'status': 'canonical',
                'integration_role': 'shell-governance',
                'sot_bindings': ['DOC-SOT-0002', DEMO_SHELL_MAP_OBJECT_ID],
            },
            {
                'id': 'IMP-DEMO-0002',
                'name': 'demo_orbital_manifest',
                'kind': 'manifest',
                'upstream_path': 'docs/orbital_manifest.json',
                'status': 'canonical',
                'integration_role': 'shell-runtime-state',
                'sot_bindings': ['REG-SOT-0003', DEMO_SHELL_MAP_OBJECT_ID],
            },
        ],
    }


def test_resolve_index_registry_path_prefers_v2(tmp_path: Path) -> None:
    (tmp_path / 'integration' / 'registries').mkdir(parents=True)
    (tmp_path / 'integration').mkdir(exist_ok=True)
    v2 = tmp_path / 'integration' / 'registries' / 'index_registry_v2.yaml'
    legacy = tmp_path / 'integration' / 'index_registry.yaml'
    v2.write_text('schema: test-v2\n', encoding='utf-8')
    legacy.write_text('schema: test-legacy\n', encoding='utf-8')
    assert resolve_index_registry_path(tmp_path) == v2


def test_demo_shell_inventory_validation_accepts_valid_inventory() -> None:
    issues, paths = validate_demo_shell_inventory_data(
        _valid_inventory(),
        expected_upstream_repo='AdrianLipa90/ciel-omega-demo',
    )
    assert [issue for issue in issues if issue.level == 'error'] == []
    assert 'AGENT.md' in paths


def test_demo_shell_map_validation_accepts_valid_contract() -> None:
    inventory_issues, known_paths = validate_demo_shell_inventory_data(
        _valid_inventory(),
        expected_upstream_repo='AdrianLipa90/ciel-omega-demo',
    )
    assert [issue for issue in inventory_issues if issue.level == 'error'] == []

    issues = validate_demo_shell_map_data(
        _valid_shell_map(),
        map_object=_valid_map_object(),
        registry_ids=_registry_ids(),
        known_upstream_paths=known_paths,
    )
    assert [issue for issue in issues if issue.level == 'error'] == []


def test_demo_shell_map_validation_accepts_legacy_binding_under_v2_object_id() -> None:
    inventory_issues, known_paths = validate_demo_shell_inventory_data(
        _valid_inventory(),
        expected_upstream_repo='AdrianLipa90/ciel-omega-demo',
    )
    assert [issue for issue in inventory_issues if issue.level == 'error'] == []

    issues = validate_demo_shell_map_data(
        _valid_shell_map(),
        map_object=_valid_v2_map_object(),
        registry_ids=_registry_ids(),
        known_upstream_paths=known_paths,
    )
    assert [issue for issue in issues if issue.level == 'error'] == []


def test_demo_shell_map_validation_flags_unknown_binding_and_unknown_upstream_path() -> None:
    inventory_issues, known_paths = validate_demo_shell_inventory_data(
        _valid_inventory(),
        expected_upstream_repo='AdrianLipa90/ciel-omega-demo',
    )
    assert [issue for issue in inventory_issues if issue.level == 'error'] == []

    invalid_map = _valid_shell_map()
    invalid_map['objects'][0]['sot_bindings'] = ['DOC-SOT-0002', 'UNKNOWN-SOT-9999']
    invalid_map['objects'][0]['upstream_path'] = 'missing/file.py'

    issues = validate_demo_shell_map_data(
        invalid_map,
        map_object=_valid_map_object(),
        registry_ids=_registry_ids(),
        known_upstream_paths=known_paths,
    )

    messages = [issue.message for issue in issues if issue.level == 'error']
    assert any('unknown SOT binding: UNKNOWN-SOT-9999' in message for message in messages)
    assert any('references unknown upstream_path: missing/file.py' in message for message in messages)


def test_current_repo_has_no_demo_shell_or_inventory_errors_under_v2_validator() -> None:
    root = Path(__file__).resolve().parents[1]
    issues = validate_index_registry(root)
    target_errors = [
        issue for issue in issues
        if issue.object_id in {DEMO_SHELL_MAP_OBJECT_ID, DEMO_SHELL_MAP_V2_OBJECT_ID} and issue.level == 'error'
    ]
    assert target_errors == []
    assert (root / DEMO_SHELL_INVENTORY_PATH).exists()
