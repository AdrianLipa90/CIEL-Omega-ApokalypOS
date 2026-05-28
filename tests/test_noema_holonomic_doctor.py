from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from noema_holonomic_doctor import DoctorConfig, noema_ls, run_doctor_cycle


def test_noema_ls_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "b.json").write_text('{"x": 1}\n', encoding="utf-8")

    first = noema_ls(tmp_path)
    second = noema_ls(tmp_path)

    assert first == second
    assert [entry.path for entry in first] == ["a.py", "b.json"]
    assert all(len(entry.sha256) == 64 for entry in first)


def test_doctor_detects_inverted_rh_metric(tmp_path: Path) -> None:
    bad = tmp_path / "bad_metric.py"
    bad.write_text('score = 1.0 - snap.get("R_H", 1.0)\n', encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=False))

    assert report.status == "FAIL"
    assert any(f.code == "inverted_rh_metric_candidate" for f in report.findings)


def test_doctor_write_is_append_only_with_current_pointer(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("R_H = 0.0\n", encoding="utf-8")

    report = run_doctor_cycle(tmp_path, DoctorConfig(write=True, report_dir="doctor_reports"))

    out_dir = tmp_path / "doctor_reports"
    reports = sorted(out_dir.glob("*_doctor.noema.json"))
    current = out_dir / "CURRENT_DOCTOR.noema.json"

    assert report.schema == "noema-holonomic-doctor/report/v0.1"
    assert reports
    assert current.exists()
    pointer = json.loads(current.read_text(encoding="utf-8"))
    assert pointer["status"] == report.status
    assert len(pointer["report_sha256"]) == 64
