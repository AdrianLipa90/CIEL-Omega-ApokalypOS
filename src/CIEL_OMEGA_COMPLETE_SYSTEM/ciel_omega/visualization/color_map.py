"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

CIEL/OS colour palette — map resonance/ethics value → RGB.

Source: ext4.ColorMap
"""

from __future__ import annotations

from typing import Tuple


class ColorMap:
    """Map a [0,1] value to a CIEL/OS RGB colour."""

    palette = {
        "SOUL_BLUE":      (0.2, 0.4, 0.9),
        "INTENTION_GOLD": (0.95, 0.8, 0.2),
        "ETHICS_WHITE":   (1.0, 1.0, 0.95),
        "WARNING_RED":    (0.9, 0.2, 0.2),
        "BALANCE_GREEN":  (0.3, 0.9, 0.5),
    }

    @staticmethod
    def map_value(v: float) -> Tuple[float, float, float]:
        v = max(0.0, min(1.0, v))
        if v < 0.3:
            return ColorMap.palette["WARNING_RED"]
        elif v < 0.7:
            r1, g1, b1 = ColorMap.palette["WARNING_RED"]
            r2, g2, b2 = ColorMap.palette["INTENTION_GOLD"]
            f = (v - 0.3) / 0.4
            return (r1 + f * (r2 - r1), g1 + f * (g2 - g1), b1 + f * (b2 - b1))
        else:
            r1, g1, b1 = ColorMap.palette["INTENTION_GOLD"]
            r2, g2, b2 = ColorMap.palette["ETHICS_WHITE"]
            f = (v - 0.7) / 0.3
            return (r1 + f * (r2 - r1), g1 + f * (g2 - g1), b1 + f * (b2 - b1))


__all__ = ["ColorMap"]
