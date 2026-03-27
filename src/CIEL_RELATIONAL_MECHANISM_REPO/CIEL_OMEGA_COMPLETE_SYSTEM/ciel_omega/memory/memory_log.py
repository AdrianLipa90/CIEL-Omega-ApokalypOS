"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Structured memory journal with ethical tagging (JSONL).

Source: ext3.MemoryLog
"""

from __future__ import annotations

import datetime
import json
import os
from typing import Any, Dict

import numpy as np


class MemoryLog:
    """Append-only JSONL journal for ethical events and field measurements."""

    def __init__(self, path: str = "ciel_memory.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def record(self, entry: Dict[str, Any]):
        entry["timestamp"] = datetime.datetime.utcnow().isoformat()
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_event(self, name: str, ethical: bool, value: float):
        self.record({"event": name, "ethical": ethical, "value": value})

    def summarize(self) -> Dict[str, float]:
        if not os.path.exists(self.path):
            return {}
        with open(self.path, "r", encoding="utf-8") as f:
            lines = [json.loads(x) for x in f if x.strip()]
        values = [l["value"] for l in lines if "value" in l]
        return {"mean_value": float(np.mean(values)) if values else 0.0}


__all__ = ["MemoryLog"]
