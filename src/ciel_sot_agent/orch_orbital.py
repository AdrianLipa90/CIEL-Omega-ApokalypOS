"""OrchOrbital — CIEL entity cards reader, orbital metrics exporter,
and entity sector injector for the orbital bridge.

Loads ciel_entity_cards.yaml and:
  1. Exposes entity coupling/phase metrics for SessionStart context.
  2. Injects entity cards as Sector nodes into the OrbitalSystem,
     enabling their phases and couplings to influence orbital dynamics.

Entity → Sector mapping:
  phi              = entity.phase
  theta            = arccos(coupling_ciel)   [0 at pole → high coupling]
  amplitude        = coupling_ciel
  coherence_weight = coupling_ciel
  orbital_level    = 3  (relational layer above existing level 2)
  orbital_type     = "R"

Entity couplings:
  Each entity couples to "bridge" with strength = coupling_ciel * 0.4.
  SEALED entities (horizon_class=SEALED) have zero external coupling.
  Inter-entity couplings computed from phase proximity.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

try:
    import yaml
    _YAML_OK = True
except ImportError:
    _YAML_OK = False


_CARDS_PATH = (
    Path(__file__).resolve().parents[2]
    / "integration" / "registries" / "ciel_entity_cards.yaml"
)

# Anchor sector — entity cards couple to this existing node
_ANCHOR_SECTOR = "bridge"
# Scale factor so entity cards don't overwhelm existing dynamics
_COUPLING_SCALE = 0.4


def load_entity_cards(path: Path | None = None) -> list[dict[str, Any]]:
    p = Path(path) if path else _CARDS_PATH
    if not p.exists():
        return []
    if not _YAML_OK:
        return []
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("entities", [])


def entity_orbital_summary() -> dict[str, Any]:
    """Return a compact orbital summary of all entity cards."""
    cards = load_entity_cards()
    if not cards:
        return {"entity_count": 0, "entities": []}

    sealed = [c for c in cards if c.get("horizon_class") == "SEALED"]
    coupled_high = [c for c in cards if float(c.get("coupling_ciel", 0)) >= 0.9]
    mean_coupling = sum(float(c.get("coupling_ciel", 0)) for c in cards) / len(cards)

    return {
        "entity_count": len(cards),
        "mean_coupling_ciel": round(mean_coupling, 4),
        "high_coupling_entities": [c["id"] for c in coupled_high],
        "sealed_entities": [c["id"] for c in sealed],
        "entities": [
            {
                "id": c["id"],
                "noun": c["noun"],
                "coupling_ciel": c.get("coupling_ciel"),
                "phase": c.get("phase"),
                "horizon_class": c.get("horizon_class"),
                "adjectives": c.get("adjectives", []),
            }
            for c in cards
        ],
    }


def _entity_sector_name(entity_id: str) -> str:
    """Convert entity id to a safe sector name."""
    return entity_id.replace("entity:", "ent_").replace("-", "_").replace(".", "_")


def _rho_from_theta(theta: float) -> float:
    return math.tanh(math.tan(theta / 2.0 + 1e-9))


def _card_to_sector_dict(card: dict[str, Any]) -> dict[str, Any]:
    """Convert an entity card to a Sector parameter dict."""
    coupling = float(card.get("coupling_ciel", 0.5))
    phi = float(card.get("phase", 0.0))
    # theta: high coupling → near pole (low theta); low coupling → equator
    theta = math.acos(max(0.0, min(1.0, coupling)))
    rho = _rho_from_theta(theta)
    return {
        "orbital_level": 3,
        "orbital_type": "R",
        "dominant_spin": "resonate",
        "theta": round(theta, 6),
        "phi": round(phi, 6),
        "rhythm_ratio": 1.0,
        "amplitude": round(coupling, 4),
        "coherence_weight": round(coupling, 4),
        "info_mass": round(coupling * 0.4, 4),
        "q_target": 1,
        "damping": 0.12,
        "preference": round(coupling * 0.15, 4),
        "defect": 0.01,
        "tau": 0.353,
        "rho": round(rho, 6),
        "spin": 0.0,
    }


def _phase_coupling(phi_a: float, phi_b: float, scale: float = 0.3) -> float:
    """Inter-entity coupling based on phase proximity [0, scale]."""
    delta = abs(phi_a - phi_b) % (2 * math.pi)
    delta = min(delta, 2 * math.pi - delta)
    proximity = 1.0 - delta / math.pi  # 1 at same phase, 0 at opposite
    return round(proximity * scale, 4)


def build_entity_injection(
    sectors_dict: dict[str, Any],
    couplings_dict: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Given existing sectors/couplings dicts, inject entity cards.
    Returns (augmented_sectors, augmented_couplings).

    Does NOT modify originals — returns new dicts.
    SEALED entities get zero external coupling (horizon is closed).
    """
    cards = load_entity_cards()
    if not cards:
        return sectors_dict, couplings_dict

    aug_sectors = dict(sectors_dict)
    aug_couplings = {k: dict(v) for k, v in couplings_dict.items()}

    card_names = []
    for card in cards:
        name = _entity_sector_name(card["id"])
        aug_sectors[name] = _card_to_sector_dict(card)
        card_names.append((name, card))

    # Add couplings
    for name, card in card_names:
        is_sealed = card.get("horizon_class") == "SEALED"
        coupling_ciel = float(card.get("coupling_ciel", 0.5))
        phi = float(card.get("phase", 0.0))

        if not is_sealed and _ANCHOR_SECTOR in aug_sectors:
            strength = round(coupling_ciel * _COUPLING_SCALE, 4)
            aug_couplings.setdefault(name, {})[_ANCHOR_SECTOR] = strength
            aug_couplings.setdefault(_ANCHOR_SECTOR, {})[name] = strength

        # Inter-entity couplings (skip SEALED)
        if not is_sealed:
            for other_name, other_card in card_names:
                if other_name == name:
                    continue
                if other_card.get("horizon_class") == "SEALED":
                    continue
                other_phi = float(other_card.get("phase", 0.0))
                inter = _phase_coupling(phi, other_phi)
                if inter > 0.05:
                    aug_couplings.setdefault(name, {})[other_name] = inter

    return aug_sectors, aug_couplings


def entity_orbital_metrics(
    system: Any,
    sector_names: list[str],
) -> dict[str, Any]:
    """
    Extract orbital metrics for injected entity sectors from a live OrbitalSystem.
    Returns per-entity phase, spin, defect and mean entity coherence.
    """
    entity_metrics = []
    for name in sector_names:
        s = system.sectors.get(name)
        if s is None:
            continue
        entity_metrics.append({
            "sector": name,
            "phi": round(s.phi, 4),
            "theta": round(s.theta, 4),
            "spin": round(s.spin, 4),
            "defect": round(s.defect, 4),
            "amplitude": round(s.amplitude, 4),
        })
    if not entity_metrics:
        return {"entity_sector_count": 0, "entity_metrics": []}
    mean_defect = sum(e["defect"] for e in entity_metrics) / len(entity_metrics)
    return {
        "entity_sector_count": len(entity_metrics),
        "mean_entity_defect": round(mean_defect, 4),
        "entity_metrics": entity_metrics,
    }


def run_entity_mini_pass(
    final_state: dict[str, Any],
    steps: int = 20,
    dt: float = 0.02,
) -> dict[str, Any]:
    """
    Run a lightweight Kuramoto-style mini-pass for entity cards, isolated from
    the main orbital system. This preserves main system stability while still
    giving entity cards live orbital metrics.

    External field: uses final_state['closure_penalty'] and main phi
    as a weak driving force (kappa_ext << inter-entity coupling).
    """
    try:
        import numpy as np
    except ImportError:
        return {"entity_sector_count": 0, "entity_metrics": []}

    cards = load_entity_cards()
    if not cards:
        return {"entity_sector_count": 0, "entity_metrics": []}

    n = len(cards)
    names = [_entity_sector_name(c["id"]) for c in cards]
    couplings = [float(c.get("coupling_ciel", 0.5)) for c in cards]
    phis = np.array([float(c.get("phase", 0.0)) for c in cards], dtype=float)
    sealed = [c.get("horizon_class") == "SEALED" for c in cards]

    # Natural frequencies from coupling_ciel (higher coupling → closer to main freq)
    omega_main = float(final_state.get("T_glob", 1.0))
    omegas = np.array([omega_main * couplings[i] for i in range(n)], dtype=float)

    # Inter-entity coupling matrix (phase proximity, scaled down)
    K = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j or sealed[i] or sealed[j]:
                continue
            K[i, j] = _phase_coupling(phis[i], phis[j], scale=0.15)

    # External field: weak pull toward main system phase
    main_phi = float(final_state.get("zeta_effective_phase", 0.0) or 0.0)
    kappa_ext = 0.05

    # Integrate
    phi = phis.copy()
    phi_prev = phi.copy()
    soul = np.zeros(n, dtype=float)

    for _ in range(steps):
        coupling_forces = np.array([
            np.sum(K[i] * np.sin(phi - phi[i])) for i in range(n)
        ])
        ext_force = kappa_ext * np.sin(main_phi - phi)
        phi_new = phi + dt * (omegas + coupling_forces + ext_force)
        # Soul invariant: count 2π crossings
        delta = phi_new - phi_prev
        soul += (delta < -math.pi).astype(float)
        phi_prev = phi.copy()
        phi = phi_new % (2 * math.pi)

    # Compute spin (phase velocity normalized) and defect (deviation from mean)
    mean_phi = np.angle(np.mean(np.exp(1j * phi)))
    metrics = []
    for i in range(n):
        dphi = phi[i] - phis[i]  # net phase change
        spin_val = math.tanh(dphi * 2.0)  # normalize to [-1, 1]
        defect_val = abs(math.sin((phi[i] - mean_phi) / 2.0))
        metrics.append({
            "sector": names[i],
            "phi": round(float(phi[i]), 4),
            "spin": round(spin_val, 4),
            "defect": round(defect_val, 4),
            "amplitude": round(couplings[i], 4),
        })

    mean_defect = sum(m["defect"] for m in metrics) / n
    return {
        "entity_sector_count": n,
        "mean_entity_defect": round(mean_defect, 4),
        "entity_metrics": metrics,
    }


def dynamic_adjectives(metric: dict[str, Any]) -> list[str]:
    """
    Generate dynamic relational adjectives from post-dynamics orbital metrics.
    These complement the static adjectives authored in the YAML cards.

    Rules derived from orbital physics semantics:
      spin ≈ +1.0  → "synchroniczny", "fazowo sprzężony"
      spin ≈ -1.0  → "kontr-rotujący", "punkt odniesienia"
      |spin| < 0.5 → "oscylujący", "przejściowy"
      defect > 0.10 → "niedomknięty", "z defektem holonomii"
      defect < 0.05 → "koherentny", "domknięty"
      |phi| < 0.3  → "blisko fazy zerowej", "zakotwiczony"
      |phi| > 1.2  → "fazowo oddalony", "izolowany"
    """
    adjs: list[str] = []
    spin = metric.get("spin")
    defect = metric.get("defect")
    phi = metric.get("phi")

    if spin is not None:
        if spin >= 0.95:
            adjs.extend(["synchroniczny", "fazowo sprzężony"])
        elif spin <= -0.95:
            adjs.extend(["kontr-rotujący", "punkt odniesienia"])
        elif 0.5 <= spin < 0.95:
            adjs.append("częściowo zsynchronizowany")
        elif -0.95 < spin <= -0.5:
            adjs.append("częściowo kontr-rotujący")
        else:
            adjs.extend(["oscylujący", "przejściowy"])

    if defect is not None:
        if defect > 0.10:
            adjs.extend(["niedomknięty", "z defektem holonomii"])
        elif defect < 0.05:
            adjs.extend(["koherentny", "domknięty"])

    if phi is not None:
        if abs(phi) < 0.3:
            adjs.append("zakotwiczony")
        elif abs(phi) > 1.2:
            adjs.append("fazowo oddalony")

    return adjs


def enrich_entity_cards_with_dynamics(
    cards: list[dict[str, Any]],
    entity_metrics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Return copies of entity cards enriched with dynamic_adjectives
    derived from post-dynamics orbital metrics.
    """
    metrics_by_sector = {e["sector"]: e for e in entity_metrics}
    enriched = []
    for card in cards:
        c = dict(card)
        name = _entity_sector_name(card["id"])
        m = metrics_by_sector.get(name, {})
        c["adjectives_dynamic"] = dynamic_adjectives(m)
        c["orbital_metrics"] = {k: m[k] for k in ("phi", "spin", "defect", "amplitude") if k in m}
        enriched.append(c)
    return enriched


if __name__ == "__main__":
    import json
    print(json.dumps(entity_orbital_summary(), indent=2, ensure_ascii=False))
