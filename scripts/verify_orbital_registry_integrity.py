#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFINITIONS_DIR = Path('integration') / 'registries' / 'definitions'
BRIDGE_DIR = Path('integration') / 'reports' / 'orbital_bridge'
SAPIENS_DIR = Path('integration') / 'reports' / 'sapiens_client'

EXPORT_FORBIDDEN_FIELDS = {
    'internal_candidate_states',
    'internal_conflict_state',
    'internal_superposition_state',
    'internal_resolution_trace',
    'internal_tau_local',
    'internal_tau_orbit',
    'internal_tau_system',
    'internal_memory_mode',
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _append_issue(issues: list[str], condition: bool, message: str) -> None:
    if not condition:
        issues.append(message)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    defs = root / DEFINITIONS_DIR
    bridge = root / BRIDGE_DIR
    sapiens = root / SAPIENS_DIR

    export_payload = _load_json(defs / 'orbital_definition_registry.json')
    internal_payload = _load_json(defs / 'internal_subsystem_cards.json')
    horizon_policy = _load_json(defs / 'horizon_policy_matrix.json')
    sync_registry = _load_json(defs / 'subsystem_sync_registry.json')
    sync_report = _load_json(defs / 'subsystem_sync_report.json')
    db_manifest = _load_json(defs / 'db_library' / 'manifest.json')

    bridge_report = _load_json(bridge / 'orbital_bridge_report.json') if (bridge / 'orbital_bridge_report.json').exists() else {}
    runtime_gating = _load_json(bridge / 'runtime_gating.json') if (bridge / 'runtime_gating.json').exists() else {}
    sapiens_packet = _load_json(sapiens / 'latest_packet.json') if (sapiens / 'latest_packet.json').exists() else {}

    export_records = export_payload.get('records', [])
    internal_cards = internal_payload.get('internal_cards', [])
    export_ids = {rec['id'] for rec in export_records}
    board_ids = {rec.get('board_card_id') for rec in export_records if rec.get('board_card_id')}
    internal_by_export = {rec.get('export_card_id'): rec for rec in internal_cards if rec.get('export_card_id')}

    issues: list[str] = []

    _append_issue(issues, export_payload.get('schema') == 'ciel/orbital-definition-registry-enriched/v0.5', 'unexpected export registry schema')
    _append_issue(issues, internal_payload.get('schema') == 'ciel/internal-subsystem-card-registry/v0.3', 'unexpected internal registry schema')
    _append_issue(issues, horizon_policy.get('schema') == 'ciel/horizon-policy-matrix/v0.1', 'unexpected horizon policy schema')
    _append_issue(issues, sync_registry.get('schema') == 'ciel/subsystem-sync-registry/v0.1', 'unexpected subsystem sync schema')
    _append_issue(issues, sync_report.get('schema') == 'ciel/subsystem-sync-report/v0.1', 'unexpected subsystem sync report schema')
    _append_issue(issues, db_manifest.get('schema') == 'ciel/catalog-db-library/v0.7', 'unexpected db manifest schema')

    for rec in export_records:
        forbidden = sorted(EXPORT_FORBIDDEN_FIELDS.intersection(rec.keys()))
        _append_issue(issues, not forbidden, f"export card leaks private fields: {rec.get('id')} -> {forbidden}")
        _append_issue(issues, rec.get('internal_card_id') in {card.get('internal_card_id') for card in internal_cards}, f"missing internal card link for export card {rec.get('id')}")
        _append_issue(issues, rec.get('board_card_id') in export_ids, f"missing board card for export card {rec.get('id')}")
        _append_issue(issues, not str(rec.get('path', '')).startswith('integration/registries/definitions/'), f"recursion detected in export path {rec.get('path')}")

    for card in internal_cards:
        _append_issue(issues, card.get('export_card_id') in export_ids, f"internal card points to missing export card {card.get('internal_card_id')}")
        _append_issue(issues, card.get('board_card_id') in board_ids, f"internal card points to missing board {card.get('internal_card_id')}")

    _append_issue(issues, int(sync_report.get('board_count', 0) or 0) == int(sync_registry.get('count', 0) or 0), 'sync report board_count mismatch')
    _append_issue(issues, int(db_manifest.get('totals', {}).get('subsystem_sync', 0) or 0) == int(sync_registry.get('count', 0) or 0), 'db manifest subsystem_sync total mismatch')

    if runtime_gating:
        _append_issue(issues, runtime_gating.get('private_state_export_allowed') is False, 'runtime gating allows private state export')
        _append_issue(issues, runtime_gating.get('requires_projection_operator') is True, 'runtime gating missing projection requirement')
    if bridge_report:
        _append_issue(issues, 'subsystem_sync_manifest' in bridge_report, 'orbital bridge report missing subsystem_sync_manifest')
        _append_issue(issues, 'runtime_gating' in bridge_report, 'orbital bridge report missing runtime_gating')
    if sapiens_packet:
        _append_issue(issues, sapiens_packet.get('surface_policy', {}).get('private_state_export_allowed') is False, 'sapiens packet surface policy allows private export')
        _append_issue(issues, sapiens_packet.get('inference_contract', {}).get('projection_required') is True, 'sapiens packet inference contract missing projection requirement')

    report = {
        'schema': 'ciel/orbital-registry-verification-report/v0.1',
        'ok': not issues,
        'counts': {
            'export_cards': len(export_records),
            'internal_cards': len(internal_cards),
            'boards': len(board_ids),
            'sync_records': int(sync_registry.get('count', 0) or 0),
        },
        'issues': issues,
    }

    out_path = defs / 'verification_report.json'
    out_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if not issues else 1


if __name__ == '__main__':
    raise SystemExit(main())
