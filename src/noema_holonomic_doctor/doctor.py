"""Public orchestration API for NOEMA Holonomic Doctor."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .checks import Finding, run_static_checks
from .manifest import ManifestEntry, manifest_digest, noema_ls
from .metrics import closure_error, d_lambda, doctor_cost, epsilon_neutrino, euler_berry_phase
from .report import DoctorReport, utc_stamp, write_append_only_report


@dataclass(frozen=True)
class DoctorConfig:
    report_dir: str = "doctor_reports"
    max_text_bytes: int = 256_000
    write: bool = False


def _severity_counts(findings: list[Finding]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return counts


def build_report(root: str | Path, config: DoctorConfig | None = None) -> DoctorReport:
    config = config or DoctorConfig()
    root_path = Path(root).resolve()
    manifest = noema_ls(root_path)
    digest = manifest_digest(manifest)
    total_bytes = sum(entry.size for entry in manifest)
    eps_nu = epsilon_neutrino(len(manifest), total_bytes)
    d_lam = d_lambda(manifest)
    phase = euler_berry_phase(digest)
    closure = closure_error(phase)
    findings = run_static_checks(root_path, manifest, max_bytes=config.max_text_bytes)
    j = doctor_cost(_severity_counts(findings), closure, d_lam, eps_nu)
    status = "PASS" if not findings else "WARN" if all(f.severity in {"low", "medium"} for f in findings) else "FAIL"
    return DoctorReport(
        schema="noema-holonomic-doctor/report/v0.1",
        generated_at=utc_stamp(),
        root=str(root_path),
        manifest_sha256=digest,
        file_count=len(manifest),
        total_bytes=total_bytes,
        d_lambda=d_lam,
        epsilon_neutrino=eps_nu,
        euler_berry_phase=phase,
        euler_berry_closure_error=closure,
        j_doctor=j,
        status=status,
        findings=findings,
        manifest_sample=manifest[:25],
    )


def run_doctor_cycle(root: str | Path, config: DoctorConfig | None = None) -> DoctorReport:
    config = config or DoctorConfig()
    report = build_report(root, config)
    if config.write:
        write_append_only_report(root, report, report_dir=config.report_dir)
    return report


__all__ = [
    "DoctorConfig",
    "DoctorReport",
    "Finding",
    "ManifestEntry",
    "build_report",
    "noema_ls",
    "run_doctor_cycle",
    "write_append_only_report",
]
