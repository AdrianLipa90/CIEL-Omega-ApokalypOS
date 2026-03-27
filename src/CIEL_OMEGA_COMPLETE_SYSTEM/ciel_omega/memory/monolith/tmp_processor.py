"""CIEL/Ω Memory — TMP Kernel: two-phase analysis (A1 + A2).

Split from: unified_memory.py (lines 234–290)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from memory.monolith.data_types import DataVector
from memory.monolith.defaults import (
    gamma_from_categories,
    spectral_categories,
    validate_timestamp,
)
from memory.monolith.rules_engine import RuleHeuristicsEngine


class TMPKernel:
    """Temporary Memory Processor — gate data through rules and heuristics."""

    def __init__(self, cfg_dir: Path):
        self.rh = RuleHeuristicsEngine(cfg_dir)
        self.immutable_rules = {
            "require_context": True,
            "require_sense": True,
            "ethical_gate": True,
        }

    def first_analysis(self, D: DataVector) -> Dict[str, Any]:
        """A1 — structural checks (context, sense, timestamp)."""
        if self.immutable_rules["require_context"] and not D.D_C:
            return {"verdict": "FAIL", "response": "Missing context.", "bifurcation": 0}
        if self.immutable_rules["require_sense"] and not D.D_S:
            return {"verdict": "FAIL", "response": "Missing sense.", "bifurcation": 0}
        ok_ts, norm_ts = validate_timestamp(D.D_T)
        if not ok_ts:
            return {"verdict": "FAIL", "response": "Invalid timestamp.", "bifurcation": 0}
        D.D_T = norm_ts or D.D_T

        if isinstance(D.D_S, str) and len(D.D_S.strip()) >= 4:
            return {"verdict": "PASS", "D_TYPE": "text", "D_ATTR": {"length": len(D.D_S)}, "bifurcation": 0}
        return {"verdict": "HOLD", "response": "Provide more details.", "bifurcation": 0}

    def second_analysis(self, D: DataVector, D_TYPE: str, D_ATTR: Dict[str, Any]) -> Dict[str, Any]:
        """A2 — ethical gate + weighted scoring + spectral γ."""
        text = str(D.D_S or "")
        if self.immutable_rules["ethical_gate"] and not self.rh.ethical_gate(text):
            return {"verdict": "REJECT", "reason": "Ethical gate failed.", "bifurcation": 0}

        d_dict = {"D_C": D.D_C, "D_S": D.D_S, "D_A": D.D_A, "D_T": D.D_T,
                  "D_M": D.D_M, "D_TYPE": D_TYPE, "D_ATTR": D_ATTR}
        base = self.rh.weight(d_dict)
        cat = spectral_categories(d_dict)
        gamma = gamma_from_categories(cat)
        Wp = {k: (v * gamma if isinstance(v, float) else v) for k, v in base.items()}
        W_total = (Wp["W_L"] + Wp["W_S"] + Wp["W_K"] + Wp["W_E"]) / 4.0

        if W_total < 0.40:
            return {"verdict": "REJECT", "reason": "Too weak.", "weights": Wp, "gamma": gamma, "categories": cat, "bifurcation": 0}
        if W_total < 0.70:
            return {"verdict": "HOLD", "reason": "Needs clarification.", "weights": Wp, "gamma": gamma, "categories": cat, "bifurcation": 0}
        return {"verdict": "PASS", "weights": Wp, "gamma": gamma, "categories": cat, "bifurcation": 1}

    def process(self, D: DataVector) -> Dict[str, Any]:
        """Full A1→A2 pipeline."""
        a1 = self.first_analysis(D)
        if a1["verdict"] != "PASS":
            return {"OUT": a1, "report": "A1 pending user context or failed."}
        a2 = self.second_analysis(D, a1["D_TYPE"], a1["D_ATTR"])
        return {
            "OUT": a2,
            "report": {"REJECT": "Blocked by RULE/HEUR.", "HOLD": "Awaiting user input.", "PASS": "Logical pass."}[a2["verdict"]],
            "A1": a1,
        }
