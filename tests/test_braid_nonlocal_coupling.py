from __future__ import annotations

import json
import subprocess
import sys
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OMEGA_ROOT = ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega"
if str(OMEGA_ROOT) not in sys.path:
    sys.path.insert(0, str(OMEGA_ROOT))

from core.braid.nonlocal_coupling import (
    build_orbital_braid_diagnostics,
    compute_trace_to_nonlocal_coupling,
    compute_summary_to_nonlocal_coupling,
    domain_profile_for,
)


def test_trace_coupling_adjusts_metadata() -> None:
    payload = compute_trace_to_nonlocal_coupling(
        {
            "domain": "orbital",
            "coherence": 0.9,
            "avg_contradiction": 0.2,
            "scar_count": 1,
            "available_budget": 0.7,
        },
        base_metadata={"salience": 0.7, "confidence": 0.6, "novelty": 0.5},
    )
    assert payload["active"] is True
    adjusted = payload["adjusted_metadata"]
    assert adjusted["domain"] == "orbital"
    assert 0.0 <= adjusted["salience"] <= 1.0
    assert 0.0 <= adjusted["confidence"] <= 1.0
    assert 0.0 <= adjusted["novelty"] <= 1.0
    assert payload["cards"]


def test_domain_profiles_shift_summary_weights() -> None:
    summary = {
        "loop_count": 4,
        "scar_count": 1,
        "coherence": 0.8,
        "mean_phasor_abs": 0.9,
        "drift": {"norm": 0.2},
        "scar_taxonomy": {"repair": 1},
    }
    orbital_payload = compute_summary_to_nonlocal_coupling(
        {**summary, "domain": "orbital"},
        eba_results={"L0": {"is_coherent": True, "defect_magnitude": 0.1, "phi_ab": 0.2, "phi_berry": 0.3}},
    )
    ethics_payload = compute_summary_to_nonlocal_coupling(
        {**summary, "domain": "ethics"},
        eba_results={"L0": {"is_coherent": True, "defect_magnitude": 0.1, "phi_ab": 0.2, "phi_berry": 0.3}},
    )
    assert orbital_payload["domain_profile"]["key"] == "orbital"
    assert ethics_payload["domain_profile"]["key"] == "ethics"
    assert orbital_payload["weights"]["closure_weight"] != ethics_payload["weights"]["closure_weight"]


def test_summary_coupling_exposes_cards_and_taxonomy() -> None:
    payload = compute_summary_to_nonlocal_coupling(
        {
            "domain": "memory",
            "loop_count": 6,
            "scar_count": 2,
            "scar_taxonomy": {"fray": 2},
            "dominant_scar_class": "fray",
            "coherence": 0.8,
            "mean_phasor_abs": 0.9,
            "drift": {"norm": 0.7},
        },
        eba_results={
            "L0": {"is_coherent": True, "defect_magnitude": 0.1, "phi_ab": 0.2, "phi_berry": 0.3},
            "L1": {"is_coherent": False, "defect_magnitude": 0.4, "phi_ab": 0.5, "phi_berry": 0.6},
        },
    )
    assert payload["active"] is True
    assert payload["drift_class"] == "elevated"
    assert payload["dominant_scar_class"] == "fray"
    assert payload["cards"]
    assert payload["cards"][0]["card_id"].startswith("BNC-")


def test_orbital_diagnostics_consumes_cards() -> None:
    coupling = compute_summary_to_nonlocal_coupling(
        {
            "domain": "orbital",
            "loop_count": 5,
            "scar_count": 3,
            "scar_taxonomy": {"rupture": 2, "fray": 1},
            "coherence": 0.45,
            "mean_phasor_abs": 0.55,
            "drift": {"norm": 1.4},
        },
        eba_results={"L0": {"is_coherent": False, "defect_magnitude": 1.3, "phi_ab": 0.8, "phi_berry": 1.0}},
    )
    diag = build_orbital_braid_diagnostics(coupling, closure_score=0.22)
    assert diag["active"] is True
    assert diag["status"] in {"watch", "intervene", "stable"}
    assert diag["recommended_mode"]
    assert diag["top_card_ids"]


def test_unified_cycle_exposes_braid_nonlocal_coupling() -> None:
    if not (OMEGA_ROOT / "bootstrap_runtime.py").exists():
        pytest.skip("snapshot missing bootstrap_runtime.py; skipping executable surface smoke test")
    proc = subprocess.run(
        [
            sys.executable,
            str(OMEGA_ROOT / "unified_system.py"),
            "--mode",
            "cycle",
            "--text",
            "braid nonlocal coupling runtime visibility",
        ],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert "braid_nonlocal_coupling" in payload
    assert "cards" in payload["braid_nonlocal_coupling"]
    euler_metrics = payload.get("engine_euler_bridge", {}).get("euler_metrics", {})
    assert "braid_weighted_closure" in euler_metrics
