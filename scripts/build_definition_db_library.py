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
    cur.executescript(
        """
        CREATE TABLE records (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            language TEXT,
            kind TEXT,
            name TEXT,
            qualname TEXT,
            signature TEXT,
            lineno INTEGER,
            end_lineno INTEGER,
            doc TEXT,
            imports_json TEXT,
            calls_json TEXT,
            entrypoint INTEGER,
            card_schema TEXT,
            global_attractor_ref TEXT,
            orbital_role TEXT,
            orbital_confidence REAL,
            semantic_role TEXT,
            container_card_id TEXT,
            subsystem_kind TEXT,
            manybody_role TEXT,
            parent_orbital_role TEXT,
            horizon_id TEXT,
            horizon_class TEXT,
            information_regime TEXT,
            visible_scopes_json TEXT,
            leak_policy TEXT,
            tau_role TEXT,
            lagrange_roles_json TEXT,
            internal_card_id TEXT,
            projection_operator TEXT,
            export_state TEXT,
            export_result TEXT,
            export_confidence REAL,
            residual_uncertainty REAL
        );
        CREATE INDEX idx_records_path ON records(path);
        CREATE INDEX idx_records_kind ON records(kind);
        CREATE INDEX idx_records_name ON records(name);
        CREATE INDEX idx_records_qualname ON records(qualname);
        CREATE INDEX idx_records_orbital_role ON records(orbital_role);
        CREATE INDEX idx_records_semantic_role ON records(semantic_role);
        CREATE INDEX idx_records_container_card_id ON records(container_card_id);
        CREATE INDEX idx_records_horizon_id ON records(horizon_id);
        CREATE INDEX idx_records_information_regime ON records(information_regime);
        CREATE INDEX idx_records_tau_role ON records(tau_role);
        CREATE INDEX idx_records_manybody_role ON records(manybody_role);
        CREATE INDEX idx_records_internal_card_id ON records(internal_card_id);
        CREATE INDEX idx_records_projection_operator ON records(projection_operator);
        CREATE INDEX idx_records_export_state ON records(export_state);
        """
    )
    cur.executemany(
        """
        INSERT INTO records (
            id, path, language, kind, name, qualname, signature, lineno, end_lineno, doc,
            imports_json, calls_json, entrypoint, card_schema, global_attractor_ref, orbital_role,
            orbital_confidence, semantic_role, container_card_id, subsystem_kind, manybody_role,
            parent_orbital_role, horizon_id, horizon_class, information_regime, visible_scopes_json,
            leak_policy, tau_role, lagrange_roles_json, internal_card_id, projection_operator,
            export_state, export_result, export_confidence, residual_uncertainty
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                rec.get("id"), rec.get("path"), rec.get("language"), rec.get("kind"), rec.get("name"),
                rec.get("qualname"), rec.get("signature"), rec.get("lineno"), rec.get("end_lineno"), rec.get("doc"),
                json.dumps(rec.get("imports", []), ensure_ascii=False),
                json.dumps(rec.get("calls", []), ensure_ascii=False),
                1 if rec.get("entrypoint") else 0,
                rec.get("card_schema"), rec.get("global_attractor_ref"), rec.get("orbital_role"),
                rec.get("orbital_confidence"), rec.get("semantic_role"), rec.get("container_card_id"),
                rec.get("subsystem_kind"), rec.get("manybody_role"), rec.get("parent_orbital_role"),
                rec.get("horizon_id"), rec.get("horizon_class"), rec.get("information_regime"),
                json.dumps(rec.get("visible_scopes", []), ensure_ascii=False),
                rec.get("leak_policy"), rec.get("tau_role"), json.dumps(rec.get("lagrange_roles", []), ensure_ascii=False),
                rec.get("internal_card_id"), rec.get("projection_operator"), rec.get("export_state"),
                rec.get("export_result"), rec.get("export_confidence"), rec.get("residual_uncertainty"),
            )
            for rec in records
        ],
    )
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    conn.close()
    return count


def write_internal_cards_db(db_path: Path, records: list[dict[str, Any]]) -> int:
    conn = recreate(db_path)
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE internal_cards (
            internal_card_id TEXT PRIMARY KEY,
            internal_card_schema TEXT,
            owner_card_id TEXT NOT NULL,
            owner_horizon_id TEXT,
            container_card_id TEXT,
            subsystem_kind TEXT,
            manybody_role TEXT,
            internal_visibility TEXT,
            internal_candidate_states_json TEXT,
            internal_conflict_state TEXT,
            internal_superposition_state TEXT,
            internal_resolution_trace_json TEXT,
            internal_tau_local TEXT,
            internal_memory_mode TEXT,
            projection_operator TEXT,
            export_card_id TEXT
        );
        CREATE INDEX idx_internal_owner_card_id ON internal_cards(owner_card_id);
        CREATE INDEX idx_internal_container_card_id ON internal_cards(container_card_id);
        CREATE INDEX idx_internal_visibility ON internal_cards(internal_visibility);
        CREATE INDEX idx_internal_memory_mode ON internal_cards(internal_memory_mode);
        CREATE INDEX idx_internal_conflict_state ON internal_cards(internal_conflict_state);
        CREATE INDEX idx_internal_projection_operator ON internal_cards(projection_operator);
        """
    )
    cur.executemany(
        """
        INSERT INTO internal_cards (
            internal_card_id, internal_card_schema, owner_card_id, owner_horizon_id, container_card_id,
            subsystem_kind, manybody_role, internal_visibility, internal_candidate_states_json,
            internal_conflict_state, internal_superposition_state, internal_resolution_trace_json,
            internal_tau_local, internal_memory_mode, projection_operator, export_card_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                rec.get("internal_card_id"), rec.get("internal_card_schema"), rec.get("owner_card_id"),
                rec.get("owner_horizon_id"), rec.get("container_card_id"), rec.get("subsystem_kind"),
                rec.get("manybody_role"), rec.get("internal_visibility"),
                json.dumps(rec.get("internal_candidate_states", []), ensure_ascii=False),
                rec.get("internal_conflict_state"), rec.get("internal_superposition_state"),
                json.dumps(rec.get("internal_resolution_trace", []), ensure_ascii=False),
                rec.get("internal_tau_local"), rec.get("internal_memory_mode"),
                rec.get("projection_operator"), rec.get("export_card_id"),
            )
            for rec in records
        ],
    )
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM internal_cards").fetchone()[0]
    conn.close()
    return count


def write_edges_db(db_path: Path, edges: list[dict[str, Any]]) -> int:
    conn = recreate(db_path)
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE edges (
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            relation TEXT NOT NULL,
            weight REAL,
            PRIMARY KEY (source, target, relation)
        );
        CREATE INDEX idx_edges_source ON edges(source);
        CREATE INDEX idx_edges_target ON edges(target);
        CREATE INDEX idx_edges_relation ON edges(relation);
        """
    )
    cur.executemany(
        "INSERT INTO edges (source, target, relation, weight) VALUES (?, ?, ?, ?)",
        [(e.get("source"), e.get("target"), e.get("relation"), e.get("weight")) for e in edges],
    )
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    conn.close()
    return count


def write_reports_db(db_path: Path, report_payloads: dict[str, Any], orbit_counts: dict[str, int]) -> int:
    conn = recreate(db_path)
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE reports (
            name TEXT PRIMARY KEY,
            payload_json TEXT NOT NULL
        );
        CREATE TABLE orbit_counts (
            orbital_role TEXT PRIMARY KEY,
            count INTEGER NOT NULL
        );
        """
    )
    cur.executemany(
        "INSERT INTO reports (name, payload_json) VALUES (?, ?)",
        [(name, json.dumps(payload, ensure_ascii=False)) for name, payload in report_payloads.items()],
    )
    cur.executemany(
        "INSERT INTO orbit_counts (orbital_role, count) VALUES (?, ?)",
        list(orbit_counts.items()),
    )
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    conn.close()
    return count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    base = repo_root / "integration" / "registries" / "definitions"
    db_dir = base / "db_library"
    db_dir.mkdir(parents=True, exist_ok=True)

    reg = load_json(base / "orbital_definition_registry.json")
    internal_reg = load_json(base / "internal_subsystem_cards.json")
    edges_payload = load_json(base / "nonlocal_definition_edges.json")
    report = load_json(base / "orbital_assignment_report.json")
    edges = edges_payload["edges"]

    records_db = db_dir / "records.sqlite"
    internal_cards_db = db_dir / "internal_cards.sqlite"
    reports_db = db_dir / "reports.sqlite"
    edge_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        edge_groups[edge.get("relation", "unknown")].append(edge)

    record_count = write_records_db(records_db, reg["records"])
    internal_card_count = write_internal_cards_db(internal_cards_db, internal_reg["internal_cards"])
    edge_db_meta: dict[str, Any] = {}
    total_edge_rows = 0
    for relation, relation_edges in sorted(edge_groups.items()):
        relation_db = db_dir / f"edges_{relation}.sqlite"
        relation_count = write_edges_db(relation_db, relation_edges)
        total_edge_rows += relation_count
        edge_db_meta[relation] = {
            "path": repo_relative(repo_root, relation_db),
            "rows": relation_count,
            "size_bytes": relation_db.stat().st_size,
            "tables": ["edges"],
            "relation": relation,
        }

    report_count = write_reports_db(
        reports_db,
        {
            "orbital_assignment_report": report,
            "db_library_manifest_stub": {
                "schema": "ciel/catalog-db-library/v0.5",
                "records_db": repo_relative(repo_root, records_db),
                "internal_cards_db": repo_relative(repo_root, internal_cards_db),
                "reports_db": repo_relative(repo_root, reports_db),
                "edge_relations": sorted(edge_groups.keys()),
            },
        },
        report.get("orbit_counts", {}),
    )

    manifest = {
        "schema": "ciel/catalog-db-library/v0.5",
        "card_schema": reg.get("card_schema", "ciel/orbital-export-card/v0.3"),
        "internal_card_schema": internal_reg.get("internal_card_schema", "ciel/internal-subsystem-card/v0.1"),
        "databases": {
            "records": {
                "path": repo_relative(repo_root, records_db),
                "rows": record_count,
                "size_bytes": records_db.stat().st_size,
                "tables": ["records"],
                "indexed_fields": [
                    "path", "kind", "name", "qualname", "orbital_role", "semantic_role",
                    "container_card_id", "horizon_id", "information_regime", "tau_role", "manybody_role",
                    "internal_card_id", "projection_operator", "export_state",
                ],
            },
            "internal_cards": {
                "path": repo_relative(repo_root, internal_cards_db),
                "rows": internal_card_count,
                "size_bytes": internal_cards_db.stat().st_size,
                "tables": ["internal_cards"],
                "indexed_fields": [
                    "owner_card_id", "container_card_id", "internal_visibility",
                    "internal_memory_mode", "internal_conflict_state", "projection_operator",
                ],
            },
            "reports": {
                "path": repo_relative(repo_root, reports_db),
                "rows": report_count,
                "size_bytes": reports_db.stat().st_size,
                "tables": ["reports", "orbit_counts"],
            },
            "edge_shards": edge_db_meta,
        },
        "totals": {
            "records": record_count,
            "internal_cards": internal_card_count,
            "edges": total_edge_rows,
            "edge_relations": len(edge_db_meta),
        },
        "reports": {
            "orbital_assignment_report": repo_relative(repo_root, base / "orbital_assignment_report.json"),
            "orbital_registry": repo_relative(repo_root, base / "orbital_definition_registry.json"),
            "internal_card_registry": repo_relative(repo_root, base / "internal_subsystem_cards.json"),
            "edges": repo_relative(repo_root, base / "nonlocal_definition_edges.json"),
        },
    }
    (db_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
