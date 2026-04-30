"""Semantic mass operator — Foundation Pack P3.

M_sem(f) = α·M_EC(f) + β·M_ZS(f) + χ·C_dep(f) + δ·C_prov(f) + ε·C_exec(f)

For sectors and entities we proxy the components from available data:
  M_EC  — Euler-Collatz mass: based on info_mass and coupling strength (closure affinity)
  M_ZS  — Zeta-Schrödinger mass: based on coherence_weight and spectral resonance (tau)
  C_dep — dependency centrality: sum of coupling weights to this node
  C_prov— provenance: horizon_class encoded as depth score
  C_exec— execution activity: amplitude (sectors) or coupling_ciel (entities)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .loader import SectorGeom, EntityGeom, load_sectors, load_couplings, load_entities

# Default weights (Foundation Pack §8, operator M_sem)
_ALPHA = 0.30   # M_EC weight
_BETA  = 0.25   # M_ZS weight
_CHI   = 0.20   # C_dep weight
_DELTA = 0.15   # C_prov weight
_EPS   = 0.10   # C_exec weight

# Horizon depth scores (SEALED = most anchored, OBSERVATIONAL = least)
_HORIZON_DEPTH = {
    "SEALED":        1.0,
    "POROUS":        0.65,
    "TRANSMISSIVE":  0.80,
    "OBSERVATIONAL": 0.35,
}

# Tau normalization reference (max tau in Foundation Pack = 0.489)
_TAU_REF = 0.489


@dataclass
class SemanticMassRecord:
    id: str
    M_sem: float       # total semantic mass [0, ∞)
    M_EC: float        # Euler-Collatz component
    M_ZS: float        # Zeta-Schrödinger component
    C_dep: float       # dependency centrality
    C_prov: float      # provenance depth
    C_exec: float      # execution activity
    orbit_period: float   # T² ∝ a³ / A_eff (Kepler-like; a = Poincaré radius)
    orbit_radius: float   # Poincaré radius used for Kepler rule


def compute_sector_mass(
    sector: SectorGeom,
    coupling_sum: float,
    alpha: float = _ALPHA,
    beta: float  = _BETA,
    chi: float   = _CHI,
    delta: float = _DELTA,
    eps: float   = _EPS,
) -> SemanticMassRecord:
    """Compute semantic mass for a sector node."""
    # M_EC — closure affinity: info_mass scaled by coupling
    M_EC = sector.info_mass * (0.5 + 0.5 * min(1.0, coupling_sum))

    # M_ZS — spectral resonance: coherence_weight and tau proximity to equilateral solution
    tau_norm = sector.tau / _TAU_REF
    M_ZS = sector.coherence_weight * (0.5 + 0.5 * tau_norm)

    # C_dep — dependency centrality: normalised sum of coupling weights
    C_dep = min(1.0, coupling_sum / 3.0)

    # C_prov — for sectors: use amplitude as proxy for provenance depth
    C_prov = sector.amplitude

    # C_exec — execution activity: amplitude directly
    C_exec = sector.amplitude

    M_sem = alpha * M_EC + beta * M_ZS + chi * C_dep + delta * C_prov + eps * C_exec

    # Kepler-like orbit period: T² ∝ a³ / A_eff where a = poincare_radius(theta)
    from .disk import poincare_radius
    a = max(1e-6, poincare_radius(sector.theta))
    T_sq = (a**3) / max(1e-9, M_sem)
    T = math.sqrt(T_sq)

    return SemanticMassRecord(
        id=f"sector:{sector.name}",
        M_sem=round(M_sem, 5),
        M_EC=round(M_EC, 5),
        M_ZS=round(M_ZS, 5),
        C_dep=round(C_dep, 5),
        C_prov=round(C_prov, 5),
        C_exec=round(C_exec, 5),
        orbit_period=round(T, 5),
        orbit_radius=round(a, 5),
    )


def compute_entity_mass(
    entity: EntityGeom,
    alpha: float = _ALPHA,
    beta: float  = _BETA,
    chi: float   = _CHI,
    delta: float = _DELTA,
    eps: float   = _EPS,
) -> SemanticMassRecord:
    """Compute semantic mass for an entity node."""
    # M_EC — coupling as Euler-Collatz affinity proxy (high coupling = closure anchor)
    M_EC = entity.coupling_ciel

    # M_ZS — horizon class encodes spectral depth
    M_ZS = _HORIZON_DEPTH.get(entity.horizon_class, 0.5)

    # C_dep — entities have no explicit coupling matrix; use coupling_ciel as proxy
    C_dep = entity.coupling_ciel * 0.7

    # C_prov — horizon depth
    C_prov = _HORIZON_DEPTH.get(entity.horizon_class, 0.5)

    # C_exec — coupling_ciel (activity = how tightly coupled to CIEL)
    C_exec = entity.coupling_ciel

    M_sem = alpha * M_EC + beta * M_ZS + chi * C_dep + delta * C_prov + eps * C_exec

    # Kepler: a = coupling_ciel (rho on disk)
    a = max(1e-6, min(0.999, entity.coupling_ciel))
    T_sq = (a**3) / max(1e-9, M_sem)
    T = math.sqrt(T_sq)

    return SemanticMassRecord(
        id=entity.id,
        M_sem=round(M_sem, 5),
        M_EC=round(M_EC, 5),
        M_ZS=round(M_ZS, 5),
        C_dep=round(C_dep, 5),
        C_prov=round(C_prov, 5),
        C_exec=round(C_exec, 5),
        orbit_period=round(T, 5),
        orbit_radius=round(a, 5),
    )


def build_mass_table(
    include_entities: bool = True,
    entity_limit: int = 40,
) -> list[SemanticMassRecord]:
    """Compute semantic mass for all sectors and entities. Returns sorted by M_sem desc."""
    sectors   = load_sectors()
    couplings = load_couplings()
    records: list[SemanticMassRecord] = []

    for name, sector in sectors.items():
        # Dependency: sum of all coupling weights to this sector
        coupling_sum = sum(w for (src, dst), w in couplings.items() if dst == name)
        records.append(compute_sector_mass(sector, coupling_sum))

    if include_entities:
        try:
            entities = load_entities()
        except (ImportError, FileNotFoundError):
            entities = []
        for entity in entities[:entity_limit]:
            records.append(compute_entity_mass(entity))

    records.sort(key=lambda r: r.M_sem, reverse=True)
    return records


if __name__ == "__main__":
    import json
    table = build_mass_table()
    print(f"{'ID':<40} {'M_sem':>7} {'M_EC':>6} {'M_ZS':>6} {'C_dep':>6} {'T_orbit':>8}")
    print("-" * 75)
    for r in table:
        short = r.id.replace("entity:", "").replace("sector:", "§")
        print(f"{short:<40} {r.M_sem:>7.4f} {r.M_EC:>6.4f} {r.M_ZS:>6.4f} {r.C_dep:>6.4f} {r.orbit_period:>8.4f}")
