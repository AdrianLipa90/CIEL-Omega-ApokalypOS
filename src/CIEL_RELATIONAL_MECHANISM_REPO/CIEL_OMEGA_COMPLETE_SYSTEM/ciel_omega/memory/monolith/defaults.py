"""CIEL/Ω Memory — Default configs, timestamp utils, spectral multiplier γ.

Split from: unified_memory.py (lines 38–128)
"""

from __future__ import annotations

import datetime as dt
import re
from typing import Any, Dict, Optional, Tuple

# -- Default configs --------------------------------------------------------

DEFAULT_RULES_IMMUTABLE = {
    "require_context": True,
    "require_sense": True,
    "ethical_gate": True,
    "forbidden_patterns": ["illegal", "harm", "exploit"],
}

DEFAULT_HEURISTICS_USER = {
    "weights": {"logic": 0.35, "semantic": 0.25, "context": 0.20, "emotion": 0.20},
    "boosts": {"novelty_hint": 0.15, "trusted_source": 0.10},
    "penalties": {"contradiction_flag": -0.25, "ethics_warning": -0.50},
}

DEFAULT_HEURISTICS_SELF = {
    "weights": {"logic": 0.30, "semantic": 0.25, "context": 0.25, "emotion": 0.20},
    "boosts": {"long_form": 0.10, "associations_present": 0.05},
    "penalties": {"too_short": -0.15},
}

# -- Timestamp validation ---------------------------------------------------

ISO8601_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$"
)


def is_iso8601(ts: str) -> bool:
    if not isinstance(ts, str):
        return False
    if ISO8601_RE.match(ts):
        return True
    try:
        dt.datetime.fromisoformat(ts)
        return True
    except Exception:
        return False


def validate_timestamp(ts: Optional[str]) -> Tuple[bool, Optional[str]]:
    if not ts:
        return (False, None)
    if is_iso8601(ts):
        try:
            norm = dt.datetime.fromisoformat(
                ts.replace("Z", "+00:00") if ts.endswith("Z") else ts
            ).isoformat()
            return (True, norm)
        except Exception:
            return (True, ts)
    return (False, None)


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# -- Spectral multiplier γ -------------------------------------------------

def spectral_categories(D: Dict[str, Any]) -> Dict[str, float]:
    sense = str(D.get("D_S", "") or "").strip()
    associations = D.get("D_A", []) or []
    meta = D.get("D_M", {}) or {}
    return {
        "clarity": 0.4 if len(sense) >= 64 else (0.2 if len(sense) >= 16 else -0.2),
        "relevance": 0.2 if associations else -0.1,
        "originality": 0.5 if meta.get("novelty_hint") else 0.0,
        "coherence": -0.6 if meta.get("contradiction_flag") else 0.1,
        "ethical_harmony": -0.7 if meta.get("ethics_warning") else 0.2,
    }


def gamma_from_categories(values: Dict[str, float]) -> float:
    if not values:
        return 1.0
    vals = sorted(clamp(v, -1.0, 1.0) for v in values.values())
    n = len(vals)
    med = vals[n // 2] if n % 2 == 1 else 0.5 * (vals[n // 2 - 1] + vals[n // 2])
    return clamp(1.0 + med, 0.0, 2.0)
