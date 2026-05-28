from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPT = ROOT / "scripts" / "noema_doctor_cycle.py"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

_spec = importlib.util.spec_from_file_location("noema_doctor_cycle", SCRIPT)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)  # type: ignore[union-attr]


def _run_cli(args: list[str]) -> tuple[int, dict]:
    stdout = StringIO()
    with patch("sys.argv", ["noema_doctor_cycle.py", *args]), patch("sys.stdout", stdout):
        code = _module.main()
    return code, json.loads(stdout.getvalue())


def test_cli_returns_zero_for_clean_manifest(tmp_path: Path) -> None:
    (tmp_path / "clean.py").write_text("x = 1\n", encoding="utf-8")

    code, payload = _run_cli(["--root", str(tmp_path)])

    assert code == 0
    assert payload["schema"] == "noema-holonomic-doctor/report/v0.1"
    assert payload["status"] == "PASS"


def test_cli_returns_one_for_inverted_rh_metric(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text('score = 1.0 - snap.get("R_H", 1.0)\n', encoding="utf-8")

    code, payload = _run_cli(["--root", str(tmp_path)])

    assert code == 1
    assert payload["status"] == "FAIL"
    assert any(f["code"] == "inverted_rh_metric_candidate" for f in payload["findings"])


def test_cli_write_creates_append_only_report_and_current_pointer(tmp_path: Path) -> None:
    (tmp_path / "clean.py").write_text("x = 1\n", encoding="utf-8")

    code, payload = _run_cli(["--root", str(tmp_path), "--write"])

    out_dir = tmp_path / "doctor_reports"
    report_files = sorted(out_dir.glob("*_doctor.noema.json"))
    current = out_dir / "CURRENT_DOCTOR.noema.json"

    assert code == 0
    assert payload["status"] == "PASS"
    assert len(report_files) == 1
    assert current.exists()
    pointer = json.loads(current.read_text(encoding="utf-8"))
    assert pointer["status"] == payload["status"]
    assert len(pointer["report_sha256"]) == 64


def test_cli_write_respects_custom_report_dir(tmp_path: Path) -> None:
    (tmp_path / "clean.py").write_text("x = 1\n", encoding="utf-8")

    code, payload = _run_cli(["--root", str(tmp_path), "--write", "--report-dir", "custom_reports"])

    out_dir = tmp_path / "custom_reports"
    assert code == 0
    assert payload["status"] == "PASS"
    assert out_dir.is_dir()
    assert (out_dir / "CURRENT_DOCTOR.noema.json").exists()
    assert list(out_dir.glob("*_doctor.noema.json"))
