from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.ciel_sot_agent.cielingo_bridge import build_lingo_frame
from src.ciel_sot_agent.jokeheal_atlas import build_mnemonic_atlas


def test_build_mnemonic_atlas_extracts_pressure(tmp_path: Path) -> None:
    path = tmp_path / "jokeheal_scars.jsonl"
    now = datetime.now(timezone.utc).timestamp()
    rows = [
        {
            "timestamp": now,
            "symbolic_object": "renal_obelisk",
            "tags": ["pain", "mnemonic"],
            "closure_score": 0.2,
            "residual_tension": 0.6,
            "mnemonic_likely": True,
            "boundary_level": "watch",
        },
        {
            "timestamp": now,
            "symbolic_object": "renal_obelisk",
            "tags": ["pain"],
            "closure_score": 0.3,
            "residual_tension": 0.5,
            "mnemonic_likely": True,
            "boundary_level": "watch",
        },
    ]
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    atlas = build_mnemonic_atlas(path)

    assert atlas["scar_count"] == 2
    assert atlas["mnemonic_pressure"] > 0.0
    assert atlas["symbolic_pull"] > 0.0
    assert atlas["top_symbolic_objects"][0]["symbolic_object"] == "renal_obelisk"


def test_cielingo_frame_can_consume_mnemonic_atlas(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "jokeheal_scars.jsonl"
    now = datetime.now(timezone.utc).timestamp()
    row = {
        "timestamp": now,
        "symbolic_object": "soft_tension_knot",
        "tags": ["pain", "memory"],
        "closure_score": 0.25,
        "residual_tension": 0.55,
        "mnemonic_likely": True,
        "boundary_level": "watch",
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    from src.ciel_sot_agent import jokeheal_atlas as atlas_mod
    monkeypatch.setattr(atlas_mod, "default_scar_path", lambda: path)

    frame = build_lingo_frame("here now memory knot", ciel_state={"language": "en"})

    assert "mnemonic_atlas" in frame
    assert frame["mnemonic_atlas"]["mnemonic_pressure"] > 0.0
    assert frame["tau_bridge"]["mnemonic_pressure"] > 0.0
    assert "mnemonic_pressure=" in frame["summary"]
