"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

JSONL logger for reality-simulation events.

Source: ext1.RealityLogger
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict


class RealityLogger:
    """Append-only JSONL logger (tool-friendly format)."""

    def __init__(self, path: str = "logs/reality.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def record(self, step: int, metrics: Dict[str, Any]) -> None:
        rec = dict(step=step, t=time.time(), **metrics)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


__all__ = ["RealityLogger"]
