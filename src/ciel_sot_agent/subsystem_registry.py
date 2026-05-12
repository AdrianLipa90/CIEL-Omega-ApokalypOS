"""SubsystemRegistry — zarządza per-subsystem DB i kartami NOEMA.

Każdy subsystem Poziomu 1 (CORE) dostaje:
  - integration/subsystems/{id}/state.db   — SQLite: metrics, events, config_defaults
  - integration/subsystems/{id}/noema_card.json
  - integration/subsystems/{id}/defaults.json

Usage:
    python -m ciel_sot_agent.subsystem_registry --init-all
    python -m ciel_sot_agent.subsystem_registry --status
"""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import resolve_project_root

_ROOT = resolve_project_root(__file__)
_SUBSYSTEMS_DIR = _ROOT / "integration" / "subsystems"

_SCHEMA_VERSION = "ciel/subsystem-registry/v0.1"

# Definicje kanoniczne subsystemów Poziomu 1
SUBSYSTEM_DEFS: list[dict[str, Any]] = [
    {
        "id": "noema_registry",
        "noema_id": "NL-NOEMA-CORE-0001",
        "name": "NOEMA Registry — Global SoT Matrix",
        "sector_name": "noema_registry",
        "orbital_level": 1,
        "orbital_type": "P",
        "theta": 0.1,
        "M_sem": 0.99,
        "gravity_role": "GLOBAL_SOT_MATRIX",
        "python_module": "noema_sot",
        "input_from": ["all_subsystems"],
        "output_to": ["session_hook", "ciel_pipeline"],
        "key_metrics": ["noema_card_count", "global_coherence", "SoT_version", "tag_matrix_size"],
        "config_defaults": {
            "global_coherence_threshold": ("0.767", "float", "alert"),
            "SoT_version": ("1.0", "str", "version"),
            "tag_matrix_size": ("0", "int", "counter"),
        },
    },
    {
        "id": "ciel_omega_core",
        "noema_id": "NL-OMEGA-CORE-0001",
        "name": "CIEL/Ω Core Pipeline",
        "sector_name": "ciel_omega_core",
        "orbital_level": 1,
        "orbital_type": "F",
        "theta": 0.15,
        "M_sem": 0.97,
        "gravity_role": "CORE_EXECUTOR",
        "python_module": "ciel_pipeline",
        "input_from": ["orbital_bridge_core"],
        "output_to": ["session_output", "memory"],
        "key_metrics": ["ethical_score", "dominant_emotion", "soul_invariant", "lie4_trace"],
        "config_defaults": {
            "ethical_score_min": ("0.4", "float", "alert"),
            "soul_invariant_seed": ("0.0", "float", "state"),
            "lie4_trace_target": ("4.183", "float", "constant"),
        },
    },
    {
        "id": "orbital_bridge_core",
        "noema_id": "NL-BRIDGE-CORE-0001",
        "name": "Orbital Bridge Core",
        "sector_name": "orbital_bridge_core",
        "orbital_level": 1,
        "orbital_type": "F",
        "theta": 0.2,
        "M_sem": 0.95,
        "gravity_role": "CORE_EXECUTOR",
        "python_module": "orbital_bridge",
        "input_from": ["sync_core"],
        "output_to": ["ciel_omega_core"],
        "key_metrics": ["coherence_index", "R_H", "system_health", "closure_penalty", "nonlocal_coherent_fraction"],
        "config_defaults": {
            "coherence_index_min": ("0.767", "float", "alert"),
            "system_health_min": ("0.5", "float", "alert"),
            "closure_penalty_deep": ("0.15", "float", "threshold"),
            "closure_penalty_safe": ("0.35", "float", "threshold"),
        },
    },
    {
        "id": "sync_core",
        "noema_id": "NL-SYNC-CORE-0001",
        "name": "Synchronize Core — Layer 1",
        "sector_name": "sync_core",
        "orbital_level": 1,
        "orbital_type": "F",
        "theta": 0.3,
        "M_sem": 0.91,
        "gravity_role": "CORE_EXECUTOR",
        "python_module": "synchronize",
        "input_from": ["repos", "gh_coupling"],
        "output_to": ["orbital_bridge_core"],
        "key_metrics": ["closure_defect", "repo_tensions_max", "sync_duration_s", "n_repos"],
        "config_defaults": {
            "closure_defect_max": ("0.05", "float", "alert"),
            "repo_tensions_max": ("0.03", "float", "alert"),
            "n_repos_expected": ("5", "int", "constant"),
        },
    },
    {
        "id": "orch_orbital_core",
        "noema_id": "NL-ORCH-CORE-0001",
        "name": "OrchOrbital — Entity Injection Core",
        "sector_name": "orch_orbital_core",
        "orbital_level": 1,
        "orbital_type": "S",
        "theta": 0.35,
        "M_sem": 0.88,
        "gravity_role": "CORE_INJECTOR",
        "python_module": "orch_orbital",
        "input_from": ["ciel_entity_cards"],
        "output_to": ["orbital_bridge_core"],
        "key_metrics": ["entity_count", "mean_entity_defect", "mean_coupling_ciel", "sealed_count"],
        "config_defaults": {
            "entity_coupling_scale": ("0.4", "float", "constant"),
            "anchor_sector": ("bridge", "str", "constant"),
            "entity_mini_pass_steps": ("20", "int", "algorithm"),
        },
    },
    {
        "id": "db_orchestrator",
        "noema_id": "NL-DB-CORE-0001",
        "name": "Orbital DB Orchestrator",
        "sector_name": "db_orchestrator",
        "orbital_level": 1,
        "orbital_type": "S",
        "theta": 0.4,
        "M_sem": 0.86,
        "gravity_role": "CORE_MEMORY",
        "python_module": "orbital_db_orchestrator",
        "input_from": ["all_subsystems"],
        "output_to": ["TSM", "GLOSSARY", "WO"],
        "key_metrics": ["db_ok_count", "tsm_rows", "sync_latency_ms", "total_dbs"],
        "config_defaults": {
            "total_dbs_expected": ("6", "int", "constant"),
            "tsm_msem": ("0.929", "float", "constant"),
            "glossary_msem": ("0.860", "float", "constant"),
        },
    },
]


def _rho_from_theta(theta: float) -> float:
    return math.tanh(math.tan(theta / 2.0 + 1e-9))


def _init_db(db_path: Path, sub: dict[str, Any]) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS metrics (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            ts    TEXT NOT NULL,
            key   TEXT NOT NULL,
            value REAL,
            unit  TEXT DEFAULT '',
            source TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS events (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            ts         TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload    TEXT DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS config_defaults (
            key            TEXT PRIMARY KEY,
            value          TEXT NOT NULL,
            dtype          TEXT DEFAULT 'str',
            subsystem_role TEXT DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_metrics_key ON metrics(key);
        CREATE INDEX IF NOT EXISTS idx_metrics_ts  ON metrics(ts);
    """)
    now = datetime.now(timezone.utc).isoformat()
    for key, (value, dtype, role) in sub.get("config_defaults", {}).items():
        cur.execute(
            "INSERT OR IGNORE INTO config_defaults(key,value,dtype,subsystem_role) VALUES(?,?,?,?)",
            (key, value, dtype, role),
        )
    cur.execute(
        "INSERT INTO events(ts,event_type,payload) VALUES(?,?,?)",
        (now, "init", json.dumps({"subsystem_id": sub["id"], "M_sem": sub["M_sem"]})),
    )
    conn.commit()
    conn.close()


def _write_noema_card(card_path: Path, sub: dict[str, Any]) -> None:
    card = {
        "schema": "ciel/noema-card/v0.1",
        "noema_id": sub["noema_id"],
        "subsystem_id": sub["id"],
        "name": sub["name"],
        "sector_name": sub["sector_name"],
        "orbital_level": sub["orbital_level"],
        "orbital_type": sub["orbital_type"],
        "theta": sub["theta"],
        "rho": round(_rho_from_theta(sub["theta"]), 6),
        "M_sem": sub["M_sem"],
        "gravity_role": sub["gravity_role"],
        "python_module": sub["python_module"],
        "input_from": sub["input_from"],
        "output_to": sub["output_to"],
        "key_metrics": sub["key_metrics"],
        "diagnosis_debt": [],
        "created": datetime.now(timezone.utc).isoformat(),
    }
    card_path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_defaults(defaults_path: Path, sub: dict[str, Any]) -> None:
    defaults = {
        "schema": "ciel/subsystem-defaults/v0.1",
        "subsystem_id": sub["id"],
        "M_sem": sub["M_sem"],
        "orbital_level": sub["orbital_level"],
        "key_metrics": sub["key_metrics"],
        "config": {k: {"value": v, "dtype": dtype, "role": role}
                   for k, (v, dtype, role) in sub.get("config_defaults", {}).items()},
    }
    defaults_path.write_text(json.dumps(defaults, ensure_ascii=False, indent=2), encoding="utf-8")


def init_subsystem(sub: dict[str, Any], force: bool = False) -> Path:
    """Tworzy katalog, state.db, noema_card.json i defaults.json dla subsystemu."""
    sub_dir = _SUBSYSTEMS_DIR / sub["id"]
    sub_dir.mkdir(parents=True, exist_ok=True)

    db_path = sub_dir / "state.db"
    if not db_path.exists() or force:
        _init_db(db_path, sub)

    card_path = sub_dir / "noema_card.json"
    if not card_path.exists() or force:
        _write_noema_card(card_path, sub)

    defaults_path = sub_dir / "defaults.json"
    if not defaults_path.exists() or force:
        _write_defaults(defaults_path, sub)

    return sub_dir


def init_all(force: bool = False) -> list[str]:
    created = []
    for sub in SUBSYSTEM_DEFS:
        init_subsystem(sub, force=force)
        created.append(sub["id"])
    return created


def write_metric(subsystem_id: str, key: str, value: float, unit: str = "", source: str = "") -> None:
    db_path = _SUBSYSTEMS_DIR / subsystem_id / "state.db"
    if not db_path.exists():
        return
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO metrics(ts,key,value,unit,source) VALUES(?,?,?,?,?)",
        (now, key, value, unit, source),
    )
    conn.commit()
    conn.close()


def read_latest_metrics(subsystem_id: str) -> dict[str, float]:
    db_path = _SUBSYSTEMS_DIR / subsystem_id / "state.db"
    if not db_path.exists():
        return {}
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT key, value FROM metrics WHERE ts = (SELECT MAX(ts) FROM metrics m2 WHERE m2.key=metrics.key)"
        " GROUP BY key"
    ).fetchall()
    conn.close()
    return {k: v for k, v in rows}


def status() -> dict[str, Any]:
    result = {}
    for sub in SUBSYSTEM_DEFS:
        sid = sub["id"]
        sub_dir = _SUBSYSTEMS_DIR / sid
        db_path = sub_dir / "state.db"
        card_path = sub_dir / "noema_card.json"
        ok = db_path.exists() and card_path.exists()
        metrics_count = 0
        if db_path.exists():
            conn = sqlite3.connect(db_path)
            metrics_count = conn.execute("SELECT COUNT(*) FROM metrics").fetchone()[0]
            conn.close()
        result[sid] = {
            "ok": ok,
            "M_sem": sub["M_sem"],
            "orbital_level": sub["orbital_level"],
            "noema_id": sub["noema_id"],
            "metrics_rows": metrics_count,
            "db": str(db_path),
        }
    return result


def get_noema_cards() -> list[dict[str, Any]]:
    cards = []
    for sub in SUBSYSTEM_DEFS:
        card_path = _SUBSYSTEMS_DIR / sub["id"] / "noema_card.json"
        if card_path.exists():
            cards.append(json.loads(card_path.read_text(encoding="utf-8")))
    return cards


if __name__ == "__main__":
    import sys
    args = set(sys.argv[1:])

    if "--init-all" in args or not args:
        force = "--force" in args
        created = init_all(force=force)
        print(f"Zainicjowano {len(created)} subsystemów:")
        for s in created:
            print(f"  {s}")

    if "--status" in args:
        st = status()
        print("\nStatus subsystemów:")
        for sid, info in st.items():
            ok_str = "OK" if info["ok"] else "MISSING"
            print(f"  [{ok_str}] {sid:25s} lv={info['orbital_level']} M_sem={info['M_sem']} rows={info['metrics_rows']}")

    sys.exit(0)
