from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ThresholdProfile:
    r1: float = 0.30
    r2: float = 0.70

    def validate(self) -> None:
        if self.r1 < 0 or self.r2 < 0:
            raise ValueError("Thresholds must be non-negative.")
        if self.r1 >= self.r2:
            raise ValueError("Expected r1 < r2.")


@dataclass
class RHDecision:
    rh: float
    sector: str
    mode: str
    severity: str
    allowed_actions: list[str] = field(default_factory=list)
    discouraged_actions: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    sector_overrides: dict[str, list[str]] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    effective_rh: float = 0.0
    drivers: dict[str, float] = field(default_factory=dict)


BASE_POLICIES = {
    "normal_operation": {
        "severity": "low",
        "allowed_actions": ["run", "merge", "route", "compare", "report", "link"],
        "discouraged_actions": [],
        "actions": [
            "Proceed with normal execution.",
            "Keep manifests and README mesh synchronized.",
            "Monitor R_H but do not constrain throughput unnecessarily.",
        ],
        "notes": ["Low coherence defect: expansion is admissible."],
    },
    "slow_execution_local_correction": {
        "severity": "medium",
        "allowed_actions": ["resolve", "report", "link", "compare", "stabilize", "route"],
        "discouraged_actions": ["fast_merge", "broad_refactor"],
        "actions": [
            "Slow execution tempo.",
            "Prefer local correction over large global changes.",
            "Route only through explicit bridges.",
            "Increase reporting and dependency exposure.",
        ],
        "notes": ["Moderate coherence defect: restrict expansion and repair local drift."],
    },
    "freeze_and_rebuild_closure": {
        "severity": "high",
        "allowed_actions": ["resolve", "report", "stabilize", "link", "archive"],
        "discouraged_actions": ["merge", "broad_route", "speculative_refactor", "execution_burst"],
        "actions": [
            "Freeze merges.",
            "Isolate sectors contributing to high defect.",
            "Rebuild closure from constraints and manifests.",
            "Prioritize diagnosis over execution.",
        ],
        "notes": ["High coherence defect: the system should not expand."],
    },
}


SECTOR_OVERRIDES = {
    "runtime": [
        "Reduce execution tempo.",
        "Check memory synchronization before new runs.",
    ],
    "bridge": [
        "Restrict transport to explicit dependency paths.",
        "Audit semantic mismatch and broken bridges first.",
    ],
    "memory": [
        "Check path residue and disappearing-file history.",
        "Prefer stabilization over new writes.",
    ],
    "constraints": [
        "Re-evaluate closure residuals.",
        "Treat hidden bypasses as critical.",
    ],
    "generic": [],
}


def _obs(snapshot: dict, *keys: str, default: float = 0.0) -> float:
    for key in keys:
        if key in snapshot and snapshot.get(key) is not None:
            try:
                return float(snapshot.get(key, default) or 0.0)
            except Exception:
                continue
    return float(default)


def _phase_gap(phi_berry: float, target_phase: float) -> float:
    # Cyclic distance on S¹: wrap difference into [-π, π] first
    diff = (phi_berry - target_phase + math.pi) % (2 * math.pi) - math.pi
    return min(1.0, abs(diff) / math.pi)


def effective_rh(snapshot: dict) -> tuple[float, dict[str, float]]:
    """Collapse local/nonlocal/Euler observables into a single RH defect score.

    Lower is better.  This is intentionally conservative: nonlocal incoherence and
    weak Euler closure should raise the defect even when raw R_H is small.
    """
    raw_rh = max(0.0, _obs(snapshot, "R_H"))
    eba_defect = max(0.0, _obs(snapshot, "nonlocal_eba_defect_mean", "eba_defect_mean"))
    coherent_fraction = max(0.0, min(1.0, _obs(snapshot, "nonlocal_coherent_fraction", "coherent_fraction")))
    closure_score = max(0.0, min(1.0, _obs(snapshot, "euler_bridge_closure_score", "bridge_closure_score", "closure_score")))
    phi_berry = _obs(snapshot, "nonlocal_phi_berry_mean", "phi_berry_mean")
    target_phase = _obs(snapshot, "euler_bridge_target_phase", "bridge_target_phase", "target_phase")
    phase_gap = _phase_gap(phi_berry, target_phase)

    score = (
        raw_rh
        + 0.35 * min(1.0, eba_defect)
        + 0.20 * (1.0 - coherent_fraction)
        + 0.15 * (1.0 - closure_score)
        + 0.10 * phase_gap
    )
    score = max(0.0, min(1.0, score))
    drivers = {
        "raw_rh": raw_rh,
        "eba_defect": eba_defect,
        "coherent_fraction": coherent_fraction,
        "closure_score": closure_score,
        "phase_gap": phase_gap,
    }
    return score, drivers


class RHController:
    def __init__(self, profile: ThresholdProfile | None = None):
        self.profile = profile or ThresholdProfile()
        self.profile.validate()

    def classify(self, rh: float) -> str:
        if rh < self.profile.r1:
            return "normal_operation"
        if rh < self.profile.r2:
            return "slow_execution_local_correction"
        return "freeze_and_rebuild_closure"

    def evaluate(self, rh: float, sector: str = "generic") -> RHDecision:
        if rh < 0:
            raise ValueError("R_H must be non-negative.")
        mode = self.classify(rh)
        base = BASE_POLICIES[mode]
        sector_key = sector if sector in SECTOR_OVERRIDES else "generic"
        notes = list(base["notes"])
        if sector_key != "generic":
            notes.append(f"Sector override applied: {sector_key}")
        return RHDecision(
            rh=rh,
            effective_rh=rh,
            drivers={"raw_rh": rh},
            sector=sector_key,
            mode=mode,
            severity=base["severity"],
            allowed_actions=list(base["allowed_actions"]),
            discouraged_actions=list(base["discouraged_actions"]),
            actions=list(base["actions"]),
            sector_overrides={sector_key: list(SECTOR_OVERRIDES[sector_key])},
            notes=notes,
        )

    def evaluate_snapshot(self, snapshot: dict, sector: str = "generic") -> RHDecision:
        rh_eff, drivers = effective_rh(snapshot)
        decision = self.evaluate(rh_eff, sector=sector)
        decision.effective_rh = rh_eff
        decision.drivers = drivers
        decision.notes.append(
            "effective_rh combines raw R_H, EBA defect, coherent fraction, Euler closure and Berry target phase gap."
        )
        return decision
