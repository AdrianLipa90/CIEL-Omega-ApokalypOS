"""CIEL/Ω Memory — Rule/heuristics weighting engine.

Split from: unified_memory.py (lines 170–228)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

from ciel_omega.memory.monolith.defaults import (
    DEFAULT_HEURISTICS_SELF,
    DEFAULT_HEURISTICS_USER,
    DEFAULT_RULES_IMMUTABLE,
    clamp,
)


class RuleHeuristicsEngine:
    """Score data vectors using immutable rules + user/self heuristics."""

    def __init__(self, cfg_dir: Path):
        self.cfg_dir = Path(cfg_dir)
        self.immutable = self._load_json("rules_immutable.json", DEFAULT_RULES_IMMUTABLE)
        self.user = self._load_json("heuristics_user.json", DEFAULT_HEURISTICS_USER)
        self.selfcfg = self._load_json("heuristics_self.json", DEFAULT_HEURISTICS_SELF)

    def _load_json(self, name: str, default_obj: Dict[str, Any]) -> Dict[str, Any]:
        try:
            p = self.cfg_dir / name
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
        return json.loads(json.dumps(default_obj))

    def ethical_gate(self, text: str) -> bool:
        if not self.immutable.get("ethical_gate", True):
            return True
        for pat in self.immutable.get("forbidden_patterns", []):
            if re.search(pat, text or "", flags=re.IGNORECASE):
                return False
        return True

    def weight(self, D_dict: Dict[str, Any]) -> Dict[str, float]:
        sense = str(D_dict.get("D_S", "")).strip()
        meta = D_dict.get("D_M", {}) or {}
        associations = D_dict.get("D_A", []) or []

        logic = 0.6 if len(sense) >= 32 else 0.4
        semantic = 0.6 if len(sense.split()) >= 5 else 0.4
        context = 0.55 if D_dict.get("D_C") else 0.30
        emotion = 0.50

        u = self.user
        if meta.get("trusted_source"):
            logic += u["boosts"].get("trusted_source", 0.10)
        if meta.get("novelty_hint"):
            semantic += u["boosts"].get("novelty_hint", 0.15)
        if meta.get("contradiction_flag"):
            logic += u["penalties"].get("contradiction_flag", -0.25)
        if meta.get("ethics_warning"):
            semantic += u["penalties"].get("ethics_warning", -0.50)

        s = self.selfcfg
        if len(sense) >= 120:
            logic += s["boosts"].get("long_form", 0.10)
        if associations:
            context += s["boosts"].get("associations_present", 0.05)
        if len(sense) < 8:
            semantic += s["penalties"].get("too_short", -0.15)

        def _cl(x: float) -> float:
            return clamp(x, 0.0, 1.0)

        return {"W_L": _cl(logic), "W_S": _cl(semantic), "W_K": _cl(context), "W_E": _cl(emotion)}
