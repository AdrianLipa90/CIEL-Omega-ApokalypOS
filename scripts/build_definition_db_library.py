#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any


def repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except Exception:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return load_json(path)


def recreate(path: Path) -> sqlite3.Connection:
    for suffix in ("", "-wal", "-shm"):
        candidate = Path(f"{path}{suffix}") if suffix else path
        if candidate.exists():
            candidate.unlink()
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=DELETE;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    return conn


def write_records_db(db_path: Path, records: list[dict[str, Any]]) -> int:
    conn = recreate(db_path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE records (
            id TEXT PRIMARY KEY, path TEXT NOT NULL, language TEXT, kind TEXT, name TEXT, qualname TEXT,
            signature TEXT, lineno INTEGER, end_lineno INTEGER, doc TEXT, imports_json TEXT, calls_json TEXT,
            entrypoint INTEGER, card_schema TEXT, sync_schema TEXT, global_attractor_ref TEXT,
            orbital_role TEXT, orbital_confidence REAL, semantic_role TEXT, board_card_id TEXT,
            container_card_id TEXT, subsystem_kind TEXT, manybody_role TEXT, parent_orbital_role TEXT,
            horizon_id TEXT, horizon_class TEXT, information_regime TEXT, visible_scopes_json TEXT,
            leak_policy TEXT, tau_role TEXT, tau_local TEXT, tau_orbit TEXT, tau_system TEXT,
            sync_scope TEXT, sync_law_ref TEXT, condensation_operator TEXT, lagrange_roles_json TEXT,
            internal_card_id TEXT, projection_operator TEXT, privacy_constraint TEXT, leak_channel_mode TEXT,
            leak_budget_class TEXT, allowed_visibility_transitions_json TEXT, export_state TEXT,
            export_result TEXT, export_confidence REAL, residual_uncertainty REAL, policy_table_ref TEXT
        );
        CREATE INDEX idx_records_board_card_id ON records(board_card_id);
        CREATE INDEX idx_records_tau_orbit ON records(tau_orbit);
        CREATE INDEX idx_records_tau_system ON records(tau_system);
        CREATE INDEX idx_records_sync_scope ON records(sync_scope);
        CREATE INDEX idx_records_sync_law_ref ON records(sync_law_ref);
    """)
    cur.executemany(
        "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [(
            rec.get("id"), rec.get("path"), rec.get("language"), rec.get("kind"), rec.get("name"), rec.get("qualname"), rec.get("signature"), rec.get("lineno"), rec.get("end_lineno"), rec.get("doc"),
            json.dumps(rec.get("imports", []), ensure_ascii=False), json.dumps(rec.get("calls", []), ensure_ascii=False), 1 if rec.get("entrypoint") else 0,
            rec.get("card_schema"), rec.get("sync_schema"), rec.get("global_attractor_ref"), rec.get("orbital_role"), rec.get("orbital_confidence"), rec.get("semantic_role"), rec.get("board_card_id"), rec.get("container_card_id"),
            rec.get("subsystem_kind"), rec.get("manybody_role"), rec.get("parent_orbital_role"), rec.get("horizon_id"), rec.get("horizon_class"), rec.get("information_regime"), json.dumps(rec.get("visible_scopes", []), ensure_ascii=False),
            rec.get("leak_policy"), rec.get("tau_role"), rec.get("tau_local"), rec.get("tau_orbit"), rec.get("tau_system"), rec.get("sync_scope"), rec.get("sync_law_ref"), rec.get("condensation_operator"), json.dumps(rec.get("lagrange_roles", []), ensure_ascii=False),
            rec.get("internal_card_id"), rec.get("projection_operator"), rec.get("privacy_constraint"), rec.get("leak_channel_mode"), rec.get("leak_budget_class"), json.dumps(rec.get("allowed_visibility_transitions", []), ensure_ascii=False),
            rec.get("export_state"), rec.get("export_result"), rec.get("export_confidence"), rec.get("residual_uncertainty"), rec.get("policy_table_ref")
        ) for rec in records]
    )
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    conn.close()
    return count


def write_internal_cards_db(db_path: Path, records: list[dict[str, Any]]) -> int:
    conn = recreate(db_path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE internal_cards (
            internal_card_id TEXT PRIMARY KEY, internal_card_schema TEXT, sync_schema TEXT, owner_card_id TEXT,
            owner_horizon_id TEXT, board_card_id TEXT, container_card_id TEXT, subsystem_kind TEXT,
            manybody_role TEXT, internal_visibility TEXT, internal_candidate_states_json TEXT,
            internal_conflict_state TEXT, internal_superposition_state TEXT, internal_resolution_trace_json TEXT,
            internal_tau_local TEXT, internal_tau_orbit TEXT, internal_tau_system TEXT, sync_scope TEXT,
            sync_law_ref TEXT, condensation_operator TEXT, internal_memory_mode TEXT, projection_operator TEXT,
            export_card_id TEXT, privacy_constraint TEXT, horizon_transition_profile TEXT,
            exportable_fields_json TEXT, sealed_fields_json TEXT, policy_table_ref TEXT
        );
        CREATE INDEX idx_internal_board_card_id ON internal_cards(board_card_id);
        CREATE INDEX idx_internal_tau_orbit ON internal_cards(internal_tau_orbit);
        CREATE INDEX idx_internal_tau_system ON internal_cards(internal_tau_system);
        CREATE INDEX idx_internal_sync_scope ON internal_cards(sync_scope);
    """)
    cur.executemany(
        "INSERT INTO internal_cards VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [(
            rec.get("internal_card_id"), rec.get("internal_card_schema"), rec.get("sync_schema"), rec.get("owner_card_id"), rec.get("owner_horizon_id"), rec.get("board_card_id"), rec.get("container_card_id"), rec.get("subsystem_kind"),
            rec.get("manybody_role"), rec.get("internal_visibility"), json.dumps(rec.get("internal_candidate_states", []), ensure_ascii=False), rec.get("internal_conflict_state"), rec.get("internal_superposition_state"), json.dumps(rec.get("internal_resolution_trace", []), ensure_ascii=False),
            rec.get("internal_tau_local"), rec.get("internal_tau_orbit"), rec.get("internal_tau_system"), rec.get("sync_scope"), rec.get("sync_law_ref"), rec.get("condensation_operator"), rec.get("internal_memory_mode"), rec.get("projection_operator"),
            rec.get("export_card_id"), rec.get("privacy_constraint"), rec.get("horizon_transition_profile"), json.dumps(rec.get("exportable_fields", []), ensure_ascii=False), json.dumps(rec.get("sealed_fields", []), ensure_ascii=False), rec.get("policy_table_ref")
        ) for rec in records]
    )
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM internal_cards").fetchone()[0]
    conn.close()
    return count


def write_policy_db(db_path: Path, policy_payload: dict[str, Any]) -> int:
    conn = recreate(db_path)
    cur = conn.cursor()
    cur.executescript("CREATE TABLE horizon_policies (horizon_class TEXT PRIMARY KEY, privacy_constraint TEXT, leak_channel_mode TEXT, leak_budget_class TEXT, allowed_visibility_transitions_json TEXT, exportable_fields_json TEXT, sealed_fields_json TEXT);")
    classes = policy_payload.get("classes", {})
    cur.executemany(
        "INSERT INTO horizon_policies VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(
            h,
            p.get("privacy_constraint"),
            p.get("leak_channel_mode"),
            p.get("leak_budget_class"),
            json.dumps(p.get("allowed_visibility_transitions", []), ensure_ascii=False),
            json.dumps(p.get("exportable_fields", []), ensure_ascii=False),
            json.dumps(p.get("sealed_fields", []), ensure_ascii=False),
        ) for h, p in classes.items()]
    )
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM horizon_policies").fetchone()[0]
    conn.close()
    return count


def write_subsystem_sync_db(db_path: Path, registry_payload: dict[str, Any], report_payload: dict[str, Any]) -> int:
    conn = recreate(db_path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE subsystem_sync (
            board_card_id TEXT PRIMARY KEY, board_path TEXT, board_horizon_id TEXT, tau_orbit TEXT, tau_system TEXT,
            sync_law_ref TEXT, condensation_operator TEXT, board_sync_scope TEXT, child_sync_scopes_json TEXT,
            child_card_ids_json TEXT, member_card_ids_json TEXT, internal_card_ids_json TEXT, member_count INTEGER,
            card_count INTEGER, orbit_role_distribution_json TEXT, manybody_role_distribution_json TEXT,
            avg_export_confidence REAL, avg_residual_uncertainty REAL, board_export_state TEXT, board_export_result TEXT,
            dominant_orbit TEXT, dominant_manybody_role TEXT, private_condensate_sources_json TEXT,
            aggregation_model TEXT, condensed_half_conclusion_json TEXT
        );
        CREATE TABLE subsystem_sync_report (key TEXT PRIMARY KEY, value_json TEXT NOT NULL);
    """)
    cur.executemany(
        "INSERT INTO subsystem_sync VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [(
            rec.get("board_card_id"), rec.get("board_path"), rec.get("board_horizon_id"), rec.get("tau_orbit"), rec.get("tau_system"), rec.get("sync_law_ref"), rec.get("condensation_operator"), rec.get("board_sync_scope"),
            json.dumps(rec.get("child_sync_scopes", []), ensure_ascii=False), json.dumps(rec.get("child_card_ids", []), ensure_ascii=False), json.dumps(rec.get("member_card_ids", []), ensure_ascii=False), json.dumps(rec.get("internal_card_ids", []), ensure_ascii=False),
            rec.get("member_count"), rec.get("card_count"), json.dumps(rec.get("orbit_role_distribution", {}), ensure_ascii=False), json.dumps(rec.get("manybody_role_distribution", {}), ensure_ascii=False), rec.get("avg_export_confidence"), rec.get("avg_residual_uncertainty"), rec.get("board_export_state"), rec.get("board_export_result"),
            rec.get("dominant_orbit"), rec.get("dominant_manybody_role"), json.dumps(rec.get("private_condensate_sources", []), ensure_ascii=False), rec.get("aggregation_model"), json.dumps(rec.get("condensed_half_conclusion", {}), ensure_ascii=False)
        ) for rec in registry_payload.get("records", [])]
    )
    cur.executemany("INSERT INTO subsystem_sync_report (key, value_json) VALUES (?, ?)", [(k, json.dumps(v, ensure_ascii=False)) for k, v in report_payload.items()])
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM subsystem_sync").fetchone()[0]
    conn.close()
    return count


def write_edges_db(db_path: Path, edges: list[dict[str, Any]]) -> int:
    conn = recreate(db_path)
    cur = conn.cursor()
    cur.executescript("CREATE TABLE edges (source TEXT NOT NULL, target TEXT NOT NULL, relation TEXT NOT NULL, weight REAL, PRIMARY KEY (source, target, relation));")
    cur.executemany("INSERT INTO edges (source, target, relation, weight) VALUES (?, ?, ?, ?)", [(e.get("source"), e.get("target"), e.get("relation"), e.get("weight")) for e in edges])
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    conn.close()
    return count


def write_reports_db(db_path: Path, report_payloads: dict[str, Any], orbit_counts: dict[str, int]) -> int:
    conn = recreate(db_path)
    cur = conn.cursor()
    cur.executescript("CREATE TABLE reports (name TEXT PRIMARY KEY, payload_json TEXT NOT NULL); CREATE TABLE orbit_counts (orbital_role TEXT PRIMARY KEY, count INTEGER NOT NULL);")
    cur.executemany("INSERT INTO reports (name, payload_json) VALUES (?, ?)", [(name, json.dumps(payload, ensure_ascii=False)) for name, payload in report_payloads.items()])
    cur.executemany("INSERT INTO orbit_counts (orbital_role, count) VALUES (?, ?)", list(orbit_counts.items()))
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    conn.close()
    return count


def derive_orbit_counts(records: list[dict[str, Any]], fallback: dict[str, int]) -> dict[str, int]:
    if fallback:
        return fallback
    counts: dict[str, int] = {}
    for rec in records:
        role = str(rec.get("orbital_role") or "unknown")
        counts[role] = counts.get(role, 0) + 1
    return counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    base = repo_root / "integration" / "registries" / "definitions"
    db_dir = base / "db_library"
    db_dir.mkdir(parents=True, exist_ok=True)

    reg = load_json(base / "orbital_definition_registry.json")
    internal_reg = load_json_if_exists(base / "internal_subsystem_cards.json", {"schema": "ciel/internal-subsystem-card-registry/v0.3", "internal_card_schema": "ciel/internal-subsystem-card/v0.3", "internal_cards": []})
    policy_reg = load_json_if_exists(base / "horizon_policy_matrix.json", {"schema": "ciel/horizon-policy-matrix/v0.1", "classes": {}})
    sync_reg = load_json_if_exists(base / "subsystem_sync_registry.json", {"schema": "ciel/subsystem-sync-registry/v0.1", "count": 0, "records": []})
    sync_report = load_json_if_exists(base / "subsystem_sync_report.json", {"schema": "ciel/subsystem-sync-report/v0.1", "board_count": 0, "avg_members_per_board": 0.0, "sync_scope_counts": {}, "sync_law_counts": {}, "condensation_operator_counts": {}, "tau_orbit_count": 0, "tau_system_count": 0})
    edges_payload = load_json_if_exists(base / "nonlocal_definition_edges.json", {"schema": "ciel/nonlocal-definition-edges/v0.1", "count": 0, "edges": []})
    report = load_json_if_exists(base / "orbital_assignment_report.json", {"schema": "ciel/orbital-assignment-report/v0.5", "orbit_counts": {}})

    records_db = db_dir / "records.sqlite"
    internal_cards_db = db_dir / "internal_cards.sqlite"
    horizon_policies_db = db_dir / "horizon_policies.sqlite"
    subsystem_sync_db = db_dir / "subsystem_sync.sqlite"
    reports_db = db_dir / "reports.sqlite"

    edge_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges_payload.get("edges", []):
        edge_groups[edge.get("relation", "unknown")].append(edge)

    record_count = write_records_db(records_db, reg.get("records", []))
    internal_card_count = write_internal_cards_db(internal_cards_db, internal_reg.get("internal_cards", []))
    policy_count = write_policy_db(horizon_policies_db, policy_reg)
    sync_count = write_subsystem_sync_db(subsystem_sync_db, sync_reg, sync_report)

    edge_db_meta: dict[str, Any] = {}
    total_edge_rows = 0
    for relation, relation_edges in sorted(edge_groups.items()):
        relation_db = db_dir / f"edges_{relation}.sqlite"
        relation_count = write_edges_db(relation_db, relation_edges)
        total_edge_rows += relation_count
        edge_db_meta[relation] = {"path": repo_relative(repo_root, relation_db), "rows": relation_count, "size_bytes": relation_db.stat().st_size, "tables": ["edges"], "relation": relation}

    orbit_counts = derive_orbit_counts(reg.get("records", []), report.get("orbit_counts", {}))
    report_count = write_reports_db(
        reports_db,
        {
            "orbital_assignment_report": report,
            "subsystem_sync_report": sync_report,
            "db_library_manifest_stub": {"schema": "ciel/catalog-db-library/v0.7", "subsystem_sync_db": repo_relative(repo_root, subsystem_sync_db)},
        },
        orbit_counts,
    )

    manifest = {
        "schema": "ciel/catalog-db-library/v0.7",
        "card_schema": reg.get("card_schema", "ciel/orbital-export-card/v0.5"),
        "internal_card_schema": internal_reg.get("internal_card_schema", "ciel/internal-subsystem-card/v0.3"),
        "sync_schema": sync_reg.get("schema", "ciel/subsystem-sync-registry/v0.1"),
        "databases": {
            "records": {"path": repo_relative(repo_root, records_db), "rows": record_count},
            "internal_cards": {"path": repo_relative(repo_root, internal_cards_db), "rows": internal_card_count},
            "horizon_policies": {"path": repo_relative(repo_root, horizon_policies_db), "rows": policy_count},
            "subsystem_sync": {"path": repo_relative(repo_root, subsystem_sync_db), "rows": sync_count},
            "reports": {"path": repo_relative(repo_root, reports_db), "rows": report_count},
            "edge_shards": edge_db_meta,
        },
        "totals": {"records": record_count, "internal_cards": internal_card_count, "horizon_policies": policy_count, "subsystem_sync": sync_count, "edges": total_edge_rows, "edge_relations": len(edge_db_meta)},
        "reports": {"subsystem_sync_registry": repo_relative(repo_root, base / "subsystem_sync_registry.json"), "subsystem_sync_report": repo_relative(repo_root, base / "subsystem_sync_report.json")},
    }
    (db_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
