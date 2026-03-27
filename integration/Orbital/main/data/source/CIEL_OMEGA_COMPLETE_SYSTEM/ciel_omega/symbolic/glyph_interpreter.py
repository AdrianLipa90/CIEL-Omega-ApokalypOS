"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Glyph interpreter — project sigils onto 2-D consciousness fields + DSL node execution.

Sources: ext1.GlyphInterpreter, ext8.GlyphNode, ext8.GlyphNodeInterpreter
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Field-level interpreter (ext1)
# ---------------------------------------------------------------------------

class GlyphInterpreter:
    """Map sigil vectors to a 2-D complex field via radial basis functions."""

    def __init__(self, vectors: np.ndarray):
        self.vectors = np.asarray(vectors, dtype=float)
        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-12
        self.vectors = self.vectors / norms

    def to_field(self, shape: Tuple[int, int], code: Optional[List[int]] = None) -> np.ndarray:
        h, w = shape
        Y = np.linspace(-1.0, 1.0, h)[:, None]
        X = np.linspace(-1.0, 1.0, w)[None, :]
        out = np.zeros((h, w), dtype=np.complex128)

        if not len(self.vectors):
            return out

        idx = code if code is not None else list(range(min(4, len(self.vectors))))
        for k in idx:
            vec = self.vectors[k]
            cx = ((k + 1) / (len(self.vectors) + 1)) * 1.6 - 0.8
            cy = -cx
            r2 = (X - cx) ** 2 + (Y - cy) ** 2
            basis = np.exp(-3.0 * r2)
            weight = np.tanh(np.sum(vec))
            out += weight * basis
        return out


# ---------------------------------------------------------------------------
# DSL node interpreter (ext8)
# ---------------------------------------------------------------------------

@dataclass
class GlyphNode:
    """Single executable node in the glyph DSL."""

    name: str
    operator: str = "identity"
    params: Dict = field(default_factory=dict)

    def execute(self) -> str:
        return f"{self.name}:{self.operator}({self.params})"

    def transfer_to(self, new_operator: str):
        self.operator = new_operator


class GlyphNodeInterpreter:
    """Registry-based interpreter for glyph DSL nodes."""

    def __init__(self):
        self._registry: Dict[str, GlyphNode] = {}

    def register(self, node: GlyphNode):
        self._registry[node.name] = node

    def execute_all(self) -> List[str]:
        return [node.execute() for node in self._registry.values()]

    def get(self, name: str) -> Optional[GlyphNode]:
        return self._registry.get(name)


__all__ = ["GlyphInterpreter", "GlyphNode", "GlyphNodeInterpreter"]
