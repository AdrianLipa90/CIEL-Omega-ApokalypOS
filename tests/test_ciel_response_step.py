from __future__ import annotations

from pathlib import Path

import scripts.ciel_response_step as response_step


def test_write_raw_response_log_creates_codex_raw_log(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(response_step, "RAW_LOG_DIR", tmp_path / "raw_logs" / "codex")
    metrics_out = {
        "cycle": 2,
        "identity_phase": 0.2,
        "mean_coherence": 0.9,
        "closure_penalty": 0.15,
        "system_health": 0.75,
        "ethical_score": 0.65,
    }
    sub = {"affect": "calm", "impulse": "stay consistent"}
    response_step._write_raw_response_log("assistant reply", metrics_out, sub, "xyz987")
    files = list((tmp_path / "raw_logs" / "codex").rglob("*_response.md"))
    assert files
    text = files[0].read_text(encoding="utf-8")
    assert "assistant reply" in text
    assert "calm" in text
