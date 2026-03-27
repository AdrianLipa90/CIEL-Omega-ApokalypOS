from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class GlyphDataset:
    path: str
    items: List[Dict[str, Any]] = field(default_factory=list)

    def load(self) -> 'GlyphDataset':
        with open(self.path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.items = data if isinstance(data, list) else data.get('items', [])
        return self

    def to_vectors(self, key: str = 'features') -> np.ndarray:
        feats = [it.get(key, []) for it in self.items]
        maxlen = max((len(v) for v in feats), default=0)
        arr = np.zeros((len(feats), maxlen), dtype=float)
        for i, v in enumerate(feats):
            arr[i, : len(v)] = np.asarray(v, dtype=float)
        return arr


class GlyphInterpreter:
    def __init__(self, vectors: np.ndarray):
        self.vectors = np.asarray(vectors, dtype=float)
        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-12
        self.vectors = self.vectors / norms

    def to_field(self, shape: Tuple[int, int], code: Optional[List[int]] = None) -> np.ndarray:
        h, w = shape
        Y = np.linspace(-1.0, 1.0, h)[:, None]
        X = np.linspace(-1.0, 1.0, w)[None, :]
        field = np.zeros((h, w), dtype=np.complex128)

        if not len(self.vectors):
            return field

        idx = code if code is not None else list(range(min(4, len(self.vectors))))
        for k in idx:
            vec = self.vectors[k]
            cx = ((k + 1) / (len(self.vectors) + 1)) * 1.6 - 0.8
            cy = -cx
            r2 = (X - cx) ** 2 + (Y - cy) ** 2
            basis = np.exp(-3.0 * r2)
            weight = np.tanh(np.sum(vec))
            field += weight * basis

        return field.astype(np.complex128)
