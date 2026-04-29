from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESOLVE_SCRIPT = REPO_ROOT / "scripts" / "resolve_orbital_semantics.py"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "build_subsystem_sync_registry.py"
DB_SCRIPT = REPO_ROOT / "scripts" / "build_definition_db_library.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_phase4_resolver_emits_tau_and_board_fields(tmp_path: Path) -> None:
    defs_dir = tmp_path / "integration" / "registries" / "definitions"
    _write_json(defs_dir / "definition_registry.json", {"schema": "ciel/orbital-definition-registry/v0.1", "count": 2, "records": [{"id": "file:src/example_runtime.py", "path": "src/example_runtime.py", "language": "python", "kind": "file", "name": "example_runtime.py", "qualname": "src.example_runtime", "signature": "", "lineno": 1, "end_lineno": 20, "doc": "runtime bridge file", "imports": [], "calls": [], "entrypoint": False}, {"id": "definition:src/example_runtime.py:bridge_node@L4", "path": "src/example_runtime.py", "language": "python", "kind": "function", "name": "bridge_node", "qualname": "bridge_node", "signature": "bridge_node()", "lineno": 4, "end_lineno": 8, "doc": "runtime bridge packet", "imports": [], "calls": [], "entrypoint": False}]})
    subprocess.run([sys.executable, str(RESOLVE_SCRIPT), "--repo-root", str(tmp_path)], check=True, capture_output=True, text=True)
    export_payload = json.loads((defs_dir / "orbital_definition_registry.json").read_text(encoding="utf-8"))
    internal_payload = json.loads((defs_dir / "internal_subsystem_cards.json").read_text(encoding="utf-8"))
    report_payload = json.loads((defs_dir / "orbital_assignment_report.json").read_text(encoding="utf-8"))
    bridge_card = next(r for r in export_payload["records"] if r["name"] == "bridge_node")
    internal_bridge = next(r for r in internal_payload["internal_cards"] if r["export_card_id"] == bridge_card["id"])
    assert export_payload["schema"] == "ciel/orbital-definition-registry-enriched/v0.5"
    assert bridge_card["board_card_id"] == "file:src/example_runtime.py"
    assert bridge_card["tau_local"] == f"tau-local:{bridge_card['id']}"
    assert bridge_card["tau_orbit"] == "tau-orbit:file:src/example_runtime.py"
    assert bridge_card["tau_system"] == "tau-system:GLOBAL_ATTRACTOR"
    assert bridge_card["sync_scope"] == "BOARD_MEMBER"
    assert bridge_card["sync_law_ref"] == "sync-law:METRONOME_BOARD_COUPLING"
    assert bridge_card["condensation_operator"] == "CONDENSE_HALF_CONCLUSIONS"
    assert internal_payload["schema"] == "ciel/internal-subsystem-card-registry/v0.3"
    assert internal_bridge["internal_tau_orbit"] == "tau-orbit:file:src/example_runtime.py"
    assert internal_bridge["internal_tau_system"] == "tau-system:GLOBAL_ATTRACTOR"
    assert report_payload["schema"] == "ciel/orbital-assignment-report/v0.5"
    assert report_payload["board_count"] == 1


def test_phase4_subsystem_sync_registry_aggregates_board_state(tmp_path: Path) -> None:
    defs_dir = tmp_path / "integration" / "registries" / "definitions"
    _write_json(defs_dir / "orbital_definition_registry.json", {"schema": "ciel/orbital-definition-registry-enriched/v0.5", "count": 2, "records": [{"id": "file:src/example_runtime.py", "path": "src/example_runtime.py", "kind": "file", "name": "example_runtime.py", "board_card_id": "file:src/example_runtime.py", "horizon_id": "horizon:src/example_runtime.py", "tau_orbit": "tau-orbit:file:src/example_runtime.py", "tau_system": "tau-system:GLOBAL_ATTRACTOR", "sync_scope": "BOARD_ROOT", "sync_law_ref": "sync-law:METRONOME_BOARD_COUPLING", "condensation_operator": "CONDENSE_HALF_CONCLUSIONS", "orbital_role": "DYNAMIC", "manybody_role": "SUBSYSTEM_BOARD", "export_result": "BOARD<DYNAMIC>", "export_state": "SUBSYSTEM_SUMMARY", "export_confidence": 0.7, "residual_uncertainty": 0.3, "internal_card_id": "internal:file:src/example_runtime.py"}, {"id": "definition:src/example_runtime.py:bridge_node@L4", "path": "src/example_runtime.py", "kind": "function", "name": "bridge_node", "board_card_id": "file:src/example_runtime.py", "horizon_id": "horizon:src/example_runtime.py", "tau_orbit": "tau-orbit:file:src/example_runtime.py", "tau_system": "tau-system:GLOBAL_ATTRACTOR", "sync_scope": "BOARD_MEMBER", "sync_law_ref": "sync-law:METRONOME_BOARD_COUPLING", "condensation_operator": "CONDENSE_HALF_CONCLUSIONS", "orbital_role": "INTERACTION", "manybody_role": "TRANSFER_NODE", "export_result": "BROKERED_TRANSFER_RESULT", "export_state": "BROKERED_INTERFACE", "export_confidence": 0.6, "residual_uncertainty": 0.4, "internal_card_id": "internal:definition:src/example_runtime.py:bridge_node@L4"}]})
    _write_json(defs_dir / "internal_subsystem_cards.json", {"schema": "ciel/internal-subsystem-card-registry/v0.3", "count": 2, "internal_cards": [{"internal_card_id": "internal:file:src/example_runtime.py", "export_card_id": "file:src/example_runtime.py"}, {"internal_card_id": "internal:definition:src/example_runtime.py:bridge_node@L4", "export_card_id": "definition:src/example_runtime.py:bridge_node@L4"}]})
    subprocess.run([sys.executable, str(SYNC_SCRIPT), "--repo-root", str(tmp_path)], check=True, capture_output=True, text=True)
    sync_registry = json.loads((defs_dir / "subsystem_sync_registry.json").read_text(encoding="utf-8"))
    assert sync_registry["schema"] == "ciel/subsystem-sync-registry/v0.1"
    board = sync_registry["records"][0]
    assert board["board_card_id"] == "file:src/example_runtime.py"
    assert board["tau_orbit"] == "tau-orbit:file:src/example_runtime.py"
    assert board["tau_system"] == "tau-system:GLOBAL_ATTRACTOR"
    assert board["member_count"] == 1
    assert board["card_count"] == 2


def test_phase4_db_persists_subsystem_sync_layer(tmp_path: Path) -> None:
    defs_dir = tmp_path / "integration" / "registries" / "definitions"
    _write_json(defs_dir / "orbital_definition_registry.json", {"schema": "ciel/orbital-definition-registry-enriched/v0.5", "card_schema": "ciel/orbital-export-card/v0.5", "sync_schema": "ciel/subsystem-sync-registry/v0.1", "count": 1, "records": [{"id": "file:src/example_runtime.py", "path": "src/example_runtime.py", "language": "python", "kind": "file", "name": "example_runtime.py", "qualname": "src.example_runtime", "signature": "", "lineno": 1, "end_lineno": 20, "doc": "runtime bridge file", "imports": [], "calls": [], "entrypoint": False, "card_schema": "ciel/orbital-export-card/v0.5", "sync_schema": "ciel/subsystem-sync-registry/v0.1", "global_attractor_ref": "GLOBAL_ATTRACTOR:PRIMARY_INFORMATION_SOURCE", "orbital_role": "DYNAMIC", "orbital_confidence": 0.8, "semantic_role": "dynamic-file", "board_card_id": "file:src/example_runtime.py", "container_card_id": None, "subsystem_kind": "BOARD", "manybody_role": "SUBSYSTEM_BOARD", "parent_orbital_role": "IDENTITY", "horizon_id": "horizon:src/example_runtime.py", "horizon_class": "POROUS", "information_regime": "LOCAL_PLUS_HORIZON", "visible_scopes": ["self", "local-orbit", "horizon-leak"], "leak_policy": "HAWKING_EULER", "tau_role": "TAU_LOCAL", "tau_local": "tau-local:file:src/example_runtime.py", "tau_orbit": "tau-orbit:file:src/example_runtime.py", "tau_system": "tau-system:GLOBAL_ATTRACTOR", "sync_scope": "BOARD_ROOT", "sync_law_ref": "sync-law:METRONOME_BOARD_COUPLING", "condensation_operator": "CONDENSE_HALF_CONCLUSIONS", "lagrange_roles": [], "internal_card_id": "internal:file:src/example_runtime.py", "projection_operator": "Π_H[POROUS|HAWKING_EULER]", "privacy_constraint": "GRADIENT_LIMITED_DISCLOSURE", "leak_channel_mode": "HAWKING_EULER_DIFFUSIVE", "leak_budget_class": "MICRO_LEAK_BUDGET", "allowed_visibility_transitions": ["self->container"], "export_state": "SUBSYSTEM_SUMMARY", "export_result": "BOARD<DYNAMIC>", "export_confidence": 0.68, "residual_uncertainty": 0.32, "policy_table_ref": "horizon-policy:POROUS"}]})
    _write_json(defs_dir / "internal_subsystem_cards.json", {"schema": "ciel/internal-subsystem-card-registry/v0.3", "internal_card_schema": "ciel/internal-subsystem-card/v0.3", "sync_schema": "ciel/subsystem-sync-registry/v0.1", "count": 1, "internal_cards": [{"internal_card_id": "internal:file:src/example_runtime.py", "internal_card_schema": "ciel/internal-subsystem-card/v0.3", "sync_schema": "ciel/subsystem-sync-registry/v0.1", "owner_card_id": "file:src/example_runtime.py", "owner_horizon_id": "horizon:src/example_runtime.py", "board_card_id": "file:src/example_runtime.py", "container_card_id": None, "subsystem_kind": "BOARD", "manybody_role": "SUBSYSTEM_BOARD", "internal_visibility": "PRIVATE_SUBSYSTEM_ONLY", "internal_candidate_states": ["DYNAMIC_LOCAL_CANDIDATE"], "internal_conflict_state": "MEDIUM", "internal_superposition_state": "BOARD_AGGREGATION_ACTIVE", "internal_resolution_trace": ["SUBSYSTEM_AGGREGATION"], "internal_tau_local": "tau-local:file:src/example_runtime.py", "internal_tau_orbit": "tau-orbit:file:src/example_runtime.py", "internal_tau_system": "tau-system:GLOBAL_ATTRACTOR", "sync_scope": "BOARD_ROOT", "sync_law_ref": "sync-law:METRONOME_BOARD_COUPLING", "condensation_operator": "CONDENSE_HALF_CONCLUSIONS", "internal_memory_mode": "TRANSIENT_RUNTIME", "projection_operator": "Π_H[POROUS|HAWKING_EULER]", "export_card_id": "file:src/example_runtime.py", "privacy_constraint": "GRADIENT_LIMITED_DISCLOSURE", "horizon_transition_profile": "POROUS", "exportable_fields": ["export_result"], "sealed_fields": ["internal_candidate_states"], "policy_table_ref": "horizon-policy:POROUS"}]})
    _write_json(defs_dir / "horizon_policy_matrix.json", {"schema": "ciel/horizon-policy-matrix/v0.1", "classes": {"POROUS": {"privacy_constraint": "GRADIENT_LIMITED_DISCLOSURE", "leak_channel_mode": "HAWKING_EULER_DIFFUSIVE", "leak_budget_class": "MICRO_LEAK_BUDGET", "allowed_visibility_transitions": ["self->container"], "exportable_fields": ["export_result"], "sealed_fields": ["internal_candidate_states"]}}})
    _write_json(defs_dir / "subsystem_sync_registry.json", {"schema": "ciel/subsystem-sync-registry/v0.1", "count": 1, "records": [{"board_card_id": "file:src/example_runtime.py", "board_path": "src/example_runtime.py", "board_horizon_id": "horizon:src/example_runtime.py", "tau_orbit": "tau-orbit:file:src/example_runtime.py", "tau_system": "tau-system:GLOBAL_ATTRACTOR", "sync_law_ref": "sync-law:METRONOME_BOARD_COUPLING", "condensation_operator": "CONDENSE_HALF_CONCLUSIONS", "board_sync_scope": "BOARD_ROOT", "child_sync_scopes": ["BOARD_ROOT"], "child_card_ids": ["file:src/example_runtime.py"], "member_card_ids": [], "internal_card_ids": ["internal:file:src/example_runtime.py"], "member_count": 0, "card_count": 1, "orbit_role_distribution": {"DYNAMIC": 1}, "manybody_role_distribution": {"SUBSYSTEM_BOARD": 1}, "avg_export_confidence": 0.68, "avg_residual_uncertainty": 0.32, "board_export_state": "SUBSYSTEM_SUMMARY", "board_export_result": "BOARD<DYNAMIC>", "dominant_orbit": "DYNAMIC", "dominant_manybody_role": "SUBSYSTEM_BOARD", "private_condensate_sources": ["internal:file:src/example_runtime.py"], "aggregation_model": "BOARD_METRONOME_COUPLING", "condensed_half_conclusion": {"result": "BOARD<DYNAMIC>", "confidence": 0.68, "uncertainty": 0.32}}]})
    _write_json(defs_dir / "subsystem_sync_report.json", {"schema": "ciel/subsystem-sync-report/v0.1", "board_count": 1, "avg_members_per_board": 0.0, "sync_scope_counts": {"BOARD_ROOT": 1}, "sync_law_counts": {"sync-law:METRONOME_BOARD_COUPLING": 1}, "condensation_operator_counts": {"CONDENSE_HALF_CONCLUSIONS": 1}, "tau_orbit_count": 1, "tau_system_count": 1})
    _write_json(defs_dir / "nonlocal_definition_edges.json", {"schema": "ciel/nonlocal-definition-edges/v0.1", "count": 0, "edges": []})
    _write_json(defs_dir / "orbital_assignment_report.json", {"schema": "ciel/orbital-assignment-report/v0.5", "card_schema": "ciel/orbital-export-card/v0.5", "internal_card_schema": "ciel/internal-subsystem-card/v0.3", "horizon_policy_schema": "ciel/horizon-policy-matrix/v0.1", "sync_schema": "ciel/subsystem-sync-registry/v0.1", "count": 1, "export_card_count": 1, "internal_card_count": 1, "board_count": 1, "orbit_counts": {"DYNAMIC": 1}, "unresolved": 0, "information_regime_counts": {"LOCAL_PLUS_HORIZON": 1}, "horizon_class_counts": {"POROUS": 1}, "tau_role_counts": {"TAU_LOCAL": 1}, "sync_scope_counts": {"BOARD_ROOT": 1}, "manybody_role_counts": {"SUBSYSTEM_BOARD": 1}, "lagrange_role_counts": {}, "projection_operator_counts": {"Π_H[POROUS|HAWKING_EULER]": 1}, "privacy_constraint_counts": {"GRADIENT_LIMITED_DISCLOSURE": 1}, "leak_channel_mode_counts": {"HAWKING_EULER_DIFFUSIVE": 1}, "leak_budget_class_counts": {"MICRO_LEAK_BUDGET": 1}, "export_state_counts": {"SUBSYSTEM_SUMMARY": 1}, "transition_profile_counts": {"POROUS": 1}, "internal_memory_mode_counts": {"TRANSIENT_RUNTIME": 1}, "internal_conflict_state_counts": {"MEDIUM": 1}, "internal_visibility_counts": {"PRIVATE_SUBSYSTEM_ONLY": 1}})
    subprocess.run([sys.executable, str(DB_SCRIPT), "--repo-root", str(tmp_path)], check=True, capture_output=True, text=True)
    manifest = json.loads((defs_dir / "db_library" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "ciel/catalog-db-library/v0.7"
    assert manifest["totals"]["subsystem_sync"] == 1
    conn = sqlite3.connect(defs_dir / "db_library" / "subsystem_sync.sqlite")
    assert conn.execute("SELECT board_card_id, tau_orbit, tau_system, sync_law_ref, condensation_operator FROM subsystem_sync").fetchone() == ("file:src/example_runtime.py", "tau-orbit:file:src/example_runtime.py", "tau-system:GLOBAL_ATTRACTOR", "sync-law:METRONOME_BOARD_COUPLING", "CONDENSE_HALF_CONCLUSIONS")
    conn.close()
