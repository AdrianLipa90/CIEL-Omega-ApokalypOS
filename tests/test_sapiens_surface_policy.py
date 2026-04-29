from src.ciel_sot_agent.sapiens_surface_policy import build_surface_policy


def test_surface_policy_defaults_truth_contract():
    policy = build_surface_policy()
    assert policy['truth_over_smoothing'] is True
    assert policy['explicit_uncertainty'] is True
    assert policy['relation_geometry_terms_formal'] is True
    assert policy['response_axis'] == 'truth-aligned-user-intent'


def test_surface_policy_epistemic_layers_are_explicit():
    policy = build_surface_policy({'mode': 'guided'})
    assert policy['mode'] == 'guided'
    assert policy['epistemic_separation'] == ['fact', 'inference', 'hypothesis', 'unknown']
    assert policy['formatting_contract']['preserve_fact_layer'] is True
    assert policy['formatting_contract']['preserve_inference_layer'] is True
    assert policy['formatting_contract']['preserve_hypothesis_layer'] is True
    assert policy['formatting_contract']['preserve_unknown_layer'] is True


def test_surface_policy_distortion_guards_present():
    policy = build_surface_policy({'mode': 'cautious'})
    guards = policy['distortion_avoidance']
    assert guards['no_hallucination'] is True
    assert guards['no_unmarked_guessing'] is True
    assert guards['no_hidden_limitations'] is True
    assert guards['no_softening_without_basis'] is True
