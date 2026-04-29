#!/usr/bin/env python3
"""Repo-local wrapper for the canonical CIEL/Ω inference surface."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OMEGA_ROOT = REPO_ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega"
if str(OMEGA_ROOT) not in sys.path:
    sys.path.insert(0, str(OMEGA_ROOT))

from ciel_inference_surface import main  # type: ignore

if __name__ == "__main__":
    raise SystemExit(main())
