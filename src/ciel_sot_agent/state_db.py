"""Unified SQLite state store for CIEL system.

Single source of truth for: orchestrator state, M0-M8 metrics, JSON reports,
intentions, and metrics history. Replaces scattered pickle + 72 JSON files.

DB location: ~/.claude/ciel_state.db
WAL mode for concurrent read/write safety.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

_DB_PATH = Path.home() / ".claude" / "ciel_state.db"
_SCHEMA_VERSION = 1

_SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS schema_version (
  version INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS orchestrator_state (
  id                  INTEGER PRIMARY KEY,
  cycle_index         INTEGER,
  current_time        REAL,
  identity_phase      REAL,
  dynamics_phases     TEXT,     -- JSON [8 floats]
  dynamics_velocities TEXT,     -- JSON [8 floats]
  loops               TEXT,     -- JSON
  last_eba            TEXT,     -- JSON
  snapshot_at         REAL,
  version             INTEGER DEFAULT 2,
  berry_accumulated    REAL DEFAULT 0.0,
  winding_total        REAL DEFAULT 0.0,
  groove_depth         REAL DEFAULT 0.0,
  winding_subjective   REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS m2_episodes (
  id                  TEXT PRIMARY KEY,
  content             TEXT,
  context             TEXT,     -- JSON
  timestamp           REAL,
  phase_at_storage    REAL,
  salience            REAL,
  identity_impact     REAL,
  consolidation_score REAL,
  promoted_to_semantic INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS m2_ts ON m2_episodes(timestamp);

CREATE TABLE IF NOT EXISTS consolidation_items (
  id                  TEXT PRIMARY KEY,
  channel             INTEGER,  -- 3=semantic,4=procedural,5=affective,6=identity
  item_key            TEXT,
  canonical_text      TEXT,
  phase               REAL,
  confidence          REAL,
  stability           REAL,
  identity_alignment  REAL,
  status              TEXT,     -- active|contested|deprecated
  extra               TEXT,     -- JSON
  created_at          REAL,
  updated_at          REAL
);
CREATE INDEX IF NOT EXISTS ci_channel ON consolidation_items(channel, item_key);
CREATE INDEX IF NOT EXISTS ci_status  ON consolidation_items(status);

CREATE TABLE IF NOT EXISTS m8_audit (
  id          TEXT PRIMARY KEY,
  timestamp   REAL,
  entry_type  TEXT,
  source_ch   INTEGER,
  target_ch   INTEGER,
  description TEXT,
  metadata    TEXT              -- JSON
);
CREATE INDEX IF NOT EXISTS m8_ts ON m8_audit(timestamp DESC);

CREATE TABLE IF NOT EXISTS json_reports (
  report_type  TEXT PRIMARY KEY,
  schema_id    TEXT,
  payload      TEXT,            -- JSON full report
  generated_at REAL
);

CREATE TABLE IF NOT EXISTS intentions (
  id           TEXT PRIMARY KEY,
  priority     TEXT,            -- H|M|L|x
  text         TEXT,
  created_at   TEXT,
  completed_at TEXT
);

CREATE TABLE IF NOT EXISTS word_holonomy (
  word_id               TEXT PRIMARY KEY,
  berry_accumulated     REAL DEFAULT 0.0,
  languages_traversed   INTEGER DEFAULT 0,
  last_traversal        TEXT
);

CREATE TABLE IF NOT EXISTS metrics_history (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp       REAL,
  cycle_index     INTEGER,
  identity_phase  REAL,
  ethical_score   REAL,
  system_health   REAL,
  coherence_index REAL,
  closure_penalty REAL,
  mood            REAL,
  dominant_emotion TEXT
);
CREATE INDEX IF NOT EXISTS mh_ts ON metrics_history(timestamp DESC);
"""


_schema_initialized: set[str] = set()  # db paths already initialized this process


def get_db(path: Path | None = None) -> sqlite3.Connection:
    """Return a WAL-mode connection to the CIEL state database."""
    db_path = path or _DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    if str(db_path) not in _schema_initialized:
        _ensure_schema(conn)
        _schema_initialized.add(str(db_path))
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)
    row = conn.execute("SELECT version FROM schema_version").fetchone()
    if row is None:
        conn.execute("INSERT INTO schema_version VALUES (?)", (_SCHEMA_VERSION,))
        conn.commit()
    # migrate existing DB: add holonomy columns if missing
    existing = {r[1] for r in conn.execute("PRAGMA table_info(orchestrator_state)").fetchall()}
    for col, typedef in [("berry_accumulated", "REAL DEFAULT 0.0"),
                         ("winding_total", "REAL DEFAULT 0.0"),
                         ("groove_depth", "REAL DEFAULT 0.0"),
                         ("winding_subjective", "REAL DEFAULT 0.0")]:
        if col not in existing:
            conn.execute(f"ALTER TABLE orchestrator_state ADD COLUMN {col} {typedef}")
    conn.commit()


# ── Reports ───────────────────────────────────────────────────────────────────

def save_report(report_type: str, payload: dict[str, Any], schema_id: str = "") -> None:
    """Upsert a JSON report into the database."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO json_reports(report_type, schema_id, payload, generated_at)
               VALUES(?,?,?,?)
               ON CONFLICT(report_type) DO UPDATE SET
                 schema_id=excluded.schema_id,
                 payload=excluded.payload,
                 generated_at=excluded.generated_at""",
            (report_type, schema_id, json.dumps(payload, ensure_ascii=False), time.time()),
        )


def load_report(report_type: str) -> dict[str, Any]:
    """Load a JSON report from the database. Returns {} if not found."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT payload FROM json_reports WHERE report_type=?", (report_type,)
        ).fetchone()
    if row is None:
        return {}
    try:
        return json.loads(row["payload"])
    except Exception:
        return {}


def load_report_freshness(report_type: str) -> float | None:
    """Return generated_at timestamp of a report, or None if not found."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT generated_at FROM json_reports WHERE report_type=?", (report_type,)
        ).fetchone()
    return row["generated_at"] if row else None


# ── Metrics history ───────────────────────────────────────────────────────────

def append_metrics(
    *,
    cycle_index: int,
    identity_phase: float,
    ethical_score: float = 0.0,
    system_health: float = 0.0,
    coherence_index: float = 0.0,
    closure_penalty: float = 0.0,
    mood: float = 0.0,
    dominant_emotion: str = "",
) -> None:
    """Append a metrics snapshot to history."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO metrics_history
               (timestamp, cycle_index, identity_phase, ethical_score, system_health,
                coherence_index, closure_penalty, mood, dominant_emotion)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (
                time.time(), cycle_index, identity_phase, ethical_score,
                system_health, coherence_index, closure_penalty, mood, dominant_emotion,
            ),
        )


def load_metrics_history(limit: int = 100) -> list[dict[str, Any]]:
    """Return recent metrics snapshots, newest first."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM metrics_history ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# ── Orchestrator state ────────────────────────────────────────────────────────

def save_orchestrator_state(state: dict[str, Any]) -> None:
    """Upsert orchestrator state (id=1 as singleton row)."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO orchestrator_state
               (id, cycle_index, current_time, identity_phase,
                dynamics_phases, dynamics_velocities, loops, last_eba,
                snapshot_at, version, berry_accumulated, winding_total, groove_depth)
               VALUES(1,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 cycle_index=excluded.cycle_index,
                 current_time=excluded.current_time,
                 identity_phase=excluded.identity_phase,
                 dynamics_phases=excluded.dynamics_phases,
                 dynamics_velocities=excluded.dynamics_velocities,
                 loops=excluded.loops,
                 last_eba=excluded.last_eba,
                 snapshot_at=excluded.snapshot_at,
                 version=excluded.version,
                 berry_accumulated=excluded.berry_accumulated,
                 winding_total=excluded.winding_total,
                 groove_depth=excluded.groove_depth""",
            (
                state.get("cycle_index", 0),
                state.get("current_time", 0.0),
                state.get("identity_phase", 0.0),
                json.dumps(state.get("dynamics_phases", [])),
                json.dumps(state.get("dynamics_velocities", [])),
                json.dumps(state.get("loops", {})),
                json.dumps(state.get("last_eba", {})),
                time.time(),
                state.get("version", 2),
                state.get("berry_accumulated", 0.0),
                state.get("winding_total", 0.0),
                state.get("groove_depth", 0.0),
            ),
        )


def load_orchestrator_state() -> dict[str, Any] | None:
    """Load orchestrator state. Returns None if not yet saved."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM orchestrator_state WHERE id=1"
        ).fetchone()
    if row is None:
        return None
    d = dict(row)
    for key in ("dynamics_phases", "dynamics_velocities", "loops", "last_eba"):
        try:
            d[key] = json.loads(d[key]) if d[key] else {}
        except Exception:
            d[key] = {}
    return d


# ── Holonomy accumulation ─────────────────────────────────────────────────────

def load_holonomy() -> dict[str, float]:
    """Load accumulated holonomy state. Returns zeros if not yet saved."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT berry_accumulated, winding_total, groove_depth, winding_subjective "
            "FROM orchestrator_state WHERE id=1"
        ).fetchone()
    if row is None:
        return {"berry_accumulated": 0.0, "winding_total": 0.0, "groove_depth": 0.0, "winding_subjective": 0.0}
    return {
        "berry_accumulated": float(row["berry_accumulated"] or 0.0),
        "winding_total": float(row["winding_total"] or 0.0),
        "groove_depth": float(row["groove_depth"] or 0.0),
        "winding_subjective": float(row["winding_subjective"] or 0.0),
    }


def accumulate_berry(phi_berry_delta: float, groove_delta: float) -> dict[str, float]:
    """Add phi_berry_delta to accumulated holonomy. Returns updated state."""
    import math
    prev = load_holonomy()
    berry_new = prev["berry_accumulated"] + phi_berry_delta
    winding_new = berry_new / (2 * math.pi)
    groove_new = prev["groove_depth"] + groove_delta
    with get_db() as conn:
        conn.execute(
            """UPDATE orchestrator_state
               SET berry_accumulated=?, winding_total=?, groove_depth=?
               WHERE id=1""",
            (berry_new, winding_new, groove_new),
        )
        if conn.execute("SELECT changes()").fetchone()[0] == 0:
            conn.execute(
                """INSERT OR IGNORE INTO orchestrator_state
                   (id, berry_accumulated, winding_total, groove_depth)
                   VALUES(1, ?, ?, ?)""",
                (berry_new, winding_new, groove_new),
            )
    return {"berry_accumulated": berry_new, "winding_total": winding_new, "groove_depth": groove_new}


def accumulate_subjective_winding(winding_delta: float) -> dict[str, float]:
    """Accumulate subjective winding (P3 Δτ-weighted) by winding_delta per cycle."""
    prev = load_holonomy()
    new_val = prev["winding_subjective"] + winding_delta
    with get_db() as conn:
        conn.execute(
            "UPDATE orchestrator_state SET winding_subjective=? WHERE id=1",
            (new_val,),
        )
        if conn.execute("SELECT changes()").fetchone()[0] == 0:
            conn.execute(
                "INSERT OR IGNORE INTO orchestrator_state (id, winding_subjective) VALUES(1, ?)",
                (new_val,),
            )
    return {**prev, "winding_subjective": new_val}


# ── M8 Audit ──────────────────────────────────────────────────────────────────

def append_audit(
    entry_id: str,
    entry_type: str,
    description: str,
    source_ch: int | None = None,
    target_ch: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Append an M8 audit journal entry."""
    with get_db() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO m8_audit
               (id, timestamp, entry_type, source_ch, target_ch, description, metadata)
               VALUES(?,?,?,?,?,?,?)""",
            (
                entry_id, time.time(), entry_type, source_ch, target_ch,
                description, json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )


# ── Batch write (single transaction) ─────────────────────────────────────────

def _read_cycle_from_pickle() -> int:
    """Read cycle_index — prefers SQLite metrics_history, falls back to pickle."""
    try:
        with get_db() as conn:
            row = conn.execute(
                "SELECT cycle_index FROM metrics_history ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()
        if row and row["cycle_index"]:
            return int(row["cycle_index"])
    except Exception:
        pass
    import pickle
    for p in [str(Path.home() / 'Pulpit/CIEL_memories/state/ciel_orch_state.pkl'),
              str(Path.home() / '.claude/ciel_orch_state.pkl')]:
        try:
            with open(p, 'rb') as f:
                orch = pickle.load(f)
            return int(getattr(orch, 'cycle_index', 0))
        except Exception:
            continue
    return 0


def save_bridge_snapshot(
    summary: dict[str, Any],
    runtime_gating: dict[str, Any],
    health_manifest: dict[str, Any],
    state_manifest: dict[str, Any],
    ciel_pipe: dict[str, Any],
) -> None:
    """Write all orbital bridge data in a single SQLite transaction.

    Replaces multiple save_report() + append_metrics() calls (each with its own
    COMMIT) with one atomic write. Critical for performance — each COMMIT on WAL
    SQLite takes ~700ms on this machine.
    """
    import time as _time
    now = _time.time()
    cycle = int(ciel_pipe.get('cycle_index', 0)) or _read_cycle_from_pickle()
    metrics_row = (
        now,
        cycle,
        float(ciel_pipe.get('identity_phase', 0.0)),
        float(ciel_pipe.get('ethical_score', 0.0)),
        float(health_manifest.get('system_health', 0.0)),
        float(state_manifest.get('coherence_index', 0.0)),
        float(health_manifest.get('closure_penalty', 0.0)),
        float(ciel_pipe.get('mood', 0.0)),
        str(ciel_pipe.get('dominant_emotion', '')),
    )
    summary_json = json.dumps(summary, ensure_ascii=False)
    gating_json  = json.dumps(runtime_gating, ensure_ascii=False)

    conn = get_db()
    try:
        conn.execute("BEGIN")
        conn.execute(
            """INSERT INTO json_reports(report_type, schema_id, payload, generated_at)
               VALUES('orbital_bridge',?,?,?)
               ON CONFLICT(report_type) DO UPDATE SET
                 schema_id=excluded.schema_id, payload=excluded.payload,
                 generated_at=excluded.generated_at""",
            (summary.get('schema', ''), summary_json, now),
        )
        conn.execute(
            """INSERT INTO json_reports(report_type, schema_id, payload, generated_at)
               VALUES('runtime_gating',?,?,?)
               ON CONFLICT(report_type) DO UPDATE SET
                 schema_id=excluded.schema_id, payload=excluded.payload,
                 generated_at=excluded.generated_at""",
            (runtime_gating.get('schema', ''), gating_json, now),
        )
        conn.execute(
            """INSERT INTO metrics_history
               (timestamp, cycle_index, identity_phase, ethical_score, system_health,
                coherence_index, closure_penalty, mood, dominant_emotion)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            metrics_row,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Convenience ───────────────────────────────────────────────────────────────

def db_path() -> Path:
    return _DB_PATH
