from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXTRA_PATHS = (
    ROOT,
    ROOT / 'src' / 'ciel_rh_control_mini_repo',
    ROOT / 'src' / 'CIEL_OMEGA_COMPLETE_SYSTEM',
)

for path in EXTRA_PATHS:
    text = str(path)
    if path.exists() and text not in sys.path:
        sys.path.insert(0, text)

# Preload canonical integration package so pytest import order does not depend on
# namespace-package resolution.
import integration.Orbital.main.bootstrap  # noqa: F401
