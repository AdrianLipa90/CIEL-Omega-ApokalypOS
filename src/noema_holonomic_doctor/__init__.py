"""NOEMA Holonomic Doctor subsystem.

Standalone diagnostic layer for cyclic repository health checks.
It builds a deterministic local manifest, evaluates holonomic-style code-health
constraints, and can write append-only NOEMA-style reports when explicitly asked.
"""
from __future__ import annotations

from .checks import Finding, run_static_checks
from .doctor import DoctorConfig, build_report, run_doctor_cycle
from .manifest import ManifestEntry, manifest_digest, noema_ls
from .metrics import closure_error, d_lambda, doctor_cost, epsilon_neutrino, euler_berry_phase
from .report import DoctorReport, write_append_only_report

__all__ = [
    "DoctorConfig",
    "DoctorReport",
    "Finding",
    "ManifestEntry",
    "build_report",
    "closure_error",
    "d_lambda",
    "doctor_cost",
    "epsilon_neutrino",
    "euler_berry_phase",
    "manifest_digest",
    "noema_ls",
    "run_doctor_cycle",
    "run_static_checks",
    "write_append_only_report",
]
