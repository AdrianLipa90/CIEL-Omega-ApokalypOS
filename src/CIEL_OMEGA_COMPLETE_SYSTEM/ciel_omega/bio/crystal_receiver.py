"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Crystal field receiver — translate external vibration signals into intention space.

Source: ext7.CrystalFieldReceiver
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class CrystalFieldReceiver:
    """Adapter: external vibration → intention field perturbation."""

    grid_shape: Tuple[int, int] = (96, 96)
    coupling: float = 0.1

    def receive(self, vibration: np.ndarray, base_field: np.ndarray) -> np.ndarray:
        """Mix normalised vibration signal into *base_field*."""
        v = np.asarray(vibration, dtype=float).ravel()
        norm_v = v / (np.linalg.norm(v) + 1e-12)
        # Project 1-D vibration onto the 2-D field via outer broadcast
        h, w = base_field.shape
        projection = np.outer(norm_v[:h], norm_v[:w]) if len(norm_v) >= max(h, w) else np.zeros_like(base_field)
        return base_field + self.coupling * projection


__all__ = ["CrystalFieldReceiver"]
