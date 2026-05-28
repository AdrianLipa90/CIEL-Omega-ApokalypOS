"""Compatibility wrapper for NOEMA Holonomic Doctor static checks."""
from __future__ import annotations

from .checks_runtime import (
    Finding,
    check_inverted_rh,
    check_rh_pipeline_hook,
    run_static_checks,
)

__all__ = ["Finding", "check_inverted_rh", "check_rh_pipeline_hook", "run_static_checks"]
