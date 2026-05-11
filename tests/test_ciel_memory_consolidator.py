from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

import scripts.ciel_memory_consolidator as consolidator


def test_score_consolidation_penalizes_empty_fields() -> None:
    parsed = {"themes": [], "affect": "unknown", "essence": "", "hunch": ""}
    score, issues = consolidator._score_consolidation(parsed, "sample content with enough words", "raw prompt")
    assert score < 0.6
    assert "affect_unknown" in issues
    assert "essence_empty" in issues
    assert "hunch_empty" in issues


def test_reconsolidation_prompt_mentions_previous_issues() -> None:
    prompt = consolidator._reconsolidation_prompt("content here", "previous raw", ["essence_empty"])
    assert "essence_empty" in prompt
    assert "Popraw poprzednią konsolidację pamięci" in prompt


def test_audit_consolidations_requeues_low_quality_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mem_root = tmp_path / "CIEL_memories"
    local_test = mem_root / "local_test"
    local_test.mkdir(parents=True, exist_ok=True)
    db_path = local_test / "consolidator.db"

    monkeypatch.setattr(consolidator, "MEMORIES_DIR", mem_root)
    monkeypatch.setattr(consolidator, "LOCAL_TEST", local_test)
    monkeypatch.setattr(consolidator, "DB_PATH", db_path)
    monkeypatch.setattr(consolidator, "MIRROR_DIR", local_test / "mirror")

    consolidator.init_db()
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            "INSERT INTO files (path, mtime, size_bytes, source_type, first_seen, processed_at, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("sample.md", 1.0, 10, "journal", "2026-05-11T00:00:00Z", "2026-05-11T00:00:00Z", "done"),
        )
        conn.execute(
            "INSERT INTO consolidations "
            "(ts, file_path, cycle, themes, affect, essence, hunch, latency_s, model, raw_response, "
            "quality_score, quality_issues, reconsolidation_count, review_status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "2026-05-11T00:00:00Z",
                "sample.md",
                1,
                json.dumps([], ensure_ascii=False),
                "unknown",
                "",
                "",
                0.1,
                "gemma-3-1b-ciel",
                "raw",
                0.2,
                json.dumps(["essence_empty"], ensure_ascii=False),
                0,
                "done",
            ),
        )
        conn.commit()

    result = consolidator.audit_consolidations(limit=10)
    assert result["requeued"] == 1

    with sqlite3.connect(str(db_path)) as conn:
        status = conn.execute("SELECT status FROM files WHERE path=?", ("sample.md",)).fetchone()[0]
        review_status = conn.execute(
            "SELECT review_status FROM consolidations WHERE file_path=? ORDER BY id DESC LIMIT 1",
            ("sample.md",),
        ).fetchone()[0]

    assert status == "pending"
    assert review_status == "requeue"


def test_scan_and_register_files_includes_jokeheal_scars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mem_root = tmp_path / "CIEL_memories"
    local_test = mem_root / "local_test"
    jokeheal_dir = mem_root / "jokeheal"
    local_test.mkdir(parents=True, exist_ok=True)
    jokeheal_dir.mkdir(parents=True, exist_ok=True)
    db_path = local_test / "consolidator.db"
    scar_path = jokeheal_dir / "jokeheal_scars.jsonl"
    scar_path.write_text('{"schema":"ciel/jokeheal-scar/v0.1"}\n', encoding="utf-8")

    monkeypatch.setattr(consolidator, "MEMORIES_DIR", mem_root)
    monkeypatch.setattr(consolidator, "LOCAL_TEST", local_test)
    monkeypatch.setattr(consolidator, "DB_PATH", db_path)
    monkeypatch.setattr(consolidator, "MIRROR_DIR", local_test / "mirror")
    monkeypatch.setattr(
        consolidator,
        "SCAN_SOURCES",
        [mem_root / "jokeheal" / "jokeheal_scars.jsonl"],
    )
    monkeypatch.setattr(consolidator, "SCAN_DIRS", [])

    consolidator.init_db()
    new_count, changed_count = consolidator.scan_and_register_files()

    assert new_count == 1
    assert changed_count == 0

    with sqlite3.connect(str(db_path)) as conn:
        source_type = conn.execute("SELECT source_type FROM files WHERE path=?", (str(scar_path),)).fetchone()[0]

    assert source_type == "jokeheal"
