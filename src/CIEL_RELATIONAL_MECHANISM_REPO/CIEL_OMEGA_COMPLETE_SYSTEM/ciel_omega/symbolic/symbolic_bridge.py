"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Symbolic bridge — integrates glyphs with ColorOS palette and Σ.

Source: ext8.SymbolicBridge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

import numpy as np


@dataclass
class SymbolicBridge:
    """Map glyph coherence × Σ to a CIEL/OS colour."""

    sigma_scalar: float
    palette: Dict[str, Tuple[float, float, float]] = field(default_factory=lambda: {
        "SOUL_BLUE":      (0.2, 0.4, 0.9),
        "INTENTION_GOLD": (0.95, 0.8, 0.2),
        "ETHICS_WHITE":   (1.0, 1.0, 0.95),
        "WARNING_RED":    (0.9, 0.2, 0.2),
        "BALANCE_GREEN":  (0.3, 0.9, 0.5),
    })

    def glyph_color(self, coherence: float) -> Tuple[float, float, float]:
        val = float(np.clip(coherence * self.sigma_scalar, 0.0, 1.0))
        if val < 0.3:
            base = np.array(self.palette["WARNING_RED"])
        elif val < 0.7:
            base = np.array(self.palette["INTENTION_GOLD"])
        else:
            base = np.array(self.palette["ETHICS_WHITE"])
        soul = np.array(self.palette["SOUL_BLUE"])
        rgb = base * val + (1 - val) * soul
        return tuple(float(c) for c in rgb)


__all__ = ["SymbolicBridge"]
