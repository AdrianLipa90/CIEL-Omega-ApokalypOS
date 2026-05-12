from __future__ import annotations

import types
from pathlib import Path

import scripts.ciel_response_step as response_step


def test_query_sub_direct_uses_inline_backend(monkeypatch) -> None:
    import importlib.util as ilu

    class _Loader:
        def exec_module(self, module) -> None:
            module.query_daemon = lambda text, timeout=2.0: {
                "affect": "[calm]",
                "concept": "[memory]",
                "impulse": "[stay consistent]",
            }

    class _Spec:
        loader = _Loader()

    monkeypatch.setattr(ilu, "spec_from_file_location", lambda *a, **k: _Spec())
    monkeypatch.setattr(ilu, "module_from_spec", lambda spec: types.SimpleNamespace())

    result = response_step.query_sub_direct("hello")
    assert result["affect"] == "calm"
    assert result["concept"] == "memory"
    assert result["impulse"] == "stay consistent"


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
