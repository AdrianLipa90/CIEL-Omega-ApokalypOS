"""Report model and append-only writer for NOEMA Holonomic Doctor."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .checks import Finding
from .manifest import ManifestEntry, sha256_bytes


@dataclass(frozen=True)
class DoctorReport:
    schema: str
    generated_at: str
    root: str
    manifest_sha256: str
    file_count: int
    total_bytes: int
    d_lambda: float
    epsilon_neutrino: float
    euler_berry_phase: float
    euler_berry_closure_error: float
    j_doctor: float
    status: str
    findings: list[Finding]
    manifest_sample: list[ManifestEntry]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["findings"] = [asdict(f) for f in self.findings]
        data["manifest_sample"] = [asdict(m) for m in self.manifest_sample]
        return data


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def write_append_only_report(root: str | Path, report: DoctorReport, *, report_dir: str = "doctor_reports") -> Path:
    """Write report history and update a CURRENT pointer.

    The timestamped report is append-only.  ``CURRENT_DOCTOR.noema.json`` is
    only a pointer to the latest immutable report.
    """
    root_path = Path(root).resolve()
    out_dir = root_path / report_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{report.generated_at}_doctor.noema.json"
    current_path = out_dir / "CURRENT_DOCTOR.noema.json"
    payload = json.dumps(report.to_json_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    report_path.write_text(payload, encoding="utf-8")
    current = {
        "schema": "noema-holonomic-doctor/current/v0.1",
        "generated_at": report.generated_at,
        "report_path": report_path.as_posix(),
        "report_sha256": sha256_bytes(payload.encode("utf-8")),
        "status": report.status,
        "j_doctor": report.j_doctor,
    }
    current_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path


__all__ = ["DoctorReport", "utc_stamp", "write_append_only_report"]
