"""Shared runtime bootstrap for local CIEL/Ω entry surfaces.

This module centralizes path normalization so orchestrator/client/unified do not
carry divergent bootstrap logic. It supports both package-style execution and
local script execution from the Omega root.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable


def candidate_paths(this_file: str | Path) -> tuple[Path, Path]:
    this_path = Path(this_file).resolve()
    omega_root = this_path.parent
    parent = omega_root.parent
    return omega_root, parent


def ensure_runtime_paths(this_file: str | Path) -> Path:
    omega_root, parent = candidate_paths(this_file)
    for candidate in (omega_root, parent):
        candidate_str = str(candidate)
        if candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)
    return omega_root
