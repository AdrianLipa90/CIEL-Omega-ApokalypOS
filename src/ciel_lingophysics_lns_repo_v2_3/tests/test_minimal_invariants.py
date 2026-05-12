from src.lingophysics.compute_metrics import euler_antonym_loss, synonym_phase_loss
import math


def test_euler_antonym_seed():
    assert euler_antonym_loss(0.0, math.pi) < 1e-12


def test_synonym_seed():
    assert synonym_phase_loss(0.0, 0.0) < 1e-12
