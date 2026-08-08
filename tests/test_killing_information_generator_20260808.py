"""Regression tests for the formal Bloch Killing information generator W_s."""
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.killing_information_generator import (
    fourier_killing_operator, killing_expectation, apply_killing_operator,
    is_hermitian_operator, generator_receipt,
)


def test_fourier_modes_are_exact_killing_eigenmodes():
    modes=(-2,-1,0,1,2)
    W=fourier_killing_operator(modes)
    for j,m in enumerate(modes):
        e=np.zeros(len(modes),dtype=complex); e[j]=1.0
        assert np.allclose(apply_killing_operator(e,modes),m*e)
    assert is_hermitian_operator(W)


def test_pure_mode_expectation_equals_integer_mode_number():
    modes=(-3,-1,2,5)
    for j,m in enumerate(modes):
        c=np.zeros(len(modes),dtype=complex); c[j]=1.0j
        assert killing_expectation(c,modes)==float(m)


def test_superposition_expectation_is_probability_weighted_mode_mean():
    modes=(-1,1)
    c=np.array([1.0,2.0j])
    expected=(-1*1 + 1*4)/5
    assert np.isclose(killing_expectation(c,modes),expected)


def test_axis_selection_remains_explicit_model_input():
    r=generator_receipt((-1,0,1),axis_provenance="Berry-axis candidate fixture")
    assert r.hermitian
    assert r.generator_status=="CONDITIONALLY_CLOSED_FORMAL_GEOMETRIC_GENERATOR"
    assert r.axis_selection_status=="SUPPLIED_MODEL_SELECTION__NOT_DERIVED_HERE"
