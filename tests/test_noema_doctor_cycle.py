"""Tests for scripts/noema_doctor_cycle.py CLI entry-point."""
from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS_DIR = ROOT / "scripts"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Import the CLI module under test.  The module-level sys.path manipulation
# in the script is benign because SRC is already on the path.
import importlib.util
import types

_spec = importlib.util.spec_from_file_location(
    "noema_doctor_cycle", ROOT / "scripts" / "noema_doctor_cycle.py"
)
assert _spec is not None and _spec.loader is not None
_noema_doctor_cycle: types.ModuleType = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_noema_doctor_cycle)  # type: ignore[union-attr]
main = _noema_doctor_cycle.main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_main(argv: list[str], *, capture_stdout: bool = True) -> tuple[int, str]:
    """Run main() with patched argv and return (exit_code, captured_stdout)."""
    buf = StringIO()
    with patch("sys.argv", ["noema_doctor_cycle.py"] + argv):
        if capture_stdout:
            with patch("sys.stdout", buf):
                code = main()
        else:
            code = main()
    return code, buf.getvalue()


# ---------------------------------------------------------------------------
# Return-code tests
# ---------------------------------------------------------------------------


def test_main_returns_0_for_pass(tmp_path: Path) -> None:
    (tmp_path / "clean.py").write_text("x = 1\n", encoding="utf-8")

    code, _ = _run_main(["--root", str(tmp_path)])

    assert code == 0


def test_main_returns_0_for_warn(tmp_path: Path) -> None:
    # Trigger the medium-severity "rh_pipeline_hook_pending" finding -> WARN
    sot = tmp_path / "src" / "ciel_sot_agent"
    sot.mkdir(parents=True)
    (sot / "rh_pipeline_jfunctional.py").write_text("pass\n", encoding="utf-8")
    (sot / "ciel_pipeline.py").write_text("def run(): pass\n", encoding="utf-8")
    (tmp_path / "patches").mkdir()
    (tmp_path / "patches" / "fix_rh_jfunctional_pipeline_hook.diff").write_text(
        "---\n", encoding="utf-8"
    )

    code, _ = _run_main(["--root", str(tmp_path)])

    assert code == 0


def test_main_returns_1_for_fail(tmp_path: Path) -> None:
    # High-severity inverted_rh_metric_candidate -> FAIL
    (tmp_path / "bad.py").write_text('v = 1 - R_H\n', encoding="utf-8")

    code, _ = _run_main(["--root", str(tmp_path)])

    assert code == 1


def test_main_returns_0_for_empty_directory(tmp_path: Path) -> None:
    code, _ = _run_main(["--root", str(tmp_path)])

    assert code == 0


# ---------------------------------------------------------------------------
# JSON output tests
# ---------------------------------------------------------------------------


def test_main_outputs_valid_json(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")

    _, output = _run_main(["--root", str(tmp_path)])

    data = json.loads(output)
    assert "schema" in data
    assert data["schema"] == "noema-holonomic-doctor/report/v0.1"


def test_main_json_output_contains_status(tmp_path: Path) -> None:
    _, output = _run_main(["--root", str(tmp_path)])

    data = json.loads(output)
    assert data["status"] in {"PASS", "WARN", "FAIL"}


def test_main_json_output_sorted_keys(tmp_path: Path) -> None:
    _, output = _run_main(["--root", str(tmp_path)])

    # JSON should be pretty-printed with sorted keys
    data = json.loads(output)
    keys = list(data.keys())
    assert keys == sorted(keys)


def test_main_json_output_has_findings_list(tmp_path: Path) -> None:
    _, output = _run_main(["--root", str(tmp_path)])

    data = json.loads(output)
    assert isinstance(data["findings"], list)


def test_main_json_output_has_manifest_sample(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")

    _, output = _run_main(["--root", str(tmp_path)])

    data = json.loads(output)
    assert isinstance(data["manifest_sample"], list)
    assert len(data["manifest_sample"]) >= 1


# ---------------------------------------------------------------------------
# --write flag tests
# ---------------------------------------------------------------------------


def test_main_write_flag_creates_report_files(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")

    _run_main(["--root", str(tmp_path), "--write"])

    out_dir = tmp_path / "doctor_reports"
    assert out_dir.is_dir()
    assert list(out_dir.glob("*_doctor.noema.json"))
    assert (out_dir / "CURRENT_DOCTOR.noema.json").exists()


def test_main_no_write_flag_creates_no_report_dir(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")

    _run_main(["--root", str(tmp_path)])

    assert not (tmp_path / "doctor_reports").exists()


def test_main_write_flag_report_json_is_valid(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")

    _run_main(["--root", str(tmp_path), "--write"])

    out_dir = tmp_path / "doctor_reports"
    report_files = list(out_dir.glob("*_doctor.noema.json"))
    assert len(report_files) == 1
    data = json.loads(report_files[0].read_text(encoding="utf-8"))
    assert data["schema"] == "noema-holonomic-doctor/report/v0.1"


# ---------------------------------------------------------------------------
# --report-dir tests
# ---------------------------------------------------------------------------


def test_main_custom_report_dir(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")

    _run_main(["--root", str(tmp_path), "--write", "--report-dir", "custom_dr"])

    assert (tmp_path / "custom_dr").is_dir()
    assert list((tmp_path / "custom_dr").glob("*_doctor.noema.json"))


def test_main_report_dir_default_is_doctor_reports(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")

    _run_main(["--root", str(tmp_path), "--write"])

    # Default report_dir should be "doctor_reports"
    assert (tmp_path / "doctor_reports").is_dir()


# ---------------------------------------------------------------------------
# Argument parsing edge cases
# ---------------------------------------------------------------------------


def test_main_root_defaults_to_current_directory(monkeypatch, tmp_path: Path) -> None:
    # Patch os.getcwd or change Path(".") resolution by setting cwd
    import os
    (tmp_path / "f.py").write_text("z = 0\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    # Run with no --root argument; default is "."
    code, output = _run_main([])

    assert code == 0
    data = json.loads(output)
    assert data["file_count"] >= 1


def test_main_with_fail_status_json_output_shows_findings(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text('v = 1.0 - snap.get("R_H", 1.0)\n', encoding="utf-8")

    code, output = _run_main(["--root", str(tmp_path)])

    assert code == 1
    data = json.loads(output)
    assert data["status"] == "FAIL"
    codes = [f["code"] for f in data["findings"]]
    assert "inverted_rh_metric_candidate" in codes


def test_main_json_ensure_ascii_false(tmp_path: Path) -> None:
    # ensure_ascii=False: non-ASCII characters pass through unchanged
    (tmp_path / "unicode_ok.py").write_text("# こんにちは\nx = 1\n", encoding="utf-8")

    _, output = _run_main(["--root", str(tmp_path)])

    # Output should be valid JSON regardless of non-ASCII content in paths etc.
    data = json.loads(output)
    assert data["schema"] == "noema-holonomic-doctor/report/v0.1"