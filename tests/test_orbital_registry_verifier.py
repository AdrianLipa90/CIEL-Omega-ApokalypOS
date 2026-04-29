from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify_orbital_registry_integrity.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def test_verify_orbital_registry_integrity_accepts_projected_runtime_state(tmp_path: Path) -> None:
    defs_dir = tmp_path / 'integration' / 'registries' / 'definitions'
    bridge_dir = tmp_path / 'integration' / 'reports' / 'orbital_bridge'
    sapiens_dir = tmp_path / 'integration' / 'reports' / 'sapiens_client'

    _write_json(defs_dir / 'orbital_definition_registry.json', {'schema': 'ciel/orbital-definition-registry-enriched/v0.5', 'records': [{'id': 'file:src/example.py', 'path': 'src/example.py', 'board_card_id': 'file:src/example.py', 'internal_card_id': 'internal:file:src/example.py'}]})
    _write_json(defs_dir / 'internal_subsystem_cards.json', {'schema': 'ciel/internal-subsystem-card-registry/v0.3', 'internal_cards': [{'internal_card_id': 'internal:file:src/example.py', 'export_card_id': 'file:src/example.py', 'board_card_id': 'file:src/example.py'}]})
    _write_json(defs_dir / 'horizon_policy_matrix.json', {'schema': 'ciel/horizon-policy-matrix/v0.1', 'classes': {'POROUS': {'privacy_constraint': 'GRADIENT_LIMITED_DISCLOSURE'}}})
    _write_json(defs_dir / 'subsystem_sync_registry.json', {'schema': 'ciel/subsystem-sync-registry/v0.1', 'count': 1, 'records': [{'board_card_id': 'file:src/example.py'}]})
    _write_json(defs_dir / 'subsystem_sync_report.json', {'schema': 'ciel/subsystem-sync-report/v0.1', 'board_count': 1})
    _write_json(defs_dir / 'orbital_assignment_report.json', {'privacy_constraint_counts': {'GRADIENT_LIMITED_DISCLOSURE': 1}, 'horizon_class_counts': {'POROUS': 1}})
    _write_json(defs_dir / 'db_library' / 'manifest.json', {'schema': 'ciel/catalog-db-library/v0.7', 'totals': {'subsystem_sync': 1}})
    _write_json(bridge_dir / 'orbital_bridge_report.json', {'subsystem_sync_manifest': {'board_count': 1}, 'runtime_gating': {'private_state_export_allowed': False, 'requires_projection_operator': True}})
    _write_json(bridge_dir / 'runtime_gating.json', {'private_state_export_allowed': False, 'requires_projection_operator': True})
    _write_json(sapiens_dir / 'latest_packet.json', {'surface_policy': {'private_state_export_allowed': False}, 'inference_contract': {'projection_required': True}})

    proc = subprocess.run([sys.executable, str(VERIFY_SCRIPT), '--repo-root', str(tmp_path)], check=False, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    report = json.loads((defs_dir / 'verification_report.json').read_text(encoding='utf-8'))
    assert report['schema'] == 'ciel/orbital-registry-verification-report/v0.1'
    assert report['ok'] is True
    assert report['counts']['export_cards'] == 1
