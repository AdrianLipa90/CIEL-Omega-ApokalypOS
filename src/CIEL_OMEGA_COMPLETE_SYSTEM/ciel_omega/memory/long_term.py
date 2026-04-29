"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Long-term episodic memory — serialise / restore field snapshots.

Source: ext18.LongTermMemory
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class LongTermMemory:
    """In-memory episodic store with JSON serialisation."""

    entries: List[Dict[str, Any]] = field(default_factory=list)

    def put(self, label: str, psi: np.ndarray, sigma: float, meta: Optional[Dict[str, Any]] = None):
        payload = {
            "label": label,
            "sigma": float(sigma),
            "shape": list(psi.shape),
            "psi_real": psi.real.astype(np.float32).tolist(),
            "psi_imag": psi.imag.astype(np.float32).tolist(),
            "meta": meta or {},
        }
        payload["hash"] = hashlib.sha256(
            json.dumps(payload["psi_real"][:64]).encode()
        ).hexdigest()[:16]
        self.entries.append(payload)

    def export_json(self) -> str:
        return json.dumps(self.entries, ensure_ascii=False)

    def load_json(self, data: str):
        self.entries = json.loads(data)

    def restore(self, idx: int = -1) -> Tuple[np.ndarray, float, Dict[str, Any]]:
        e = self.entries[idx]
        re = np.array(e["psi_real"], dtype=np.float32).reshape(e["shape"])
        im = np.array(e["psi_imag"], dtype=np.float32).reshape(e["shape"])
        psi = (re + 1j * im).astype(np.complex128)
        return psi, float(e["sigma"]), e.get("meta", {})


__all__ = ["LongTermMemory"]
