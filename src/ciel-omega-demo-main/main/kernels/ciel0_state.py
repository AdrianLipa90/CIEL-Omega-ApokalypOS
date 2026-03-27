from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class CIEL0State:
    I: np.ndarray
    tau: np.ndarray
    S: np.ndarray
    R: np.ndarray
    mass: np.ndarray
    Lambda0: np.ndarray
