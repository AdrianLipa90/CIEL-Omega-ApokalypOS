from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESOLVE_SCRIPT = REPO_ROOT / "scripts" / "resolve_orbital_semantics.py"
DB_SCRIPT = REPO_ROOT / "scripts" / "build_definition_db_library.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_resolve_orbital_semantics_emits_export_internal_and_policy_layers(tmp_path: Path) -> None:
    defs_dir = tmp_path / "integration" / "registries" / "definitions"
    _write_json(defs_dir / "definition_registry.json", {"schema": "ciel/orbital-definition-registry/v0.1", "count": 2, "records": [
        {"id": "file:src/example_runtime.py", "path": "src/example_runtime.py", "language": "python", "kind": "file", "name": "example_runtime.py", "qualname": "src.example_runtime", "signature": "", "lineno": 1, "end_lineno": 20, "doc": "runtime bridge file", "imports": [], "calls": [], "entrypoint": False},
        {"id": "definition:src/example_runtime.py:bridge_node@L4", "path": "src/example_runtime.py", "language": "python", "kind": "function", "name": "bridge_node", "qualname": "bridge_node", "signature": "bridge_node()", "lineno": 4, "end_lineno": 8, "doc": "runtime bridge packet", "imports": [], "calls": [], "entrypoint": False}
    ]})
    subprocess.run([sys.executable, str(RESOLVE_SCRIPT), "--repo-root", str(tmp_path)], check=True, capture_output=True, text=True)
    enriched = json.loads((defs_dir / "orbital_definition_registry.json").read_text(encoding="utf-8"))
    internal = json.loads((defs_dir / "internal_subsystem_cards.json").read_text(encoding="utf-8"))
    policy = json.loads((defs_dir / "horizon_policy_matrix.json").read_text(encoding="utf-8"))
    report = json.loads((defs_dir / "orbital_assignment_report.json").read_text(encoding="utf-8"))

    bridge_card = next(r for r in enriched["records"] if r["name"] == "bridge_node")
    internal_bridge = next(r for r in internal["internal_cards"] if r["owner_card_id"] == bridge_card["id"])

    assert enriched["schema"] == "ciel/orbital-definition-registry-enriched/v0.4"
    assert internal["schema"] == "ciel/internal-subsystem-card-registry/v0.2"
    assert policy["schema"] == "ciel/horizon-policy-matrix/v0.1"
    assert set(policy["classes"].keys()) == {"SEALED", "POROUS", "TRANSMISSIVE", "OBSERVATIONAL"}
    assert bridge_card["privacy_constraint"] == "BROKER_GATED_DISCLOSURE"
    assert bridge_card["leak_channel_mode"] == "HAWKING_EULER_BROKERED"
    assert bridge_card["leak_budget_class"] == "BROKERED_LEAK_BUDGET"
    assert bridge_card["policy_table_ref"] == "horizon-policy:TRANSMISSIVE"
    assert "internal_candidate_states" not in bridge_card
    assert internal_bridge["internal_visibility"] == "PRIVATE_SUBSYSTEM_ONLY"
    assert internal_bridge["horizon_transition_profile"] == "TRANSMISSIVE"
    assert "export_result" in internal_bridge["exportable_fields"]
    assert "privacy_constraint_counts" in report
    assert "leak_channel_mode_counts" in report
    assert "leak_budget_class_counts" in report
    assert "transition_profile_counts" in report


def test_build_definition_db_library_persists_policy_and_internal_layers(tmp_path: Path) -> None:
    defs_dir = tmp_path / "integration" / "registries" / "definitions"
    _write_json(defs_dir / "orbital_definition_registry.json", {"schema": "ciel/orbital-definition-registry-enriched/v0.4", "card_schema": "ciel/orbital-export-card/v0.4", "internal_card_schema": "ciel/internal-subsystem-card/v0.2", "horizon_policy_schema": "ciel/horizon-policy-matrix/v0.1", "count": 1, "records": [{"id": "definition:src/example.py:node@L10", "path": "src/example.py", "language": "python", "kind": "function", "name": "node", "qualname": "node", "signature": "node()", "lineno": 10, "end_lineno": 12, "doc": "runtime bridge packet", "imports": [], "calls": [], "entrypoint": False, "card_schema": "ciel/orbital-export-card/v0.4", "global_attractor_ref": "GLOBAL_ATTRACTOR:PRIMARY_INFORMATION_SOURCE", "orbital_role": "INTERACTION", "orbital_confidence": 0.71, "semantic_role": "packet-memory-bridge", "container_card_id": "file:src/example.py", "subsystem_kind": "NODE", "manybody_role": "TRANSFER_NODE", "parent_orbital_role": "BOUNDARY", "horizon_id": "horizon:src/example.py", "horizon_class": "TRANSMISSIVE", "information_regime": "BOUNDARY_BROKER", "visible_scopes": ["self", "container", "adjacent-horizon", "broker-leak"], "leak_policy": "HAWKING_EULER_BROKERED", "tau_role": "TAU_LOCAL", "lagrange_roles": ["TRANSFER_NODE"], "internal_card_id": "internal:definition:src/example.py:node@L10", "projection_operator": "Π_H[TRANSMISSIVE|HAWKING_EULER_BROKERED]", "privacy_constraint": "BROKER_GATED_DISCLOSURE", "leak_channel_mode": "HAWKING_EULER_BROKERED", "leak_budget_class": "BROKERED_LEAK_BUDGET", "allowed_visibility_transitions": ["self->container", "container->local-orbit", "local-orbit->adjacent-horizon", "adjacent-horizon->broker-leak"], "export_state": "BROKERED_INTERFACE", "export_result": "BROKERED_TRANSFER_RESULT", "export_confidence": 0.61, "residual_uncertainty": 0.39, "policy_table_ref": "horizon-policy:TRANSMISSIVE"}]})
    _write_json(defs_dir / "internal_subsystem_cards.json", {"schema": "ciel/internal-subsystem-card-registry/v0.2", "internal_card_schema": "ciel/internal-subsystem-card/v0.2", "horizon_policy_schema": "ciel/horizon-policy-matrix/v0.1", "count": 1, "internal_cards": [{"internal_card_schema": "ciel/internal-subsystem-card/v0.2", "internal_card_id": "internal:definition:src/example.py:node@L10", "owner_card_id": "definition:src/example.py:node@L10", "owner_horizon_id": "horizon:src/example.py", "container_card_id": "file:src/example.py", "subsystem_kind": "NODE", "manybody_role": "TRANSFER_NODE", "internal_visibility": "PRIVATE_SUBSYSTEM_ONLY", "internal_candidate_states": ["INTERACTION_LOCAL_CANDIDATE"], "internal_conflict_state": "HIGH", "internal_superposition_state": "LOCAL_SUPERPOSITION_ACTIVE", "internal_resolution_trace": ["LOCAL_ACCUMULATION"], "internal_tau_local": "tau-local:definition:src/example.py:node@L10", "internal_memory_mode": "TRANSIENT_INTERFACE", "projection_operator": "Π_H[TRANSMISSIVE|HAWKING_EULER_BROKERED]", "privacy_constraint": "BROKER_GATED_DISCLOSURE", "horizon_transition_profile": "TRANSMISSIVE", "exportable_fields": ["export_state", "export_result", "export_confidence"], "sealed_fields": ["internal_candidate_states"], "policy_table_ref": "horizon-policy:TRANSMISSIVE", "export_card_id": "definition:src/example.py:node@L10"}]})
    _write_json(defs_dir / "horizon_policy_matrix.json", {"schema": "ciel/horizon-policy-matrix/v0.1", "classes": {"TRANSMISSIVE": {"privacy_constraint": "BROKER_GATED_DISCLOSURE", "leak_channel_mode": "HAWKING_EULER_BROKERED", "leak_budget_class": "BROKERED_LEAK_BUDGET", "allowed_visibility_transitions": ["self->container", "container->local-orbit", "local-orbit->adjacent-horizon", "adjacent-horizon->broker-leak"], "exportable_fields": ["export_state", "export_result", "export_confidence"], "sealed_fields": ["internal_candidate_states"]}}})
    _write_json(defs_dir / "nonlocal_definition_edges.json", {"schema": "ciel/nonlocal-definition-edges/v0.1", "count": 1, "edges": [{"source": "definition:src/example.py:node@L10", "target": "file:src/example.py", "relation": "contains", "weight": 1.0}]})
    _write_json(defs_dir / "orbital_assignment_report.json", {"schema": "ciel/orbital-assignment-report/v0.4", "card_schema": "ciel/orbital-export-card/v0.4", "internal_card_schema": "ciel/internal-subsystem-card/v0.2", "horizon_policy_schema": "ciel/horizon-policy-matrix/v0.1", "count": 1, "export_card_count": 1, "internal_card_count": 1, "orbit_counts": {"INTERACTION": 1}, "unresolved": 0, "information_regime_counts": {"BOUNDARY_BROKER": 1}, "horizon_class_counts": {"TRANSMISSIVE": 1}, "tau_role_counts": {"TAU_LOCAL": 1}, "manybody_role_counts": {"TRANSFER_NODE": 1}, "lagrange_role_counts": {"TRANSFER_NODE": 1}, "projection_operator_counts": {"Π_H[TRANSMISSIVE|HAWKING_EULER_BROKERED]": 1}, "privacy_constraint_counts": {"BROKER_GATED_DISCLOSURE": 1}, "leak_channel_mode_counts": {"HAWKING_EULER_BROKERED": 1}, "leak_budget_class_counts": {"BROKERED_LEAK_BUDGET": 1}, "export_state_counts": {"BROKERED_INTERFACE": 1}, "transition_profile_counts": {"TRANSMISSIVE": 1}, "internal_memory_mode_counts": {"TRANSIENT_INTERFACE": 1}, "internal_conflict_state_counts": {"HIGH": 1}, "internal_visibility_counts": {"PRIVATE_SUBSYSTEM_ONLY": 1}})
    subprocess.run([sys.executable, str(DB_SCRIPT), "--repo-root", str(tmp_path)], check=True, capture_output=True, text=True)
    manifest = json.loads((defs_dir / "db_library" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "ciel/catalog-db-library/v0.6"
    assert manifest["totals"]["horizon_policies"] == 1
    conn = sqlite3.connect(defs_dir / "db_library" / "records.sqlite")
    assert conn.execute("SELECT privacy_constraint, leak_channel_mode, leak_budget_class, policy_table_ref FROM records").fetchone() == ("BROKER_GATED_DISCLOSURE", "HAWKING_EULER_BROKERED", "BROKERED_LEAK_BUDGET", "horizon-policy:TRANSMISSIVE")
    conn.close()
    conn = sqlite3.connect(defs_dir / "db_library" / "internal_cards.sqlite")
    assert conn.execute("SELECT privacy_constraint, horizon_transition_profile, policy_table_ref FROM internal_cards").fetchone() == ("BROKER_GATED_DISCLOSURE", "TRANSMISSIVE", "horizon-policy:TRANSMISSIVE")
    conn.close()
    conn = sqlite3.connect(defs_dir / "db_library" / "horizon_policies.sqlite")
    assert conn.execute("SELECT horizon_class, privacy_constraint, leak_channel_mode, leak_budget_class FROM horizon_policies").fetchone() == ("TRANSMISSIVE", "BROKER_GATED_DISCLOSURE", "HAWKING_EULER_BROKERED", "BROKERED_LEAK_BUDGET")
    conn.close()
