"""Regression tests for relational autonomy v7."""
from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.relational_autonomy import (
    ConsentStatus, ConsentEvidence, active_consent,
    InformationAccess, information_asymmetry,
    AgencyEvidence, CoercionEvidence,
    derive_autonomy_profile, AutonomyConsequence,
    autonomy_dominates, choose_with_autonomy,
)


def test_explicit_refusal_is_not_overridden_by_predicted_benefit():
    ev=[ConsentEvidence("p",ConsentStatus.REFUSED,2.0,"explicit")]
    p=derive_autonomy_profile("p",ev)
    assert p.consent == ConsentStatus.REFUSED


def test_unknown_consent_does_not_become_affirmed():
    p=derive_autonomy_profile("p",[])
    assert p.consent == ConsentStatus.UNKNOWN


def test_withdrawal_supersedes_prior_affirmation_but_history_remains():
    ev=[
        ConsentEvidence("p",ConsentStatus.AFFIRMED,1.0,"record-1"),
        ConsentEvidence("p",ConsentStatus.WITHDRAWN,2.0,"record-2"),
    ]
    assert len(ev)==2
    assert active_consent(ev,"p").status == ConsentStatus.WITHDRAWN


def test_information_asymmetry_is_exact_set_observable():
    a=InformationAccess.from_sets("a",{"x","y","z"},{"x","y"},"a-src")
    b=InformationAccess.from_sets("b",{"x","y","z"},{"x","z"},"b-src")
    r=information_asymmetry(a,b)
    assert r.a_missing_not_b == frozenset({"z"})
    assert r.b_missing_not_a == frozenset({"y"})
    assert r.jaccard_access_overlap == 1/3


def test_coercion_is_counterfactual_evidence_not_outcome_inference():
    c=CoercionEvidence(
        "p","refuse","penalty",frozenset({"alternative"}),None,"causal-record"
    )
    assert c.has_coercive_constraint
    assert "THREAT_CONTINGENT_ON_REFUSAL" in c.indicators
    assert "ALTERNATIVES_REMOVED" in c.indicators


def test_voluntary_profile_dominates_otherwise_equal_refused_coerced_profile():
    ag=AgencyEvidence.from_sets("p",{"yes","no"},{"yes","no"},"agency")
    info=InformationAccess.from_sets("p",{"terms"},{"terms"},"info")
    voluntary=derive_autonomy_profile(
        "p",[ConsentEvidence("p",ConsentStatus.AFFIRMED,1.0,"consent")],
        agency=ag, information=info,
        coercion=CoercionEvidence("p","no",None,frozenset(),None,"none"),
    )
    coerced=derive_autonomy_profile(
        "p",[ConsentEvidence("p",ConsentStatus.REFUSED,1.0,"refusal")],
        agency=ag, information=info,
        coercion=CoercionEvidence("p","no","penalty",frozenset(),None,"threat"),
    )
    a=AutonomyConsequence("voluntary",(voluntary,))
    b=AutonomyConsequence("coerced",(coerced,))
    assert autonomy_dominates(a,b)
    d=choose_with_autonomy([a,b],{"voluntary":0.1,"coerced":0.9})
    assert d.selected_action_id == "voluntary"


def test_scalar_gain_cannot_compensate_incomparable_autonomy_tradeoff():
    p1=derive_autonomy_profile(
        "p",[ConsentEvidence("p",ConsentStatus.AFFIRMED,1.0,"c")],
        agency=AgencyEvidence.from_sets("p",{"a","b"},{"a"},"ag1"),
        information=InformationAccess.from_sets("p",{"x","y"},{"x"},"i1"),
        coercion=CoercionEvidence("p","b",None,frozenset(),None,"no-c"),
    )
    p2=derive_autonomy_profile(
        "p",[ConsentEvidence("p",ConsentStatus.AFFIRMED,1.0,"c")],
        agency=AgencyEvidence.from_sets("p",{"a"},{"a"},"ag2"),
        information=InformationAccess.from_sets("p",{"x","y"},{"x","y"},"i2"),
        coercion=CoercionEvidence("p","a",None,frozenset(),None,"no-c"),
    )
    d=choose_with_autonomy(
        [AutonomyConsequence("more-options",(p1,)),AutonomyConsequence("more-info",(p2,))],
        {"more-options":0.1,"more-info":0.9},
    )
    assert d.status == "UNRESOLVED"
    assert d.selected_action_id is None
