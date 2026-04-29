"""Ensure the repository root is importable during tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent.parent  # CIEL1/
for p in [str(ROOT), str(REPO / "src"), str(REPO / "integration" / "Orbital" / "main")]:
    if p not in sys.path:
        sys.path.insert(0, p)
