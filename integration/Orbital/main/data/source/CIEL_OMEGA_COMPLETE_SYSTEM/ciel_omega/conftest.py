"""Ensure the package parent is importable during tests."""

from __future__ import annotations

import sys
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent
PACKAGE_PARENT = PKG_ROOT.parent

for candidate in (PACKAGE_PARENT, PKG_ROOT):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)
