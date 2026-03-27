from __future__ import annotations

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
            sector=sector_key,
            mode=mode,
            severity=base["severity"],
            allowed_actions=list(base["allowed_actions"]),
            discouraged_actions=list(base["discouraged_actions"]),
            actions=list(base["actions"]),
            sector_overrides={sector_key: list(SECTOR_OVERRIDES[sector_key])},
            notes=notes,
        )
