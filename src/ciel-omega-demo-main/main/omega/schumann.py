from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import math
import time

import numpy as np


def schumann_harmonics(base: float = 7.83, k: int = 1) -> float:
    return base * k


@dataclass
class SchumannClock:
    base_hz: float = 7.83
    start_t: float = field(default_factory=time.perf_counter)

    def phase(self, t: Optional[float] = None, k: int = 1) -> float:
        t_now = (time.perf_counter() - self.start_t) if t is None else float(t)
        omega = 2.0 * math.pi * schumann_harmonics(self.base_hz, k)
        return float((omega * t_now) % (2.0 * math.pi))

    def carrier(self, shape: Tuple[int, int], amp: float = 1.0, k: int = 1) -> np.ndarray:
        ph = self.phase(k=k)
        return amp * np.exp(1j * ph) * np.ones(shape, dtype=np.complex128)
