from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def default_scar_path() -> Path:
    return Path.home() / "Pulpit" / "CIEL_memories" / "jokeheal" / "jokeheal_scars.jsonl"


def load_scar_rows(path: str | Path | None = None, *, limit: int = 256) -> list[dict[str, Any]]:
    target = Path(path).expanduser() if path else default_scar_path()
    if not target.exists():
        return []
    try:
        lines = [line for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
    except Exception:
        return []
    rows: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def build_mnemonic_atlas(
    path: str | Path | None = None,
    *,
    limit: int = 256,
    recent_hours: float = 72.0,
) -> dict[str, Any]:
    rows = load_scar_rows(path, limit=limit)
    if not rows:
        return {
            "schema": "ciel/jokeheal-mnemonic-atlas/v0.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scar_count": 0,
            "recent_count": 0,
            "top_symbolic_objects": [],
            "top_tags": [],
            "mnemonic_pressure": 0.0,
            "symbolic_pull": 0.0,
            "recurrence_pressure": 0.0,
            "literal_alarm_rate": 0.0,
        }

    now = datetime.now(timezone.utc).timestamp()
    recent_cutoff = recent_hours * 3600.0
    recent = [
        row for row in rows
        if isinstance(row.get("timestamp"), (int, float))
        and now - float(row["timestamp"]) <= recent_cutoff
    ]
    sample = recent or rows[-64:]

    symbolic = Counter(str(row.get("symbolic_object", "")) for row in sample if row.get("symbolic_object"))
    tags = Counter(str(tag) for row in sample for tag in (row.get("tags") or []) if str(tag))
    residuals = [float(row.get("residual_tension", 0.0) or 0.0) for row in sample]
    closures = [float(row.get("closure_score", 0.0) or 0.0) for row in sample]
    mnemonic_flags = [1.0 if row.get("mnemonic_likely") else 0.0 for row in sample]
    literal_flags = [1.0 if row.get("boundary_level") == "literal_alarm" else 0.0 for row in sample]

    unique_symbolic = max(1, len(symbolic))
    total_symbolic = max(1, sum(symbolic.values()))
    recurrence_pressure = 1.0 - min(1.0, unique_symbolic / total_symbolic)
    mnemonic_pressure = min(
        1.0,
        0.40 * (sum(mnemonic_flags) / max(1, len(mnemonic_flags)))
        + 0.35 * (sum(residuals) / max(1, len(residuals)))
        + 0.25 * recurrence_pressure,
    )
    symbolic_pull = min(
        1.0,
        0.45 * recurrence_pressure
        + 0.30 * (1.0 - (sum(closures) / max(1, len(closures))))
        + 0.25 * (sum(residuals) / max(1, len(residuals))),
    )
    literal_alarm_rate = sum(literal_flags) / max(1, len(literal_flags))

    return {
        "schema": "ciel/jokeheal-mnemonic-atlas/v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scar_count": len(rows),
        "recent_count": len(recent),
        "top_symbolic_objects": [{"symbolic_object": key, "count": count} for key, count in symbolic.most_common(8)],
        "top_tags": [{"tag": key, "count": count} for key, count in tags.most_common(8)],
        "mnemonic_pressure": round(float(mnemonic_pressure), 4),
        "symbolic_pull": round(float(symbolic_pull), 4),
        "recurrence_pressure": round(float(recurrence_pressure), 4),
        "literal_alarm_rate": round(float(literal_alarm_rate), 4),
    }
