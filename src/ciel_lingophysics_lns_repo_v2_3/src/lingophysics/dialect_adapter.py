"""Dialect and variant adapter policy for CIELingo v2.3."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json

def load_dialect_policy(path: str | Path) -> Dict[str, Any]: return json.loads(Path(path).read_text(encoding="utf-8"))
def adapter_level(policy: Dict[str, Any], adapter_id: str) -> str:
    for adapter in policy.get("sample_adapters", []):
        if adapter.get("id") == adapter_id: return adapter.get("level", "UNRESOLVED_ADAPTER_LEVEL")
    return "UNRESOLVED_ADAPTER_LEVEL"
def dialect_requires_review(policy: Dict[str, Any], adapter_id: str) -> bool:
    level = adapter_level(policy, adapter_id)
    return level == "UNRESOLVED_ADAPTER_LEVEL" or level in {"L3", "L4"}
def should_activate_adapter(policy: Dict[str, Any], explicit_variant: bool = False, detector_confidence: float = 0.0, threshold: float = 0.85) -> bool:
    return explicit_variant or detector_confidence >= threshold
