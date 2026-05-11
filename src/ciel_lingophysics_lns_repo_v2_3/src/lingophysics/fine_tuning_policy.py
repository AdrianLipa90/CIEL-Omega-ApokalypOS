"""Fine-tuning policy helpers for CIELingo v2.3."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json

def load_algorithm_registry(path: str | Path) -> Dict[str, Any]: return json.loads(Path(path).read_text(encoding="utf-8"))
def promotion_allowed(score: float, target: str, policy: Dict[str, Any]) -> bool:
    thresholds = policy.get("fine_tuning_policy", {}).get("promotion_thresholds", {})
    return float(score) >= float(thresholds.get(target, 1.0))
def gguf_can_canonicalize() -> bool: return False
