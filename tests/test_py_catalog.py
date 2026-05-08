"""Performance and correctness tests for py_catalog and noema_sot integration.

Tests cover:
  - build speed (< 30s for 600 files)
  - idempotency (second build produces 0 added/removed)
  - tag correctness for known files
  - query filters (level, tag, min_loc)
  - co-occurrence table populated
  - delta tracking
  - noema_sot py_catalog summary present
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from src.ciel_sot_agent.py_catalog import build, query, status, _ROOT, _DB_PATH, _JSON_PATH
from src.ciel_sot_agent.noema_sot import _load_py_catalog_summary, export_to_context, run as noema_run


# ── helpers ──────────────────────────────────────────────────────────────────

def _fresh_build() -> dict:
    return build(_ROOT)


# ── build performance ─────────────────────────────────────────────────────────

class TestBuildPerformance:
    def test_build_completes_under_30s(self):
        t0 = time.perf_counter()
        result = _fresh_build()
        elapsed = time.perf_counter() - t0
        assert elapsed < 30.0, f"build took {elapsed:.1f}s (limit 30s)"
        assert result["total"] > 0

    def test_build_idempotent(self):
        _fresh_build()
        r2 = _fresh_build()
        assert r2["inserted"] == 0, "second build should add 0 new files"
        assert r2["removed"] == 0, "second build should remove 0 files"

    def test_file_count_realistic(self):
        result = _fresh_build()
        assert 400 <= result["total"] <= 1000, \
            f"expected 400-1000 real .py files, got {result['total']}"


# ── tag correctness ───────────────────────────────────────────────────────────

class TestTagCorrectness:
    def setup_method(self):
        _fresh_build()

    def test_orbital_bridge_is_level1_bridge(self):
        rows = query(level=1, tag="bridge")
        paths = [r["path"] for r in rows]
        assert any("orbital_bridge" in p for p in paths), \
            "orbital_bridge.py must be level=1 bridge"

    def test_noema_sot_is_level1_registry(self):
        rows = query(level=1, tag="registry")
        paths = [r["path"] for r in rows]
        assert any("noema_sot" in p for p in paths), \
            "noema_sot.py must be level=1 registry"

    def test_ciel_pipeline_is_executor(self):
        rows = query(tag="executor")
        paths = [r["path"] for r in rows]
        assert any("ciel_pipeline" in p for p in paths), \
            "ciel_pipeline.py must have tag executor"

    def test_tests_are_level4(self):
        rows = query(level=4)
        test_files = [r for r in rows if r["filename"].startswith("test_")]
        assert len(test_files) > 0, "test files must be level 4"

    def test_noema_sot_highest_msem_in_level1(self):
        rows = query(level=1)
        noema = next((r for r in rows if "noema_sot" in r["path"]), None)
        assert noema is not None
        assert noema["M_sem_proxy"] >= 0.95, \
            f"noema_sot M_sem_proxy={noema['M_sem_proxy']} expected >= 0.95"

    def test_lines_of_code_populated(self):
        rows = query(level=1)
        with_loc = [r for r in rows if r["lines_of_code"] and r["lines_of_code"] > 0]
        assert len(with_loc) > 0, "lines_of_code must be populated for level 1 files"

    def test_ciel_pipeline_loc_substantial(self):
        rows = query(tag="executor")
        pipeline = next((r for r in rows if "ciel_pipeline" in r["path"]), None)
        assert pipeline is not None
        assert pipeline["lines_of_code"] > 100, \
            f"ciel_pipeline.py loc={pipeline['lines_of_code']} expected > 100"


# ── query filters ─────────────────────────────────────────────────────────────

class TestQueryFilters:
    def setup_method(self):
        _fresh_build()

    def test_query_by_level(self):
        rows = query(level=1)
        assert all(r["orbital_level"] == 1 for r in rows)
        assert len(rows) > 0

    def test_query_by_tag(self):
        rows = query(tag="memory")
        assert all("memory" in r["tag_what"] for r in rows)

    def test_query_by_subsystem(self):
        rows = query(subsystem="ciel_sot_agent")
        assert all(r["subsystem"] == "ciel_sot_agent" for r in rows)
        assert len(rows) > 10

    def test_query_by_min_loc(self):
        rows = query(min_loc=300)
        assert all(r["lines_of_code"] >= 300 for r in rows)
        assert len(rows) > 0

    def test_query_combined(self):
        rows = query(level=1, min_loc=100)
        assert all(r["orbital_level"] == 1 and r["lines_of_code"] >= 100 for r in rows)


# ── co-occurrence ─────────────────────────────────────────────────────────────

class TestCoOccurrence:
    def setup_method(self):
        _fresh_build()

    def test_cooccurrence_table_populated(self):
        s = status()
        assert len(s["top_cooccurrences"]) > 0, "co-occurrence table must not be empty"

    def test_cooccurrence_mean_msem_valid(self):
        s = status()
        for co in s["top_cooccurrences"]:
            assert 0.0 <= co["mean_M_sem"] <= 1.0, \
                f"mean_M_sem={co['mean_M_sem']} out of range"

    def test_cooccurrence_count_positive(self):
        s = status()
        for co in s["top_cooccurrences"]:
            assert co["count"] > 0


# ── delta tracking ────────────────────────────────────────────────────────────

class TestDelta:
    def test_first_build_records_added(self):
        import sqlite3
        _fresh_build()
        con = sqlite3.connect(_DB_PATH)
        rows = con.execute(
            "SELECT change_type, COUNT(*) FROM py_files_delta "
            "GROUP BY change_type"
        ).fetchall()
        con.close()
        change_types = {r[0] for r in rows}
        assert "added" in change_types, "delta must record 'added' entries on first build"


# ── JSON export ───────────────────────────────────────────────────────────────

class TestJsonExport:
    def setup_method(self):
        _fresh_build()

    def test_json_exists(self):
        assert _JSON_PATH.exists(), f"py_library_index.json not found at {_JSON_PATH}"

    def test_json_structure(self):
        doc = json.loads(_JSON_PATH.read_text(encoding="utf-8"))
        assert "total_files" in doc
        assert "by_level" in doc
        assert "by_what_tag" in doc
        assert "top_cooccurrences" in doc
        assert "entries" in doc
        assert doc["total_files"] == len(doc["entries"])

    def test_json_entries_have_required_fields(self):
        doc = json.loads(_JSON_PATH.read_text(encoding="utf-8"))
        required = {"path", "orbital_level", "M_sem_proxy", "lines_of_code", "tag_what"}
        for entry in doc["entries"][:20]:
            missing = required - entry.keys()
            assert not missing, f"entry missing fields: {missing}"


# ── NOEMA integration ─────────────────────────────────────────────────────────

class TestNoemIntegration:
    def setup_method(self):
        _fresh_build()

    def test_noema_py_summary_loaded(self):
        summary = _load_py_catalog_summary()
        assert summary.get("total", 0) > 0, "NOEMA must load py_catalog summary"
        assert "by_level" in summary
        assert "top_tags" in summary

    def test_noema_context_contains_py_block(self):
        report = noema_run()
        ctx = export_to_context(report)
        assert "py_files" in ctx, "NOEMA context must include py_files line"
        assert "py_top_tags" in ctx, "NOEMA context must include py_top_tags line"

    def test_noema_py_level1_count_matches_query(self):
        summary = _load_py_catalog_summary()
        lv1_from_summary = summary["by_level"].get("1", 0)
        lv1_from_query = len(query(level=1))
        assert lv1_from_summary == lv1_from_query, \
            f"NOEMA summary lv1={lv1_from_summary} != query lv1={lv1_from_query}"
