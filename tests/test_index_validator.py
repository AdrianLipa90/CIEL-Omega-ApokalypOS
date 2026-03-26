from __future__ import annotations

from pathlib import Path

from src.ciel_sot_agent.index_validator import (
    DEMO_SHELL_MAP_OBJECT_ID,
    validate_demo_shell_map_data,
    validate_index_registry,
)


def _valid_map_object() -> dict[str, object]:
    return {
        'id': DEMO_SHELL_MAP_OBJECT_ID,
        'provenance': ['AdrianLipa90/ciel-omega-demo'],
        'provenance_type': 'imported',
        'tests': ['TST-SOT-0002'],
        'interfaces': ['IF-SOT-0001'],
    }


def _registry_ids() -> set[str]:
    return {
        DEMO_SHELL_MAP_OBJECT_ID,
        'DOC-SOT-0002',
        'REG-SOT-0003',
        'IF-SOT-0001',
        'TST-SOT-0002',
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


def test_demo_shell_map_validation_accepts_valid_contract() -> None:
    issues = validate_demo_shell_map_data(
        _valid_shell_map(),
        map_object=_valid_map_object(),
        registry_ids=_registry_ids(),
    )
    assert [issue for issue in issues if issue.level == 'error'] == []


def test_demo_shell_map_validation_flags_missing_self_binding_and_unknown_binding() -> None:
    invalid_map = _valid_shell_map()
    invalid_map['objects'][0]['sot_bindings'] = ['DOC-SOT-0002', 'UNKNOWN-SOT-9999']

    issues = validate_demo_shell_map_data(
        invalid_map,
        map_object=_valid_map_object(),
        registry_ids=_registry_ids(),
    )

    messages = [issue.message for issue in issues if issue.level == 'error']
    assert any('does not bind back to MAP-SOT-0001' in message for message in messages)
    assert any('unknown SOT binding: UNKNOWN-SOT-9999' in message for message in messages)


def test_current_repo_has_no_map_sot_errors() -> None:
    root = Path(__file__).resolve().parents[1]
    issues = validate_index_registry(root)
    map_errors = [issue for issue in issues if issue.object_id == DEMO_SHELL_MAP_OBJECT_ID and issue.level == 'error']
    assert map_errors == []
