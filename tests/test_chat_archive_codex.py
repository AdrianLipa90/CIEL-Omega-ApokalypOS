from __future__ import annotations

from pathlib import Path

from ciel_sot_agent import chat_archive


def test_codex_source_uses_dedicated_raw_logs_subtree(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(chat_archive, "_MEMORIES_BASE", tmp_path)
    monkeypatch.setattr(chat_archive, "_RAW_LOGS", tmp_path / "raw_logs")
    monkeypatch.setattr(chat_archive, "_DB_PATH", tmp_path / "memories_index.db")
    monkeypatch.setattr(chat_archive, "_session_file", {})

    path = chat_archive.open_session(source="codex", session_id="sess-1")

    assert path.exists()
    assert "/raw_logs/codex/" in str(path)
    assert path.name.endswith("_codex.md")
