from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"))

from ciel_omega.htri.htri_matrix import DensePhaseNetwork, build_all_to_all_matrix, build_grid_matrix, build_ring_matrix
from ciel_omega.htri.htri_local import LocalHTRI, OscillatorBank


def test_all_to_all_matrix_is_symmetric_and_zero_diagonal() -> None:
    mat = build_all_to_all_matrix(5, 0.3)
    assert np.allclose(mat, mat.T)
    assert np.allclose(np.diag(mat), 0.0)
    assert mat[0, 1] == pytest.approx(0.3)


def test_ring_matrix_only_connects_requested_neighbours() -> None:
    mat = build_ring_matrix(6, 0.4, nearest=1)
    assert mat[0, 1] == pytest.approx(0.4)
    assert mat[0, 2] == pytest.approx(0.0)
    assert np.allclose(mat, mat.T)


def test_grid_matrix_is_dense_and_distance_weighted() -> None:
    mat = build_grid_matrix(3, 2, 0.9)
    assert mat.shape == (6, 6)
    assert np.allclose(mat, mat.T)
    assert np.allclose(np.diag(mat), 0.0)
    assert mat[0, 1] > mat[0, 2]


def test_dense_network_zero_phases_has_zero_potential() -> None:
    net = DensePhaseNetwork(n=4, dt=0.01, kappa=0.2)
    net.omegas[:] = 0.0
    net.phases[:] = 0.0
    snap = net.snapshot()
    assert snap["potential"] == pytest.approx(0.0)
    assert snap["coherence"] == pytest.approx(0.0)

    net.step()
    snap2 = net.snapshot()
    assert snap2["coherence"] == pytest.approx(1.0)
    assert snap2["potential"] == pytest.approx(0.0)


def test_dense_network_coupling_changes_the_state_and_reduces_coherence() -> None:
    net = DensePhaseNetwork(n=2, dt=0.05, kappa=3.0)
    net.omegas[:] = 0.0
    net.phases[:] = np.array([0.0, 1.0])
    before = abs(np.mean(np.exp(1j * net.phases)))
    initial_potential = net.potential_energy()
    for _ in range(25):
        net.step()
    after = net.snapshot()["coherence"]
    final_potential = net.potential_energy()
    assert after < before
    assert final_potential > initial_potential
    assert np.max(np.abs(net.sigma)) > 0.0


def test_oscillator_bank_and_local_htri_expose_matrix_metrics() -> None:
    bank = OscillatorBank(n=8, kappa=0.2, dt=0.01)
    report = bank.run(steps=3)
    assert report["n_oscillators"] == 8
    assert "potential" in report
    assert "spectral_radius" in report
    assert report["coherence"] >= 0.0

    local = LocalHTRI()
    combined = local.run(cpu_steps=2, gpu_steps=2)
    assert combined["combined"]["total_oscillators"] == 780
    assert "potential" in combined["combined"]
    assert "spectral_radius" in combined["combined"]
