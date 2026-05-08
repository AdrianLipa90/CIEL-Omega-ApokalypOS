"""Semantic mass operator — Foundation Pack P3.

M_sem(f) = α·M_EC(f) + β·M_ZS(f) + χ·C_dep(f) + δ·C_prov(f) + ε·C_exec(f)
         + ζ·C_nov(f) + ξ·C_conf(f)

For sectors and entities we proxy the components from available data:
  M_EC  — Euler-Collatz mass: based on info_mass and coupling strength (closure affinity)
  M_ZS  — Zeta-Schrödinger mass: based on coherence_weight and spectral resonance (tau)
  C_dep — dependency centrality: sum of coupling weights to this node
  C_prov— provenance: horizon_class encoded as depth score
  C_exec— execution activity: amplitude (sectors) or coupling_ciel (entities)
  C_nov — novelty: recently disturbed / low-coupling nodes are fresher (higher priority)
  C_conf— conflict: spread of incoming coupling weights (contested nodes are heavier)
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from .loader import SectorGeom, EntityGeom, load_sectors, load_couplings, load_entities

_REPO_REGISTRY = (
    Path(__file__).parent.parent.parent
    / "integration/registries/repository_registry.json"
)

# Default weights (Foundation Pack §8, operator M_sem)
# Sum = 1.00: 0.27+0.23+0.18+0.13+0.09+0.06+0.04
_ALPHA = 0.27   # M_EC weight  (was 0.30 — renormalized to make room for C_nov, C_conf)
_BETA  = 0.23   # M_ZS weight  (was 0.25)
_CHI   = 0.18   # C_dep weight (was 0.20)
_DELTA = 0.13   # C_prov weight(was 0.15)
_EPS   = 0.09   # C_exec weight(was 0.10)
_ZETA  = 0.06   # C_nov weight — novelty: freshly disturbed nodes rise in priority
_XI    = 0.04   # C_conf weight— conflict: contested nodes carry more semantic weight

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
    C_nov: float       # novelty: 1 = fresh/disturbed, 0 = deeply stable
    C_conf: float      # conflict: std of incoming coupling weights (contested = heavier)
    orbit_period: float   # T² ∝ a³ / A_eff (Kepler-like; a = Poincaré radius)
    orbit_radius: float   # Poincaré radius used for Kepler rule


def compute_sector_mass(
    sector: SectorGeom,
    coupling_sum: float,
    incoming_weights: list[float] | None = None,
    alpha: float = _ALPHA,
    beta: float  = _BETA,
    chi: float   = _CHI,
    delta: float = _DELTA,
    eps: float   = _EPS,
    zeta: float  = _ZETA,
    xi: float    = _XI,
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

    # C_nov — novelty: active defect signals recent disturbance → node is fresh
    # defect ∈ [0, ∞); saturate at 0.2 → C_nov ∈ [0, 1]
    C_nov = min(1.0, sector.defect / 0.2)

    # C_conf — conflict: spread of incoming coupling weights
    # std of incoming weights; saturate at 0.5 → C_conf ∈ [0, 1]
    if incoming_weights and len(incoming_weights) > 1:
        mean_w = sum(incoming_weights) / len(incoming_weights)
        variance = sum((w - mean_w)**2 for w in incoming_weights) / len(incoming_weights)
        C_conf = min(1.0, math.sqrt(variance) / 0.5)
    else:
        C_conf = 0.0

    M_sem = (alpha * M_EC + beta * M_ZS + chi * C_dep + delta * C_prov
             + eps * C_exec + zeta * C_nov + xi * C_conf)

    # Kepler-like orbit period: T² ∝ a³ / A_eff where a = poincare_radius(theta)
    # For attractor/relational sectors with theta≈0, use info_mass as fallback radius
    from .disk import poincare_radius
    a_geom = poincare_radius(sector.theta)
    a = a_geom if a_geom > 1e-4 else max(1e-4, sector.info_mass * 0.5)
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
        C_nov=round(C_nov, 5),
        C_conf=round(C_conf, 5),
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
    zeta: float  = _ZETA,
    xi: float    = _XI,
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

    # C_nov — novelty: OBSERVATIONAL horizon = least anchored = freshest
    # invert provenance: low horizon depth → high novelty
    C_nov = 1.0 - _HORIZON_DEPTH.get(entity.horizon_class, 0.5)

    # C_conf — conflict: number of adjectives is a proxy for semantic tension
    # more descriptors = more contested identity; saturate at 6
    n_adj = len(getattr(entity, 'adjectives', []) or [])
    C_conf = min(1.0, n_adj / 6.0)

    M_sem = (alpha * M_EC + beta * M_ZS + chi * C_dep + delta * C_prov
             + eps * C_exec + zeta * C_nov + xi * C_conf)

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
        C_nov=round(C_nov, 5),
        C_conf=round(C_conf, 5),
        orbit_period=round(T, 5),
        orbit_radius=round(a, 5),
    )


def compute_repo_mass(repo: dict) -> SemanticMassRecord:
    """Compute semantic mass for a repository object (repository_registry.json).

    Mapowanie z RELATIONAL_SEED_ORBIT_SOLVER_V0:
      M_EC = mass (closure affinity — rola w łańcuchu redukcji)
      M_ZS = 1 - |phi| / π (bliskość fazy do rezonansu Zeta-Schrödingera)
      C_dep = upstream != local → wyższa zależność zewnętrzna
      C_prov = role encoding (canonical > integration > cockpit)
      C_exec = mass (aktywność wykonawcza = masa repo)
    """
    _ROLE_PROV = {
        "canonical-foundations": 1.0,
        "integration-attractor": 0.90,
        "historical-theory-simulations": 0.75,
        "desktop-runtime-surface": 0.65,
        "cockpit-ui-education": 0.55,
    }

    raw_mass = float(repo.get("mass", 0.5))
    phi = float(repo.get("phi", 0.0))
    role = str(repo.get("role", ""))
    upstream = str(repo.get("upstream", ""))
    repo_id = str(repo.get("key", repo.get("identity", "unknown")))

    M_EC = raw_mass
    M_ZS = 1.0 - min(abs(phi) / math.pi, 1.0)
    C_dep = 0.8 if "local" not in upstream else 0.4
    C_prov = _ROLE_PROV.get(role, 0.5)
    C_exec = raw_mass

    # C_nov — novelty: phase near 0 (resonance) = active/fresh; near π = dormant
    C_nov = 1.0 - min(abs(phi) / math.pi, 1.0)

    # C_conf — conflict: integration roles are structurally contested (many consumers)
    _ROLE_CONF = {
        "integration-attractor":          0.75,
        "canonical-foundations":          0.30,
        "historical-theory-simulations":  0.45,
        "desktop-runtime-surface":        0.60,
        "cockpit-ui-education":           0.50,
    }
    C_conf = _ROLE_CONF.get(role, 0.40)

    M_sem = (_ALPHA * M_EC + _BETA * M_ZS + _CHI * C_dep
             + _DELTA * C_prov + _EPS * C_exec + _ZETA * C_nov + _XI * C_conf)

    a = max(1e-6, min(0.999, raw_mass))
    T = math.sqrt(a ** 3 / max(1e-9, M_sem))

    return SemanticMassRecord(
        id=f"repo:{repo_id}",
        M_sem=round(M_sem, 5),
        M_EC=round(M_EC, 5),
        M_ZS=round(M_ZS, 5),
        C_dep=round(C_dep, 5),
        C_prov=round(C_prov, 5),
        C_exec=round(C_exec, 5),
        C_nov=round(C_nov, 5),
        C_conf=round(C_conf, 5),
        orbit_period=round(T, 5),
        orbit_radius=round(a, 5),
    )


def build_mass_table(
    include_entities: bool = True,
    include_repos: bool = True,
    entity_limit: int = 40,
) -> list[SemanticMassRecord]:
    """Compute semantic mass for sectors, entities, and repositories.

    Source of truth: RELATIONAL_SEED_ORBIT_SOLVER_V0.
    Returns sorted by M_sem desc.
    """
    sectors   = load_sectors()
    couplings = load_couplings()
    records: list[SemanticMassRecord] = []

    # Build per-sector incoming weight lists for conflict computation
    from collections import defaultdict
    incoming: dict[str, list[float]] = defaultdict(list)
    for (src, dst), w in couplings.items():
        incoming[dst].append(w)

    for name, sector in sectors.items():
        coupling_sum = sum(incoming[name])
        records.append(compute_sector_mass(sector, coupling_sum, incoming_weights=incoming[name]))

    if include_entities:
        try:
            entities = load_entities()
        except (ImportError, FileNotFoundError):
            entities = []
        for entity in entities[:entity_limit]:
            records.append(compute_entity_mass(entity))

    if include_repos and _REPO_REGISTRY.exists():
        try:
            raw = json.loads(_REPO_REGISTRY.read_text())
            for repo in raw.get("repositories", []):
                records.append(compute_repo_mass(repo))
        except Exception:
            pass

    records.sort(key=lambda r: r.M_sem, reverse=True)
    return records


# ── Fuzja M_sem z wielu źródeł ───────────────────────────────────────────────
# STATUS: NIEDOKOŃCZONE — wagi propozycyjne, wymagają walidacji z Adrianem
# Oryginalne formuły pozostają bez zmian; to dodatkowe pole M_sem_unified.

def fuse_semantic_mass(
    geo: float | None = None,
    tsm: float | None = None,
    consolidation: float | None = None,
    affective: float | None = None,
) -> float:
    """Weighted fusion of four M_sem sources → M_sem_unified ∈ [0, 1].

    Weights (propozycyjne, do walidacji):
      geo=0.40, tsm=0.30, consolidation=0.20, affective=0.10
    Missing sources are excluded from the weighted average.
    """
    _W = {"geo": 0.40, "tsm": 0.30, "consolidation": 0.20, "affective": 0.10}
    sources = {
        "geo": geo,
        "tsm": tsm,
        "consolidation": consolidation,
        "affective": affective,
    }
    total_w = sum(_W[k] for k, v in sources.items() if v is not None)
    if total_w < 1e-9:
        return 0.0
    fused = sum(_W[k] * v for k, v in sources.items() if v is not None)
    return round(min(1.0, fused / total_w), 4)


if __name__ == "__main__":
    import json
    table = build_mass_table()
    print(f"{'ID':<40} {'M_sem':>7} {'M_EC':>6} {'M_ZS':>6} {'C_dep':>6} {'C_nov':>6} {'C_conf':>6} {'T_orbit':>8}")
    print("-" * 90)
    for r in table:
        short = r.id.replace("entity:", "").replace("sector:", "§")
        print(f"{short:<40} {r.M_sem:>7.4f} {r.M_EC:>6.4f} {r.M_ZS:>6.4f} {r.C_dep:>6.4f} {r.C_nov:>6.4f} {r.C_conf:>6.4f} {r.orbit_period:>8.4f}")
