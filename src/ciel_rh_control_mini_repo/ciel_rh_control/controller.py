from .models import RHDecision, ThresholdProfile
from .policy import BASE_POLICIES, SECTOR_OVERRIDES

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
