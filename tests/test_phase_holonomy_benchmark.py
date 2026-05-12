from __future__ import annotations

from src.ciel_sot_agent.phase_holonomy_benchmark import run_phase_holonomy_benchmark


def test_phase_holonomy_benchmark_reports_stable_sector_fits() -> None:
    report = run_phase_holonomy_benchmark(
        [
            {
                "name": "proximal_case",
                "prompt": "Here now we preserve memory and truth.",
                "language": "en",
            },
            {
                "name": "distal_case",
                "prompt": "There then the signal returns and that matters.",
                "language": "en",
            },
        ],
        n_trials=32,
        strength=0.18,
        seed=7,
    )

    assert report["summary"]["case_count"] == 2
    assert report["summary"]["sample_count"] == 64
    assert report["summary"]["pass"] is True
    assert report["summary"]["global_fit_rate"] >= 0.99
    assert report["summary"]["mean_fit_rate"] >= 0.99
    assert {case["baseline"]["sector"] for case in report["cases"]} == {"proximal", "distal"}
    assert all(case["fit_rate"] >= 0.99 for case in report["cases"])


def test_phase_holonomy_benchmark_exposes_tau_and_imaginal_signals() -> None:
    report = run_phase_holonomy_benchmark(
        [
            {
                "name": "mobius_case",
                "prompt": "Here the path bends, then returns there with a twist.",
                "language": "en",
            }
        ],
        n_trials=16,
        strength=0.12,
        seed=11,
    )

    case = report["cases"][0]
    assert case["mean_tau_gradient_mean"] >= 0.0
    assert 0.0 <= case["mean_imaginal_drive"] <= 1.0
    assert case["baseline"]["phase_confidence"] >= 0.0
    assert "samples" in case and len(case["samples"]) == 16
