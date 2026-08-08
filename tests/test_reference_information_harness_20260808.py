"""Regression tests for end-to-end noncanonical reference information harness."""
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.reference_information_harness import run_reference_information_step
from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.information_phase_generator import KAPPA_INFORMATION


def test_reference_harness_executes_full_seed_to_phase_offset_chain_but_is_blocked():
    # Pure m=2 mode => <W>=2 exactly.
    step=run_reference_information_step(
        seed_p=11,k=2,
        coefficients=[0.0,0.0,1.0],mode_indices=[-1,0,2],
        delta_I0_expectation=0.1,hbar=1.5,
        axis_provenance="candidate Berry axis",
    )
    assert step.seed==(11,13)
    assert step.paired_state==(17,20)
    assert step.W_expectation==2.0
    expected_I=2*KAPPA_INFORMATION+0.1
    assert np.isclose(step.information_generator_expectation,expected_I)
    assert np.isclose(step.intention_phase_increment,step.rho_s*expected_I)
    assert np.isclose(step.J0_phase_offset,1.5*step.rho_s*expected_I)
    assert not step.canon_ready
    assert step.admission_decision=="EXPERIMENTAL_ONLY__CANON_BLOCKED"
    assert step.status=="REFERENCE_EXPERIMENT_EXECUTABLE__CANON_BLOCKED"


def test_reference_harness_does_not_depend_on_target_delta_or_sigma():
    # Inputs contain no preregistered 0.1% or 6.3 sigma target parameters.
    step=run_reference_information_step(
        seed_p=5,k=1,
        coefficients=[1.0,0.0],mode_indices=[-2,3],
        delta_I0_expectation=0.0,hbar=1.0,
        axis_provenance="fixture axis",
    )
    assert step.W_expectation==-2.0
    assert step.status.endswith("CANON_BLOCKED")
