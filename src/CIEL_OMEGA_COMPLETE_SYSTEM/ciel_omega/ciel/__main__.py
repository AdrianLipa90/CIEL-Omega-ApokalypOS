"""Canonical package entrypoint for CIEL/Ω.

This package surface delegates to the canonical Omega orchestrator instead of
bypassing it through direct engine-only flows.
"""

from __future__ import annotations

import sys
from pathlib import Path

_OMEGA_ROOT = Path(__file__).resolve().parents[1]
if str(_OMEGA_ROOT) not in sys.path:
    sys.path.insert(0, str(_OMEGA_ROOT))

from ciel_orchestrator import main


if __name__ == "__main__":
    raise SystemExit(main())
