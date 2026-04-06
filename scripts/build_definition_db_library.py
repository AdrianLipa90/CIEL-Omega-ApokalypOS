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
            orbital_role TEXT,
            orbital_confidence REAL,
            semantic_role TEXT
        );
        CREATE INDEX idx_records_path ON records(path);
        CREATE INDEX idx_records_kind ON records(kind);
        CREATE INDEX idx_records_name ON records(name);
        CREATE INDEX idx_records_qualname ON records(qualname);
        CREATE INDEX idx_records_orbital_role ON records(orbital_role);
        CREATE INDEX idx_records_semantic_role ON records(semantic_role);
        """
    )
    cur.executemany(
        """
        INSERT INTO records (
            id, path, language, kind, name, qualname, signature, lineno, end_lineno, doc,
            imports_json, calls_json, entrypoint, orbital_role, orbital_confidence, semantic_role
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                rec.get("id"), rec.get("path"), rec.get("language"), rec.get("kind"), rec.get("name"),
                rec.get("qualname"), rec.get("signature"), rec.get("lineno"), rec.get("end_lineno"), rec.get("doc"),
                json.dumps(rec.get("imports", []), ensure_ascii=False),
                json.dumps(rec.get("calls", []), ensure_ascii=False),
                1 if rec.get("entrypoint") else 0,
                rec.get("orbital_role"), rec.get("orbital_confidence"), rec.get("semantic_role"),
            )
            for rec in records
        ],
    )
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM records").fetchone()[0]
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
    edges_payload = load_json(base / "nonlocal_definition_edges.json")
    report = load_json(base / "orbital_assignment_report.json")
    edges = edges_payload["edges"]

    records_db = db_dir / "records.sqlite"
    reports_db = db_dir / "reports.sqlite"
    edge_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        edge_groups[edge.get("relation", "unknown")].append(edge)

    record_count = write_records_db(records_db, reg["records"])
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
                "schema": "ciel/catalog-db-library/v0.3",
                "records_db": repo_relative(repo_root, records_db),
                "reports_db": repo_relative(repo_root, reports_db),
                "edge_relations": sorted(edge_groups.keys()),
            },
        },
        report.get("orbit_counts", {}),
    )

    manifest = {
        "schema": "ciel/catalog-db-library/v0.3",
        "databases": {
            "records": {
                "path": repo_relative(repo_root, records_db),
                "rows": record_count,
                "size_bytes": records_db.stat().st_size,
                "tables": ["records"],
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
            "edges": total_edge_rows,
            "edge_relations": len(edge_db_meta),
        },
        "reports": {
            "orbital_assignment_report": repo_relative(repo_root, base / "orbital_assignment_report.json"),
            "orbital_registry": repo_relative(repo_root, base / "orbital_definition_registry.json"),
            "edges": repo_relative(repo_root, base / "nonlocal_definition_edges.json"),
        },
    }
    (db_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
