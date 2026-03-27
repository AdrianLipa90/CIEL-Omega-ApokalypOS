"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Visual core — convert complex field to (H,W,3) tensor: [amp, sin(φ), cos(φ)].

Source: ext5.VisualCore
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class VisualCore:
    """Prepare visual data tensor without rendering (backend-agnostic)."""

    clip_amp: Optional[float] = None  # e.g. 99th percentile

    def tensorize(self, psi: np.ndarray) -> np.ndarray:
        amp = np.abs(psi)
        if self.clip_amp is not None:
            hi = np.percentile(amp, self.clip_amp)
            amp = np.clip(amp, 0.0, hi) / (hi + 1e-12)
        else:
            amp = amp / (np.max(amp) + 1e-12)
        ph = np.angle(psi)
        return np.stack([amp, np.sin(ph), np.cos(ph)], axis=-1)


__all__ = ["VisualCore"]
