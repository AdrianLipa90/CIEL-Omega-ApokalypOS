from __future__ import annotations

from pathlib import Path

from scripts.ciel_message_step import _prompt_metrics_payload
import scripts.ciel_message_step as message_step


def test_prompt_metrics_payload_embeds_ciel_metrics() -> None:
    metrics = {
        "cycle": 12,
        "cycle_index": 34,
        "identity_phase": 0.12,
        "mean_coherence": 0.89,
        "closure_penalty": 0.21,
        "system_health": 0.55,
        "ethical_score": 0.62,
        "soul_invariant": 0.81,
        "dominant_emotion": "calm",
        "sub_affect": "focused",
        "sub_impulse": "keep the build stable",
        "sub_latency": 1.23,
        "m2_episodes": 7,
        "m3_items": 9,
        "m8_entries": 11,
        "mode": "standard",
    }
    payload = _prompt_metrics_payload("hello prompt", metrics, session_id="sess-1")

    assert payload["session_id"] == "sess-1"
    assert payload["prompt_excerpt"] == "hello prompt"
    assert payload["metrics"]["closure_penalty"] == 0.21
    assert payload["metrics"]["soul_invariant"] == 0.81
    assert payload["metrics"]["sub_affect"] == "focused"


def test_write_raw_prompt_log_creates_codex_raw_log(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(message_step, "RAW_LOG_DIR", tmp_path / "raw_logs" / "codex")
    metrics = {"cycle": 1, "identity_phase": 0.1, "mean_coherence": 0.8, "closure_penalty": 0.2, "system_health": 0.7, "ethical_score": 0.6}
    message_step._write_raw_prompt_log("hello raw", metrics, session_id="abc123")
    files = list((tmp_path / "raw_logs" / "codex").rglob("*.md"))
    assert files
    assert "hello raw" in files[0].read_text(encoding="utf-8")
