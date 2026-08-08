"""Regression tests for information-generator epistemic admission contract."""
import pytest

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.generator_input_contract import (
    InputStatus, ProvenancedScalarInput, GeneratorInputContract,
    CanonicalInputError, assert_canonical_generator_inputs,
    reference_rhythm_input, open_fluctuation_input, derived_killing_expectation_input,
    admission_receipt,
)


def test_reference_rhythm_and_open_fluctuation_block_canon_execution():
    c=GeneratorInputContract(
        derived_killing_expectation_input(2.0,"W=-iL_V; axis supplied"),
        reference_rhythm_input(1.1,"Hilbert-Kahler eq56 reference rule"),
        open_fluctuation_input(0.0,"zero-level law not derived"),
        axis_provenance="seed-selected candidate axis",
    )
    assert c.unresolved_inputs == ("rho_s","delta_I0_expectation")
    assert not c.canon_ready
    with pytest.raises(CanonicalInputError):
        assert_canonical_generator_inputs(c)
    r=admission_receipt(c)
    assert r.decision=="EXPERIMENTAL_ONLY__CANON_BLOCKED"


def test_formal_rhythm_condition_requires_positive_value():
    with pytest.raises(ValueError):
        GeneratorInputContract(
            derived_killing_expectation_input(0.0,"derived"),
            reference_rhythm_input(0.0,"reference"),
            open_fluctuation_input(0.0,"open"),
            axis_provenance="axis",
        )


def test_only_provenance_bearing_admissible_inputs_pass_canon_gate():
    c=GeneratorInputContract(
        ProvenancedScalarInput("W_expectation",1.0,InputStatus.DERIVED,"Killing generator"),
        ProvenancedScalarInput("rho_s",0.8,InputStatus.DERIVED,"future derived rhythm","RHO_CANON_V1"),
        ProvenancedScalarInput("delta_I0_expectation",0.02,InputStatus.MEASURED,"future measured fluctuation","DELTAI0_MEASURED"),
        axis_provenance="derived physical axis receipt",
    )
    assert c.canon_ready
    assert_canonical_generator_inputs(c)
    assert admission_receipt(c).decision=="CANON_EXECUTION_ALLOWED"


def test_conventional_or_fixture_inputs_do_not_become_canonical():
    for status in (InputStatus.CONVENTIONAL,InputStatus.TEST_FIXTURE,InputStatus.UNKNOWN):
        x=ProvenancedScalarInput("rho_s",1.0,status,"fixture provenance")
        assert not x.canon_admissible
