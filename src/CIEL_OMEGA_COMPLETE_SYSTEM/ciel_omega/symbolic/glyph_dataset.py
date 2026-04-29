"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Glyph/sigil dataset loaders (JSON / TXT / CVOS format).

Sources: ext1.GlyphDataset, ext8.CVOSDatasetLoader
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

import numpy as np


@dataclass
class GlyphDataset:
    """Load glyph items from a JSON file and convert to feature vectors."""

    path: str
    items: List[Dict[str, Any]] = field(default_factory=list)

    def load(self) -> "GlyphDataset":
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.items = data if isinstance(data, list) else data.get("items", [])
        return self

    def to_vectors(self, key: str = "features") -> np.ndarray:
        feats = [it.get(key, []) for it in self.items]
        maxlen = max((len(v) for v in feats), default=0)
        arr = np.zeros((len(feats), maxlen), dtype=float)
        for i, v in enumerate(feats):
            arr[i, : len(v)] = np.asarray(v, dtype=float)
        return arr


@dataclass
class CVOSDatasetLoader:
    """Load CVOS-formatted glyph data from JSON or line-oriented TXT."""

    base_dir: str = "."

    def load_json(self, filename: str) -> List[Dict[str, Any]]:
        path = f"{self.base_dir}/{filename}"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else data.get("items", [])

    def load_txt(self, filename: str) -> List[Dict[str, Any]]:
        path = f"{self.base_dir}/{filename}"
        items: List[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                items.append({"text": line})
        return items


__all__ = ["GlyphDataset", "CVOSDatasetLoader"]
