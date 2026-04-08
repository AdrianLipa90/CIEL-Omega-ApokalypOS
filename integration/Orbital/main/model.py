from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Sector:
    name: str
    orbital_level: int
    orbital_type: str
    dominant_spin: str
    theta: float
    phi: float
    rhythm_ratio: float
    amplitude: float
    coherence_weight: float
    info_mass: float
    q_target: int
    damping: float
    preference: float
    defect: float = 0.0
    berry_phase: float = 0.0
    tau: float = 0.353
    rho: float = 0.5
    spin: float = 0.0
    mu_eff: float = 1.0
    winding: int = 0
    tau_orbit: float = 1.0
    phase_slip_ready: bool = False
    orbit_stability: float = 1.0


@dataclass
class ZetaVertex:
    name: str
    theta: float
    phi: float
    tau: float
    weight: float = 0.25


@dataclass
class ZetaPole:
    vertices: List[ZetaVertex]
    kappa_tetra: float = 1.0
    spin: float = 0.0
    rho: float = 0.45


@dataclass
class OrbitalSystem:
    sectors: Dict[str, Sector] = field(default_factory=dict)
    couplings: Dict[str, Dict[str, float]] = field(default_factory=dict)
    params: Dict[str, float] = field(default_factory=dict)
    zeta_pole: Optional[ZetaPole] = None

    def names(self):
        return list(self.sectors.keys())

    def coupling(self, a: str, b: str) -> float:
        if a == b:
            return 0.0
        return self.couplings.get(a, {}).get(b, self.couplings.get(b, {}).get(a, 0.0))
