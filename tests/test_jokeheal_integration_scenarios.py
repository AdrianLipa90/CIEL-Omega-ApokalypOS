from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.ciel_sot_agent import jokeheal_atlas as atlas_mod
from src.ciel_sot_agent import noema_sot
from src.ciel_sot_agent.cielingo_bridge import build_lingo_frame


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def test_scenario_1_mnemonic_recurrence_feeds_cielingo(tmp_path: Path, monkeypatch) -> None:
    now = datetime.now(timezone.utc).timestamp()
    scar_path = tmp_path / "jokeheal_scars.jsonl"
    rows = [
        {
            "timestamp": now,
            "symbolic_object": "renal_obelisk",
            "tags": ["pain", "mnemonic"],
            "closure_score": 0.22,
            "residual_tension": 0.61,
            "mnemonic_likely": True,
            "boundary_level": "watch",
        },
        {
            "timestamp": now,
            "symbolic_object": "renal_obelisk",
            "tags": ["pain", "mnemonic"],
            "closure_score": 0.28,
            "residual_tension": 0.52,
            "mnemonic_likely": True,
            "boundary_level": "watch",
        },
    ]
    _write_rows(scar_path, rows)
    monkeypatch.setattr(atlas_mod, "default_scar_path", lambda: scar_path)

    frame = build_lingo_frame("here now memory obelisk", ciel_state={"language": "en"})

    assert frame["mnemonic_atlas"]["top_symbolic_objects"][0]["symbolic_object"] == "renal_obelisk"
    assert frame["mnemonic_atlas"]["mnemonic_pressure"] > 0.0
    assert frame["tau_bridge"]["mnemonic_pressure"] > 0.0


def test_scenario_2_literal_alarm_raises_noema_warning(tmp_path: Path, monkeypatch) -> None:
    now = datetime.now(timezone.utc).timestamp()
    scar_path = tmp_path / "jokeheal_scars.jsonl"
    rows = [
        {
            "timestamp": now,
            "symbolic_object": "alarm_object",
            "tags": ["pain", "alarm"],
            "closure_score": 0.05,
            "residual_tension": 0.72,
            "cognitive_tension": 0.81,
            "mnemonic_likely": False,
            "boundary_level": "literal_alarm",
        }
    ]
    _write_rows(scar_path, rows)
    monkeypatch.setattr(noema_sot, "_JOKEHEAL_SCAR_PATH", scar_path)
    monkeypatch.setattr(atlas_mod, "default_scar_path", lambda: scar_path)

    summary = noema_sot._load_jokeheal_summary()
    atlas = atlas_mod.build_mnemonic_atlas()

    assert summary["warning_level"] == "literal_alarm"
    assert summary["literal_alarm_count"] == 1
    assert atlas["literal_alarm_rate"] == 1.0


def test_scenario_3_mixed_scars_raise_symbolic_pull_without_alarm(tmp_path: Path, monkeypatch) -> None:
    now = datetime.now(timezone.utc).timestamp()
    scar_path = tmp_path / "jokeheal_scars.jsonl"
    rows = [
        {
            "timestamp": now,
            "symbolic_object": "soft_tension_knot",
            "tags": ["stress", "memory"],
            "closure_score": 0.31,
            "residual_tension": 0.43,
            "mnemonic_likely": True,
            "boundary_level": "watch",
        },
        {
            "timestamp": now,
            "symbolic_object": "soft_tension_knot",
            "tags": ["stress"],
            "closure_score": 0.35,
            "residual_tension": 0.40,
            "mnemonic_likely": True,
            "boundary_level": "watch",
        },
        {
            "timestamp": now,
            "symbolic_object": "bridge_static",
            "tags": ["stress", "drift"],
            "closure_score": 0.39,
            "residual_tension": 0.38,
            "mnemonic_likely": False,
            "boundary_level": "clear",
        },
    ]
    _write_rows(scar_path, rows)
    monkeypatch.setattr(atlas_mod, "default_scar_path", lambda: scar_path)
    monkeypatch.setattr(noema_sot, "_JOKEHEAL_SCAR_PATH", scar_path)

    atlas = atlas_mod.build_mnemonic_atlas()
    frame = build_lingo_frame("there then stress bridge", ciel_state={"language": "en"})
    summary = noema_sot._load_jokeheal_summary()

    assert atlas["symbolic_pull"] > 0.0
    assert frame["tau_bridge"]["symbolic_pull"] > 0.0
    assert summary["warning_level"] in {"watch", "clear"}
    assert summary["literal_alarm_count"] == 0
