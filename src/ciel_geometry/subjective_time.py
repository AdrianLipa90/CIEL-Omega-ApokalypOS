"""Subjective time operator — Foundation Pack P3.

Δτ_i(k) = Δt · g(r_i, C_i, Δ_i, m_i, A_i)

where:
  r_i  — Poincaré radius (orbit position, 0=center, 1=boundary)
  C_i  — coherence contribution of this entity
  Δ_i  — local holonomy defect contribution
  m_i  — semantic mass M_sem
  A_i  — attractor weight (coupling to system attractor)

g(r, C, Δ, m, A) = (1 / τ_ref) · (1 - r²) · (C / (1 + Δ)) · sqrt(m · A)

Interpretation:
  - Entities near disk boundary (r→1) have slower subjective time (hyperbolic dilation)
  - High coherence + low defect = faster subjective time
  - High semantic mass and attractor weight = higher baseline rate

Winding accumulation: w(N) = (1/2π) Σ_k Δφ_k · (Δt / Δτ_k)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .loader import load_sectors, load_entities, load_bridge_state
from .disk import poincare_radius, entity_to_disk
from .semantic_mass import build_mass_table, SemanticMassRecord

# τ eigenvalues from relational contract
TAU_VALUES = (0.263, 0.353, 0.489)
TAU_REF    = TAU_VALUES[1]   # middle tau as reference timescale


ORBIT_SHELLS = (0.20, 0.40, 0.60, 0.80)  # radial boundaries r < shell[i] → orbit i+1


def orbit_index(r: float) -> int:
    """Named orbit index: 1 (core) … 5 (boundary halo)."""
    for i, boundary in enumerate(ORBIT_SHELLS):
        if r < boundary:
            return i + 1
    return len(ORBIT_SHELLS) + 1


ORBIT_NAMES = {1: "core", 2: "inner", 3: "mid", 4: "outer", 5: "halo"}


@dataclass
class SubjectiveTimeRecord:
    id: str
    tau_scale: float     # Δτ/Δt — subjective time rate relative to system clock
    r: float             # Poincaré radius
    coherence: float     # C_i proxy
    defect: float        # Δ_i proxy
    M_sem: float         # semantic mass
    A_eff: float         # effective attractor weight
    winding_rate: float  # winding accumulation rate (per unit real time)
    orbit_idx: int = 0   # named orbit shell (1=core … 5=halo)


def _g(r: float, C: float, delta: float, m: float, A: float) -> float:
    """Subjective time scaling function."""
    hyperbolic_factor = max(0.01, 1.0 - r**2)   # → 0 at boundary
    coherence_factor  = C / max(1e-9, 1.0 + delta)
    mass_factor       = math.sqrt(max(0.0, m * A))
    return (1.0 / TAU_REF) * hyperbolic_factor * coherence_factor * mass_factor


def compute_subjective_times(
    coherence_index: float = 0.9,
    global_defect:   float = 0.005,
    include_entities: bool = True,
    entity_limit: int = 40,
) -> list[SubjectiveTimeRecord]:
    """Compute subjective time rates for all sectors and entities."""
    sectors   = load_sectors()
    mass_table: dict[str, SemanticMassRecord] = {
        r.id: r for r in build_mass_table(include_entities=include_entities, entity_limit=entity_limit)
    }

    records: list[SubjectiveTimeRecord] = []

    # Sectors
    for name, sector in sectors.items():
        sid = f"sector:{name}"
        r   = poincare_radius(sector.theta)
        C   = coherence_index * sector.coherence_weight
        Δ   = global_defect + sector.defect
        m   = mass_table.get(sid, None)
        M   = m.M_sem if m else 0.5
        A   = sector.amplitude
        tau = _g(r, C, Δ, M, A)
        # Winding rate: approximate phase change per unit time given tau
        # φ changes at rate ω = 2π / T_orbit; w_rate = ω / (2π·tau) = 1 / (T·tau)
        T   = m.orbit_period if m else 1.0
        w_rate = 1.0 / max(1e-9, T * tau)
        records.append(SubjectiveTimeRecord(
            id=sid, tau_scale=round(tau, 5), r=round(r, 5),
            coherence=round(C, 5), defect=round(Δ, 5),
            M_sem=round(M, 5), A_eff=round(A, 5),
            winding_rate=round(w_rate, 5),
            orbit_idx=orbit_index(r),
        ))

    # Entities
    if include_entities:
        try:
            entities = load_entities()
        except (ImportError, FileNotFoundError):
            entities = []
        for entity in entities[:entity_limit]:
            eid = entity.id
            r   = min(0.999, entity.coupling_ciel)
            C   = coherence_index * entity.coupling_ciel
            Δ   = global_defect
            m   = mass_table.get(eid, None)
            M   = m.M_sem if m else 0.4
            A   = entity.coupling_ciel
            tau = _g(r, C, Δ, M, A)
            T   = m.orbit_period if m else 1.0
            w_rate = 1.0 / max(1e-9, T * tau)
            records.append(SubjectiveTimeRecord(
                id=eid, tau_scale=round(tau, 5), r=round(r, 5),
                coherence=round(C, 5), defect=round(Δ, 5),
                M_sem=round(M, 5), A_eff=round(A, 5),
                winding_rate=round(w_rate, 5),
                orbit_idx=orbit_index(r),
            ))

    records.sort(key=lambda x: x.tau_scale, reverse=True)
    return records


def compute_from_bridge() -> list[SubjectiveTimeRecord]:
    """Convenience: load coherence and defect from live bridge report."""
    bridge = load_bridge_state()
    coherence = bridge.coherence_index
    # R_H = |Δ_H|² → global defect ≈ sqrt(R_H)
    # We use effective_rh from state_manifest if available; fall back to closure_penalty proxy
    global_defect = math.sqrt(max(0.0, min(1.0, (bridge.closure_penalty - 4.0) / 2.0))) * 0.01
    return compute_subjective_times(coherence_index=coherence, global_defect=global_defect)


if __name__ == "__main__":
    records = compute_from_bridge()
    print(f"{'ID':<40} {'τ_scale':>8} {'r':>6} {'orbit':>6} {'M_sem':>7} {'w_rate':>8}")
    print("-" * 80)
    for rec in records:
        short = rec.id.replace("entity:", "").replace("sector:", "§")
        orbit = ORBIT_NAMES.get(rec.orbit_idx, f"o{rec.orbit_idx}")
        print(f"{short:<40} {rec.tau_scale:>8.5f} {rec.r:>6.4f} {orbit:>6} {rec.M_sem:>7.4f} {rec.winding_rate:>8.4f}")
