from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.jokeheal.scar_writer import build_scar_record
from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.jokeheal.protocol import TensionInput
from src.ciel_sot_agent import noema_sot


def test_jokeheal_summary_reports_literal_alarm(tmp_path: Path, monkeypatch) -> None:
    scar_path = tmp_path / "jokeheal" / "jokeheal_scars.jsonl"
    scar_path.parent.mkdir(parents=True, exist_ok=True)

    inp = TensionInput(text="sensu stricte test", source="test")
    row = build_scar_record(
        inp,
        "alarm_object",
        {
            "mode": "safety_boundary",
            "humor_dose": 0,
            "boundary_level": "literal_alarm",
            "boundary_literal": True,
            "boundary_reasons": ["literal_marker:sensu_stricte"],
            "closure_score": 0.05,
            "residual_tension": 0.72,
            "cognitive_tension": 0.81,
            "symbolic_density": 0.15,
            "mnemonic_likely": False,
            "pain_overflow": True,
            "tags": ["pain", "alarm"],
        },
    )
    scar_path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    monkeypatch.setattr(noema_sot, "_JOKEHEAL_SCAR_PATH", scar_path)

    summary = noema_sot._load_jokeheal_summary(now_ts=datetime.now(timezone.utc))

    assert summary["warning_level"] == "literal_alarm"
    assert summary["literal_alarm_count"] == 1
    assert summary["top_symbolic_objects"][0]["symbolic_object"] == "alarm_object"

