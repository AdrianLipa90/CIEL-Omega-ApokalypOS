"""py_catalog — SQLite catalog of all .py files in the CIEL system.

Classifies ~600 real .py files using path and filename only (zero content reads).
Four tag dimensions: what / input / output / weight.
Tracks lines_of_code (wc -l), tag co-occurrence graph, and temporal delta.

Usage:
    python -m ciel_sot_agent.py_catalog --build
    python -m ciel_sot_agent.py_catalog --status
    python -m ciel_sot_agent.py_catalog --query --level 1
    python -m ciel_sot_agent.py_catalog --query --tag executor
"""
from __future__ import annotations

import json
import re
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import resolve_project_root

_ROOT = resolve_project_root(__file__)
_DB_PATH   = _ROOT / "integration" / "registries" / "py_catalog.db"
_JSON_PATH = _ROOT / "integration" / "registries" / "py_library_index.json"

_EXCLUDES = ("/.venv/", "/site-packages/", "/__pycache__/")

# ── Orbital level per folder prefix ────────────────────────────────────────

_LEVEL_MAP: list[tuple[str, int]] = [
    ("src/ciel_sot_agent",                           1),
    ("integration/Orbital/main",                     1),
    ("src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega",    2),
    ("src/ciel_geometry",                            2),
    ("src/ciel_rh_control_mini_repo",                2),
    ("src/CIEL_RELATIONAL_MECHANISM_REPO",           3),
    ("src/ciel-omega-demo-main",                     3),
    ("scripts",                                      3),
    ("integration",                                  3),
    ("tests",                                        4),
    ("app",                                          4),
]

def _orbital_level(rel: str) -> int:
    for prefix, lv in _LEVEL_MAP:
        if rel.startswith(prefix):
            return lv
    return 4


# ── M_sem_proxy per file ────────────────────────────────────────────────────

_SUBSYSTEM_MSEM: dict[str, float] = {
    "noema_sot":              0.99,
    "ciel_pipeline":          0.97,
    "orbital_bridge":         0.95,
    "synchronize":            0.91,
    "orch_orbital":           0.88,
    "orbital_db_orchestrator":0.86,
}
_LEVEL_BASE_MSEM = {0: 0.99, 1: 0.90, 2: 0.80, 3: 0.65, 4: 0.35}

def _msem_proxy(rel: str, stem: str, level: int) -> float:
    if "ciel_sot_agent" in rel:
        for key, val in _SUBSYSTEM_MSEM.items():
            if key in stem:
                return val
    if "ciel_geometry" in rel:
        return 0.82
    if rel.startswith("tests"):
        return 0.35
    return _LEVEL_BASE_MSEM.get(level, 0.40)


# ── Tag derivation ──────────────────────────────────────────────────────────

_WHAT_PATTERNS: list[tuple[str, str]] = [
    (r"orbital_bridge|sync_core|synchronize",  "bridge"),
    (r"pipeline|ciel_engine|ciel_pipeline",    "executor"),
    (r"noema|sot|registry|catalog",            "registry"),
    (r"memory|tsm|holonomic|wave",             "memory"),
    (r"affective|emotion|mood|lexicon",        "affective"),
    (r"geometry|disk|braid|phase|poincare",    "algorithm"),
    (r"diagnostics|health|validator|verif",    "diagnostics"),
    (r"^test_",                                "test"),
    (r"build_|generate_|bootstrap|seed_",      "builder"),
    (r"run_|launch|serve|start",               "runner"),
    (r"cli|chat|bench|monitor|gui",            "interface"),
    (r"__init__|paths|setup|conftest",         "config"),
    (r"orch_orbital|orch_",                    "executor"),
    (r"db_orchestrator|state_db|spreadsheet",  "db"),
    (r"satellite|sapiens|audio|relmech",       "satellite"),
    (r"canon|invariant|axiom",                 "constant"),
]

def _tag_what(stem: str, rel: str) -> list[str]:
    tags: list[str] = []
    name = stem.lower()
    for pattern, tag in _WHAT_PATTERNS:
        if re.search(pattern, name) and tag not in tags:
            tags.append(tag)
    if not tags:
        if rel.startswith("tests"):
            tags = ["test"]
        elif rel.startswith("scripts"):
            tags = ["runner"]
        elif "CIEL_OMEGA_COMPLETE_SYSTEM" in rel:
            tags = ["algorithm"]
        else:
            tags = ["support"]
    return tags


def _tag_input(level: int, rel: str) -> list[str]:
    if rel.startswith("scripts/build_") or re.search(r"build_|generate_", rel):
        return ["orbital", "repos"]
    if rel.startswith("scripts/run_"):
        return ["pipeline"]
    _map = {
        1: ["orbital", "repos", "entity"],
        2: ["external", "orbital"],
        3: ["pipeline", "orbital"],
        4: ["none"],
    }
    return _map.get(level, ["none"])


def _tag_output(level: int, rel: str, stem: str) -> list[str]:
    if re.search(r"build_|generate_|seed_|bootstrap", stem.lower()):
        return ["registry", "db"]
    if re.search(r"run_|launch", stem.lower()):
        return ["pipeline"]
    _map = {
        1: ["pipeline", "db"],
        2: ["pipeline"],
        3: ["report", "db"],
        4: ["test", "none"],
    }
    return _map.get(level, ["none"])


def _tag_weight(level: int) -> list[str]:
    return {1: ["core"], 2: ["support"], 3: ["satellite"], 4: ["archive", "test"]}.get(level, ["archive"])


def _subsystem(rel: str) -> str | None:
    if "ciel_sot_agent" in rel:
        return "ciel_sot_agent"
    if "CIEL_OMEGA_COMPLETE_SYSTEM" in rel:
        return "ciel_omega"
    if "ciel_geometry" in rel:
        return "ciel_geometry"
    if "ciel-omega-demo-main" in rel:
        return "ciel_omega_demo"
    if "ciel_rh_control" in rel:
        return "ciel_rh_control"
    return None


# ── File discovery ──────────────────────────────────────────────────────────

def _discover(root: Path) -> list[Path]:
    result = root.rglob("*.py")
    out = []
    for p in result:
        s = str(p)
        if any(ex in s for ex in _EXCLUDES):
            continue
        out.append(p)
    return out


def _count_lines(path: Path) -> int:
    try:
        r = subprocess.run(["wc", "-l", str(path)], capture_output=True, text=True, timeout=5)
        return int(r.stdout.strip().split()[0])
    except Exception:
        return 0


# ── DB schema ───────────────────────────────────────────────────────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS py_files (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    path          TEXT UNIQUE NOT NULL,
    filename      TEXT NOT NULL,
    folder_key    TEXT NOT NULL,
    depth         INTEGER NOT NULL,
    mtime         TEXT,
    size_bytes    INTEGER,
    lines_of_code INTEGER,
    tag_what      TEXT NOT NULL,
    tag_input     TEXT NOT NULL,
    tag_output    TEXT NOT NULL,
    tag_weight    TEXT NOT NULL,
    orbital_level INTEGER NOT NULL,
    M_sem_proxy   REAL NOT NULL,
    subsystem     TEXT,
    noema_id      TEXT
);
CREATE TABLE IF NOT EXISTS tag_cooccurrence (
    tag_a      TEXT NOT NULL,
    tag_b      TEXT NOT NULL,
    count      INTEGER NOT NULL,
    mean_M_sem REAL,
    PRIMARY KEY (tag_a, tag_b)
);
CREATE TABLE IF NOT EXISTS py_files_delta (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    path        TEXT NOT NULL,
    change_type TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_folder ON py_files(folder_key);
CREATE INDEX IF NOT EXISTS idx_level  ON py_files(orbital_level);
CREATE INDEX IF NOT EXISTS idx_msem   ON py_files(M_sem_proxy);
"""


def _open_db() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(_DB_PATH)
    con.executescript(_SCHEMA)
    return con


# ── Co-occurrence ───────────────────────────────────────────────────────────

def _rebuild_cooccurrence(con: sqlite3.Connection) -> None:
    con.execute("DELETE FROM tag_cooccurrence")
    rows = con.execute("SELECT tag_what, M_sem_proxy FROM py_files").fetchall()
    from collections import defaultdict
    pair_count: dict[tuple[str, str], int] = defaultdict(int)
    pair_msem:  dict[tuple[str, str], list[float]] = defaultdict(list)
    for tag_what_json, msem in rows:
        tags = json.loads(tag_what_json)
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                key = (tags[i], tags[j])
                pair_count[key] += 1
                pair_msem[key].append(msem)
    for (a, b), cnt in pair_count.items():
        mean = sum(pair_msem[(a, b)]) / len(pair_msem[(a, b)])
        con.execute(
            "INSERT OR REPLACE INTO tag_cooccurrence VALUES (?,?,?,?)",
            (a, b, cnt, round(mean, 5))
        )
    con.commit()


# ── Build ───────────────────────────────────────────────────────────────────

def build(root: Path | None = None) -> dict[str, Any]:
    root = root or _ROOT
    ts = datetime.now(timezone.utc).isoformat()
    files = _discover(root)

    con = _open_db()
    prev_paths: set[str] = {r[0] for r in con.execute("SELECT path FROM py_files").fetchall()}
    inserted = modified = 0
    seen: set[str] = set()

    for idx, p in enumerate(files, start=1):
        rel = str(p.relative_to(root))
        seen.add(rel)
        stat = p.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        size = stat.st_size
        stem = p.stem
        parts = rel.split("/")
        depth = len(parts)
        folder_key = "/".join(parts[:2]) if depth >= 2 else parts[0]
        level = _orbital_level(rel)
        msem  = _msem_proxy(rel, stem, level)
        noema_id = f"NL-PY-{stem.upper()[:24]}-{idx:04d}"

        tw = json.dumps(_tag_what(stem, rel))
        ti = json.dumps(_tag_input(level, rel))
        to = json.dumps(_tag_output(level, rel, stem))
        tw2 = json.dumps(_tag_weight(level))
        sub = _subsystem(rel)

        loc = _count_lines(p)

        existing = con.execute("SELECT mtime FROM py_files WHERE path=?", (rel,)).fetchone()
        if existing is None:
            con.execute(
                "INSERT OR REPLACE INTO py_files VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (rel, p.name, folder_key, depth, mtime, size, loc, tw, ti, to, tw2, level, msem, sub, noema_id)
            )
            con.execute("INSERT INTO py_files_delta VALUES (NULL,?,?,?)", (ts, rel, "added"))
            inserted += 1
        elif existing[0] != mtime:
            con.execute(
                """UPDATE py_files SET mtime=?,size_bytes=?,lines_of_code=?,
                   tag_what=?,tag_input=?,tag_output=?,tag_weight=?,
                   orbital_level=?,M_sem_proxy=?,subsystem=?,noema_id=?
                   WHERE path=?""",
                (mtime, size, loc, tw, ti, to, tw2, level, msem, sub, noema_id, rel)
            )
            con.execute("INSERT INTO py_files_delta VALUES (NULL,?,?,?)", (ts, rel, "modified"))
            modified += 1

    removed = 0
    for old in prev_paths - seen:
        con.execute("DELETE FROM py_files WHERE path=?", (old,))
        con.execute("INSERT INTO py_files_delta VALUES (NULL,?,?,?)", (ts, old, "removed"))
        removed += 1

    con.commit()
    _rebuild_cooccurrence(con)
    con.close()

    con2 = _open_db()
    total = con2.execute("SELECT COUNT(*) FROM py_files").fetchone()[0]
    con2.close()

    _export_json(root)

    return {
        "ts": ts, "total": total,
        "inserted": inserted, "modified": modified, "removed": removed,
    }


# ── JSON export ─────────────────────────────────────────────────────────────

def _export_json(root: Path) -> None:
    con = _open_db()
    rows = con.execute(
        "SELECT path, orbital_level, M_sem_proxy, lines_of_code, tag_what, subsystem "
        "FROM py_files ORDER BY orbital_level, M_sem_proxy DESC"
    ).fetchall()

    by_level: dict[str, int] = {}
    by_what:  dict[str, int] = {}
    for r in rows:
        lv = str(r[1])
        by_level[lv] = by_level.get(lv, 0) + 1
        for t in json.loads(r[4]):
            by_what[t] = by_what.get(t, 0) + 1

    top_co = con.execute(
        "SELECT tag_a, tag_b, count, mean_M_sem FROM tag_cooccurrence "
        "ORDER BY count DESC LIMIT 10"
    ).fetchall()

    entries = [
        {"path": r[0], "orbital_level": r[1], "M_sem_proxy": r[2],
         "lines_of_code": r[3], "tag_what": json.loads(r[4]), "subsystem": r[5]}
        for r in rows
    ]
    con.close()

    doc = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_files": len(rows),
        "by_level": by_level,
        "by_what_tag": by_what,
        "top_cooccurrences": [
            {"tags": [c[0], c[1]], "count": c[2], "mean_M_sem": c[3]}
            for c in top_co
        ],
        "entries": entries,
    }
    _JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    _JSON_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Query ────────────────────────────────────────────────────────────────────

def query(
    level: int | None = None,
    tag: str | None = None,
    subsystem: str | None = None,
    min_msem: float | None = None,
    max_msem: float | None = None,
    min_loc: int | None = None,
) -> list[dict[str, Any]]:
    con = _open_db()
    clauses, params = [], []
    if level is not None:
        clauses.append("orbital_level = ?")
        params.append(level)
    if subsystem is not None:
        clauses.append("subsystem = ?")
        params.append(subsystem)
    if min_msem is not None:
        clauses.append("M_sem_proxy >= ?")
        params.append(min_msem)
    if max_msem is not None:
        clauses.append("M_sem_proxy <= ?")
        params.append(max_msem)
    if min_loc is not None:
        clauses.append("lines_of_code >= ?")
        params.append(min_loc)
    if tag is not None:
        clauses.append(
            "EXISTS (SELECT 1 FROM json_each(tag_what) WHERE json_each.value = ?)"
        )
        params.append(tag)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT * FROM py_files {where} ORDER BY M_sem_proxy DESC"
    rows = con.execute(sql, params).fetchall()
    cols = [d[0] for d in con.execute(sql, params).description] if rows else []
    con.close()

    # re-run with description
    con2 = _open_db()
    cur = con2.execute(sql, params)
    cols = [d[0] for d in cur.description]
    results = [dict(zip(cols, r)) for r in cur.fetchall()]
    for r in results:
        for k in ("tag_what", "tag_input", "tag_output", "tag_weight"):
            if isinstance(r.get(k), str):
                r[k] = json.loads(r[k])
    con2.close()
    return results


# ── Status ───────────────────────────────────────────────────────────────────

def status() -> dict[str, Any]:
    con = _open_db()
    total = con.execute("SELECT COUNT(*) FROM py_files").fetchone()[0]
    by_level = {str(r[0]): r[1] for r in con.execute(
        "SELECT orbital_level, COUNT(*) FROM py_files GROUP BY orbital_level ORDER BY orbital_level"
    ).fetchall()}
    top_tags: dict[str, int] = {}
    for (tw,) in con.execute("SELECT tag_what FROM py_files").fetchall():
        for t in json.loads(tw):
            top_tags[t] = top_tags.get(t, 0) + 1
    top_co = con.execute(
        "SELECT tag_a, tag_b, count, mean_M_sem FROM tag_cooccurrence ORDER BY count DESC LIMIT 5"
    ).fetchall()
    last_delta = con.execute(
        "SELECT ts, change_type, COUNT(*) FROM py_files_delta GROUP BY ts, change_type ORDER BY ts DESC LIMIT 6"
    ).fetchall()
    con.close()
    return {
        "total_files": total,
        "by_level": by_level,
        "top_what_tags": dict(sorted(top_tags.items(), key=lambda x: -x[1])[:10]),
        "top_cooccurrences": [
            {"tags": [r[0], r[1]], "count": r[2], "mean_M_sem": r[3]} for r in top_co
        ],
        "last_delta": [
            {"ts": r[0][:19], "change_type": r[1], "count": r[2]} for r in last_delta
        ],
    }


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    args = sys.argv[1:]

    if "--build" in args:
        print("Building .py catalog ...", flush=True)
        r = build()
        print(f"  Done: {r['total']} files  "
              f"(+{r['inserted']} added, ~{r['modified']} modified, -{r['removed']} removed)")
        print(f"  DB  : {_DB_PATH}")
        print(f"  JSON: {_JSON_PATH}")

    elif "--status" in args:
        s = status()
        print(f"py_catalog — {s['total_files']} files")
        print("  per level:", s["by_level"])
        print("  top tags :", s["top_what_tags"])
        print("  top co-occurrences:")
        for c in s["top_cooccurrences"]:
            print(f"    {c['tags'][0]} + {c['tags'][1]}  ->  {c['count']}x  (M_sem={c['mean_M_sem']})")
        print("  last delta:")
        for d in s["last_delta"]:
            print(f"    {d['ts']}  {d['change_type']:10s}  {d['count']}")

    elif "--query" in args:
        level = None
        tag   = None
        sub   = None
        min_loc = None
        for i, a in enumerate(args):
            if a == "--level" and i + 1 < len(args):
                level = int(args[i + 1])
            if a == "--tag" and i + 1 < len(args):
                tag = args[i + 1]
            if a == "--subsystem" and i + 1 < len(args):
                sub = args[i + 1]
            if a == "--min-loc" and i + 1 < len(args):
                min_loc = int(args[i + 1])
        results = query(level=level, tag=tag, subsystem=sub, min_loc=min_loc)
        print(f"Results: {len(results)} files")
        for r in results[:20]:
            print(f"  [{r['orbital_level']}] {r['path']:60s}  M={r['M_sem_proxy']:.2f}  "
                  f"loc={r['lines_of_code']}  {r['tag_what']}")
        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more")

    else:
        print("Usage: python -m ciel_sot_agent.py_catalog "
              "[--build | --status | --query [--level N] [--tag TAG] [--subsystem S] [--min-loc N]]")
        sys.exit(1)
