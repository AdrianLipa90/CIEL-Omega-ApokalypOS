from __future__ import annotations

import scripts.ciel_subconscious as sub


def test_parse_returns_calibration_metadata_for_structured_output() -> None:
    result = sub._parse("AFFECT: calm\nCONCEPT: memory\nIMPULSE: stay consistent")
    assert result["affect"] == "calm"
    assert result["concept"] == "memory"
    assert result["impulse"] == "stay consistent"
    assert result["mode"] == "structured"
    assert result["confidence"] >= 0.95
    assert result["flags"] == []


def test_parse_marks_freeform_fallback_and_low_confidence() -> None:
    result = sub._parse("build wobbles under repeated failure")
    assert result["mode"] == "freeform"
    assert result["confidence"] < 0.95
    assert "freeform_fallback" in result["flags"]


def test_empty_backend_reports_low_confidence() -> None:
    result = sub._empty(ok=False, note="llama_cpp unavailable")
    assert result["confidence"] == 0.0
    assert result["mode"] == "empty"
    assert "backend_unavailable" in result["flags"]
