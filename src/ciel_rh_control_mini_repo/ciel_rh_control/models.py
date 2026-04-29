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
