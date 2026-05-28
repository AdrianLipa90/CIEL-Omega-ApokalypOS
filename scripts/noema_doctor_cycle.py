#!/usr/bin/env python3
"""Run one NOEMA Holonomic Doctor diagnostic cycle.

Usage:
    python scripts/noema_doctor_cycle.py --root .
    python scripts/noema_doctor_cycle.py --root . --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from noema_holonomic_doctor import DoctorConfig, run_doctor_cycle


def main() -> int:
    parser = argparse.ArgumentParser(description="Run NOEMA Holonomic Doctor diagnostics.")
    parser.add_argument("--root", default=".", help="Repository/root path to scan. Defaults to current directory.")
    parser.add_argument("--write", action="store_true", help="Write append-only report under doctor_reports/.")
    parser.add_argument("--report-dir", default="doctor_reports", help="Report directory name relative to root.")
    args = parser.parse_args()

    report = run_doctor_cycle(
        Path(args.root),
        DoctorConfig(write=args.write, report_dir=args.report_dir),
    )
    print(json.dumps(report.to_json_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report.status in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
