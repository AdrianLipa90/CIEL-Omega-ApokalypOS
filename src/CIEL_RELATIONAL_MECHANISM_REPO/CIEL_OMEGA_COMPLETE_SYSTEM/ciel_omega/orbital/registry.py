from __future__ import annotations
import json
import math
import cmath
from pathlib import Path
from .model import Sector, OrbitalSystem, ZetaPole, ZetaVertex

def rho_from_theta(theta: float) -> float:
    return math.tanh(math.tan(theta / 2.0))

def _build_zeta(params: dict) -> ZetaPole | None:
    if not bool(params.get("use_zeta_pole", True)):
        return None
    theta_star = math.acos(-1.0 / 3.0)
    phase0 = float(params.get("zeta_phase0", 0.0))
    omega = cmath.exp(2j * math.pi / 3.0)
    support_phases = [phase0 + cmath.phase(omega**k) for k in range(3)]
    return ZetaPole(vertices=[
        ZetaVertex("Z0", 0.0, phase0, tau=0.489, weight=0.25),
        ZetaVertex("Z1", theta_star, support_phases[0], tau=0.353, weight=0.25),
        ZetaVertex("Z2", theta_star, support_phases[1], tau=0.263, weight=0.25),
        ZetaVertex("Z3", theta_star, support_phases[2], tau=0.353, weight=0.25),
    ], kappa_tetra=float(params.get("zeta_tetra_weight", 0.5)), spin=0.0, rho=float(params.get("zeta_rho", 0.45)))

def load_system(sectors_path: str | Path, couplings_path: str | Path, params: dict | None = None) -> OrbitalSystem:
    sectors_raw = json.loads(Path(sectors_path).read_text(encoding="utf-8"))
    couplings_raw = json.loads(Path(couplings_path).read_text(encoding="utf-8"))
    p = dict(params or {})
    sectors = {}
    for name, payload in sectors_raw["sectors"].items():
        payload = dict(payload)
        payload.setdefault("rho", rho_from_theta(payload["theta"]))
        payload.setdefault("spin", 0.0)
        sectors[name] = Sector(name=name, **payload)
    return OrbitalSystem(sectors=sectors, couplings=couplings_raw["couplings"], params=p, zeta_pole=_build_zeta(p))
