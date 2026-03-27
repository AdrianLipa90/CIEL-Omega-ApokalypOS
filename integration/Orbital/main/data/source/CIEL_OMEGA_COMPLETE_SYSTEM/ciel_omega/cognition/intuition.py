"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Entropy-weighted intuition with memory buffer.

Source: ext10.IntuitiveCortex
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np


@dataclass
class IntuitiveCortex:
    """Lightweight intuition synthesis via entropy weighting + memory blend."""

    entropy_map: np.ndarray
    predictivity: float = 0.7
    memory_buffer: List[np.ndarray] = field(default_factory=list)
    max_memory: int = 64

    def _weights(self) -> np.ndarray:
        w = np.exp(-np.asarray(self.entropy_map, dtype=float).ravel())
        return w / (np.sum(w) + 1e-12)

    def ingest(self, obs: np.ndarray) -> None:
        v = np.asarray(obs, dtype=float).ravel()
        self.memory_buffer.append(v)
        if len(self.memory_buffer) > self.max_memory:
            self.memory_buffer.pop(0)

    def intuition(self, inputs: np.ndarray) -> float:
        x = np.asarray(inputs, dtype=float).ravel()
        w = self._weights()
        raw = np.dot(w, x)
        if self.memory_buffer:
            m = np.mean(np.stack(self.memory_buffer, axis=0), axis=0)
            raw = (1 - self.predictivity) * raw + self.predictivity * float(np.dot(w, m))
        return float(np.tanh(raw))

    def update_entropy(self, percept: np.ndarray, k: float = 0.1) -> None:
        p = np.asarray(percept, dtype=float).ravel()
        p = p / (np.max(p) + 1e-12)
        self.entropy_map = np.clip(
            self.entropy_map - k * p + 0.5 * k * (1 - p), 0.0, 5.0
        )


__all__ = ["IntuitiveCortex"]
