"""Regression tests for the explicitly noncanonical source-reference rhythm."""
import math
import pytest

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.reference_collatz_rhythm import (
    validate_twin_prime_seed, paired_collatz_state, reference_rho_from_pair,
    reference_rho, reference_rhythm_receipt, reference_rhythm_contract_input,
)
from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.generator_input_contract import InputStatus


def test_twin_prime_seed_validation():
    assert validate_twin_prime_seed(11)==(11,13)
    with pytest.raises(ValueError):
        validate_twin_prime_seed(7)


def test_paired_orbit_uses_each_twin_prime_branch():
    assert paired_collatz_state(11,0)==(11,13)
    assert paired_collatz_state(11,1)==(34,40)
    assert paired_collatz_state(11,2)==(17,20)


def test_reference_eq56_is_exactly_implemented():
    a,b=17,20
    expected=(math.log1p(a)+math.log1p(b))/(1+math.log1p(a+b))
    assert reference_rho_from_pair(a,b)==expected
    assert reference_rho(11,2)==expected


def test_receipt_never_promotes_reference_rule():
    r=reference_rhythm_receipt(11,3)
    assert r.status=="SOURCE_REFERENCE_RULE_EXECUTABLE"
    assert r.canonical_law_status=="OPEN_NOT_PROMOTED"
    assert r.rho_s>0


def test_contract_wrapper_is_explicitly_noncanonical():
    x=reference_rhythm_contract_input(11,4)
    assert x.name=="rho_s"
    assert x.status==InputStatus.REFERENCE_RULE
    assert not x.canon_admissible
    assert x.law_id=="HILBERT_KAHLER_EQ56_REFERENCE_ONLY"
