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


def test_resolve_orbital_semantics_emits_export_and_internal_card_layers(tmp_path: Path) -> None:
    defs_dir = tmp_path / "integration" / "registries" / "definitions"
    definition_registry = {
        "schema": "ciel/orbital-definition-registry/v0.1",
        "count": 3,
        "records": [
            {
                "id": "file:src/example_runtime.py",
                "path": "src/example_runtime.py",
                "language": "python",
                "kind": "file",
                "name": "example_runtime.py",
                "qualname": "src.example_runtime",
                "signature": "",
                "lineno": 1,
                "end_lineno": 20,
                "doc": "runtime bridge file",
                "imports": [],
                "calls": [],
                "entrypoint": False,
            },
            {
                "id": "definition:src/example_runtime.py:bridge_node@L4",
                "path": "src/example_runtime.py",
                "language": "python",
                "kind": "function",
                "name": "bridge_node",
                "qualname": "bridge_node",
                "signature": "bridge_node()",
                "lineno": 4,
                "end_lineno": 8,
                "doc": "runtime bridge packet",
                "imports": [],
                "calls": [],
                "entrypoint": False,
            },
            {
                "id": "definition:src/policy_guard.py:guard_rule@L2",
                "path": "src/policy_guard.py",
                "language": "python",
                "kind": "function",
                "name": "guard_rule",
                "qualname": "guard_rule",
                "signature": "guard_rule()",
                "lineno": 2,
                "end_lineno": 6,
                "doc": "boundary policy check",
                "imports": [],
                "calls": [],
                "entrypoint": False,
            },
        ],
    }
    _write_json(defs_dir / "definition_registry.json", definition_registry)

    subprocess.run(
        [sys.executable, str(RESOLVE_SCRIPT), "--repo-root", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    enriched = json.loads((defs_dir / "orbital_definition_registry.json").read_text(encoding="utf-8"))
    internal = json.loads((defs_dir / "internal_subsystem_cards.json").read_text(encoding="utf-8"))
    report = json.loads((defs_dir / "orbital_assignment_report.json").read_text(encoding="utf-8"))

    assert enriched["schema"] == "ciel/orbital-definition-registry-enriched/v0.3"
    assert enriched["card_schema"] == "ciel/orbital-export-card/v0.3"
    assert internal["schema"] == "ciel/internal-subsystem-card-registry/v0.1"
    assert internal["internal_card_schema"] == "ciel/internal-subsystem-card/v0.1"

    bridge_card = next(r for r in enriched["records"] if r["name"] == "bridge_node")
    file_card = next(r for r in enriched["records"] if r["kind"] == "file")
    internal_bridge = next(r for r in internal["internal_cards"] if r["owner_card_id"] == bridge_card["id"])

    assert bridge_card["container_card_id"] == file_card["id"]
    assert bridge_card["horizon_id"] == f"horizon:{bridge_card['path']}"
    assert bridge_card["information_regime"] in {"LOCAL_PLUS_HORIZON", "BOUNDARY_BROKER", "GLOBAL_OBSERVATION", "LOCAL_ONLY"}
    assert "TRANSFER_NODE" in bridge_card["lagrange_roles"]
    assert bridge_card["manybody_role"] == "TRANSFER_NODE"
    assert bridge_card["tau_role"].startswith("TAU_")
    assert bridge_card["global_attractor_ref"] == "GLOBAL_ATTRACTOR:PRIMARY_INFORMATION_SOURCE"
    assert bridge_card["projection_operator"].startswith("Π_H[")
    assert bridge_card["export_state"] == "BROKERED_INTERFACE"
    assert bridge_card["export_result"] == "BROKERED_TRANSFER_RESULT"
    assert 0.0 <= bridge_card["residual_uncertainty"] <= 1.0

    assert "internal_candidate_states" not in bridge_card
    assert "internal_conflict_state" not in bridge_card
    assert bridge_card["internal_card_id"] == internal_bridge["internal_card_id"]

    assert internal_bridge["internal_visibility"] == "PRIVATE_SUBSYSTEM_ONLY"
    assert internal_bridge["projection_operator"] == bridge_card["projection_operator"]
    assert internal_bridge["export_card_id"] == bridge_card["id"]
    assert internal_bridge["internal_memory_mode"] in {
        "PERSISTENT_IDENTITY", "PERSISTENT_MEMORY", "TRANSIENT_RUNTIME", "TRANSIENT_INTERFACE",
        "SNAPSHOT_OBSERVER", "POLICY_CACHE", "CURRICULUM_SNAPSHOT",
    }

    assert report["schema"] == "ciel/orbital-assignment-report/v0.3"
    assert report["export_card_count"] == 3
    assert report["internal_card_count"] == 3
    assert "projection_operator_counts" in report
    assert "export_state_counts" in report
    assert "internal_memory_mode_counts" in report
    assert "internal_conflict_state_counts" in report
    assert "internal_visibility_counts" in report


def test_build_definition_db_library_persists_export_and_internal_layers(tmp_path: Path) -> None:
    defs_dir = tmp_path / "integration" / "registries" / "definitions"
    _write_json(
        defs_dir / "orbital_definition_registry.json",
        {
            "schema": "ciel/orbital-definition-registry-enriched/v0.3",
            "card_schema": "ciel/orbital-export-card/v0.3",
            "internal_card_schema": "ciel/internal-subsystem-card/v0.1",
            "count": 1,
            "records": [
                {
                    "id": "definition:src/example.py:node@L10",
                    "path": "src/example.py",
                    "language": "python",
                    "kind": "function",
                    "name": "node",
                    "qualname": "node",
                    "signature": "node()",
                    "lineno": 10,
                    "end_lineno": 12,
                    "doc": "runtime bridge packet",
                    "imports": [],
                    "calls": [],
                    "entrypoint": False,
                    "card_schema": "ciel/orbital-export-card/v0.3",
                    "global_attractor_ref": "GLOBAL_ATTRACTOR:PRIMARY_INFORMATION_SOURCE",
                    "orbital_role": "INTERACTION",
                    "orbital_confidence": 0.71,
                    "semantic_role": "packet-memory-bridge",
                    "container_card_id": "file:src/example.py",
                    "subsystem_kind": "NODE",
                    "manybody_role": "TRANSFER_NODE",
                    "parent_orbital_role": "BOUNDARY",
                    "horizon_id": "horizon:src/example.py",
                    "horizon_class": "TRANSMISSIVE",
                    "information_regime": "BOUNDARY_BROKER",
                    "visible_scopes": ["self", "container", "adjacent-horizon", "broker-leak"],
                    "leak_policy": "HAWKING_EULER_BROKERED",
                    "tau_role": "TAU_LOCAL",
                    "lagrange_roles": ["TRANSFER_NODE"],
                    "internal_card_id": "internal:definition:src/example.py:node@L10",
                    "projection_operator": "Π_H[TRANSMISSIVE|HAWKING_EULER_BROKERED]",
                    "export_state": "BROKERED_INTERFACE",
                    "export_result": "BROKERED_TRANSFER_RESULT",
                    "export_confidence": 0.61,
                    "residual_uncertainty": 0.39,
                }
            ],
        },
    )
    _write_json(
        defs_dir / "internal_subsystem_cards.json",
        {
            "schema": "ciel/internal-subsystem-card-registry/v0.1",
            "internal_card_schema": "ciel/internal-subsystem-card/v0.1",
            "count": 1,
            "internal_cards": [
                {
                    "internal_card_schema": "ciel/internal-subsystem-card/v0.1",
                    "internal_card_id": "internal:definition:src/example.py:node@L10",
                    "owner_card_id": "definition:src/example.py:node@L10",
                    "owner_horizon_id": "horizon:src/example.py",
                    "container_card_id": "file:src/example.py",
                    "subsystem_kind": "NODE",
                    "manybody_role": "TRANSFER_NODE",
                    "internal_visibility": "PRIVATE_SUBSYSTEM_ONLY",
                    "internal_candidate_states": ["INTERACTION_LOCAL_CANDIDATE", "TRANSFER_NODE_CANDIDATE", "BROKER_NEGOTIATION_PENDING"],
                    "internal_conflict_state": "HIGH",
                    "internal_superposition_state": "LOCAL_SUPERPOSITION_ACTIVE",
                    "internal_resolution_trace": ["LOCAL_ACCUMULATION", "LOCAL_SELECTION", "HORIZON_PROJECTION<HAWKING_EULER_BROKERED>"],
                    "internal_tau_local": "tau-local:definition:src/example.py:node@L10",
                    "internal_memory_mode": "TRANSIENT_INTERFACE",
                    "projection_operator": "Π_H[TRANSMISSIVE|HAWKING_EULER_BROKERED]",
                    "export_card_id": "definition:src/example.py:node@L10",
                }
            ],
        },
    )
    _write_json(
        defs_dir / "nonlocal_definition_edges.json",
        {
            "schema": "ciel/nonlocal-definition-edges/v0.1",
            "count": 1,
            "edges": [
                {"source": "definition:src/example.py:node@L10", "target": "file:src/example.py", "relation": "contains", "weight": 1.0}
            ],
        },
    )
    _write_json(
        defs_dir / "orbital_assignment_report.json",
        {
            "schema": "ciel/orbital-assignment-report/v0.3",
            "card_schema": "ciel/orbital-export-card/v0.3",
            "internal_card_schema": "ciel/internal-subsystem-card/v0.1",
            "count": 1,
            "export_card_count": 1,
            "internal_card_count": 1,
            "orbit_counts": {"INTERACTION": 1},
            "unresolved": 0,
            "information_regime_counts": {"BOUNDARY_BROKER": 1},
            "horizon_class_counts": {"TRANSMISSIVE": 1},
            "tau_role_counts": {"TAU_LOCAL": 1},
            "manybody_role_counts": {"TRANSFER_NODE": 1},
            "lagrange_role_counts": {"TRANSFER_NODE": 1},
            "projection_operator_counts": {"Π_H[TRANSMISSIVE|HAWKING_EULER_BROKERED]": 1},
            "export_state_counts": {"BROKERED_INTERFACE": 1},
            "internal_memory_mode_counts": {"TRANSIENT_INTERFACE": 1},
            "internal_conflict_state_counts": {"HIGH": 1},
            "internal_visibility_counts": {"PRIVATE_SUBSYSTEM_ONLY": 1},
        },
    )

    subprocess.run(
        [sys.executable, str(DB_SCRIPT), "--repo-root", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    manifest = json.loads((defs_dir / "db_library" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "ciel/catalog-db-library/v0.5"
    assert manifest["card_schema"] == "ciel/orbital-export-card/v0.3"
    assert manifest["internal_card_schema"] == "ciel/internal-subsystem-card/v0.1"
    assert manifest["totals"]["records"] == 1
    assert manifest["totals"]["internal_cards"] == 1

    conn = sqlite3.connect(defs_dir / "db_library" / "records.sqlite")
    row = conn.execute(
        "SELECT container_card_id, horizon_id, information_regime, leak_policy, tau_role, manybody_role, internal_card_id, projection_operator, export_state FROM records"
    ).fetchone()
    conn.close()

    assert row == (
        "file:src/example.py",
        "horizon:src/example.py",
        "BOUNDARY_BROKER",
        "HAWKING_EULER_BROKERED",
        "TAU_LOCAL",
        "TRANSFER_NODE",
        "internal:definition:src/example.py:node@L10",
        "Π_H[TRANSMISSIVE|HAWKING_EULER_BROKERED]",
        "BROKERED_INTERFACE",
    )

    conn = sqlite3.connect(defs_dir / "db_library" / "internal_cards.sqlite")
    internal_row = conn.execute(
        "SELECT internal_visibility, internal_memory_mode, projection_operator, export_card_id FROM internal_cards"
    ).fetchone()
    conn.close()

    assert internal_row == (
        "PRIVATE_SUBSYSTEM_ONLY",
        "TRANSIENT_INTERFACE",
        "Π_H[TRANSMISSIVE|HAWKING_EULER_BROKERED]",
        "definition:src/example.py:node@L10",
    )
