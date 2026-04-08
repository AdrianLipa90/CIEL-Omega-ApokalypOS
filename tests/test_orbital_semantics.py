from __future__ import annotations

import json
import math
from pathlib import Path

from integration.Orbital.main.dynamics import step
from integration.Orbital.main.metrics import orbital_period_estimate, phase_slip_readiness
from integration.Orbital.main.registry import load_system
from src.ciel_sot_agent.phased_state import build_states


def _fixture_path() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "orbital_selection_relevance.json"


def _load_relevance_fixture() -> dict:
    return json.loads(_fixture_path().read_text(encoding="utf-8"))


def _build_fixture_states() -> tuple[list, dict, dict]:
    fixture = _load_relevance_fixture()
    entries = []
    path_to_id: dict[str, str] = {}
    for entry in fixture["entries"]:
        payload = dict(entry)
        path_to_id[payload["path"]] = payload.pop("id")
        payload["content"] = payload["content"].encode("utf-8")
        entries.append(payload)
    states = build_states(entries)
    return states, path_to_id, fixture


def test_selection_relevance_fixture_matches_expected_precision_and_recall() -> None:
    states, path_to_id, fixture = _build_fixture_states()
    ranked_ids = [path_to_id[state.path] for state in sorted(states, key=lambda s: s.selection_weight, reverse=True)]
    relevant_ids = set(fixture["relevant_ids"])

    top_1 = ranked_ids[:1]
    top_2 = ranked_ids[:2]

    precision_at_1 = len(relevant_ids.intersection(top_1)) / 1.0
    recall_at_2 = len(relevant_ids.intersection(top_2)) / float(len(relevant_ids))

    assert precision_at_1 == fixture["expected_precision_at_1"]
    assert recall_at_2 == fixture["expected_recall_at_2"]
    assert ranked_ids[0] == "orbital_runtime_core"


def test_orbital_period_estimate_increases_with_radius_for_fixed_mu_eff(tmp_path: Path) -> None:
    orbital_root = tmp_path / "integration" / "Orbital" / "main"
    orbital_root.mkdir(parents=True, exist_ok=True)
    from integration.Orbital.main.bootstrap import ensure_orbital_manifests

    info = ensure_orbital_manifests(orbital_root)
    system = load_system(info["sectors_path"], info["couplings_path"])
    name = next(iter(system.sectors))
    sector = system.sectors[name]

    sector.rho = 0.25
    tau_small = orbital_period_estimate(system, name, mu_eff=1.0)
    sector.rho = 0.60
    tau_large = orbital_period_estimate(system, name, mu_eff=1.0)

    assert tau_large > tau_small > 0.0


def test_phase_slip_readiness_has_explicit_threshold_jump(tmp_path: Path) -> None:
    orbital_root = tmp_path / "integration" / "Orbital" / "main"
    orbital_root.mkdir(parents=True, exist_ok=True)
    from integration.Orbital.main.bootstrap import ensure_orbital_manifests

    info = ensure_orbital_manifests(orbital_root)
    system = load_system(info["sectors_path"], info["couplings_path"])
    name = next(iter(system.sectors))

    assert phase_slip_readiness(system, name, stability=0.60, mismatch=0.10) is False
    assert phase_slip_readiness(system, name, stability=0.40, mismatch=0.10) is True
    assert phase_slip_readiness(system, name, stability=0.40, mismatch=0.01) is False


def test_winding_updates_when_phi_crosses_two_pi_boundary(tmp_path: Path) -> None:
    orbital_root = tmp_path / "integration" / "Orbital" / "main"
    orbital_root.mkdir(parents=True, exist_ok=True)
    from integration.Orbital.main.bootstrap import ensure_orbital_manifests

    info = ensure_orbital_manifests(orbital_root)
    system = load_system(
        info["sectors_path"],
        info["couplings_path"],
        params={
            "use_orbital_law_v0": True,
            "use_relational_lagrangian": False,
            "orbital_phi_gain": 12.0,
        },
    )
    system.couplings = {}

    name = next(iter(system.sectors))
    sector = system.sectors[name]
    sector.phi = (2.0 * math.pi) - 0.01
    sector.rhythm_ratio = 1.0
    sector.winding = 0

    nxt = step(system, dt=1.0)

    assert nxt.sectors[name].winding >= 1
    assert nxt.sectors[name].phi > sector.phi
