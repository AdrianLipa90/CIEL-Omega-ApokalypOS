"""NOEMA Holonomic Doctor subsystem.

A small, standalone diagnostic layer for cyclic repository health checks.
It is deliberately append-only/report-oriented: it diagnoses drift and defects,
but it does not auto-repair code unless an external caller explicitly applies a
repair candidate.
"""
from __future__ import annotations

from .doctor import (
    DoctorConfig,
    DoctorReport,
    ManifestEntry,
    NoemaDoctorFinding,
    build_report,
    noema_ls,
    run_doctor_cycle,
    write_append_only_report,
)

__all__ = [
    "DoctorConfig",
    "DoctorReport",
    "ManifestEntry",
    "NoemaDoctorFinding",
    "build_report",
    "noema_ls",
    "run_doctor_cycle",
    "write_append_only_report",
]
