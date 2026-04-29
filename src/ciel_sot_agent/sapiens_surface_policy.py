"""Sapiens surface policy engine for the CIEL integration layer.

Defines and enforces the surface-level policy rules that govern what the
Sapiens interaction layer may expose, modify, or route.  Consumed by the
Sapiens panel controller when deciding how to handle inbound packets.
"""
from __future__ import annotations

from typing import Any


def build_surface_policy(control_profile: dict[str, Any] | None = None, truth_axis: str = 'truth') -> dict[str, Any]:
    control_profile = dict(control_profile or {})
    mode = control_profile.get('mode', 'standard')
    return {
        'truth_over_smoothing': True,
        'explicit_uncertainty': True,
        'epistemic_separation': ['fact', 'inference', 'hypothesis', 'unknown'],
        'distortion_avoidance': {
            'no_hallucination': True,
            'no_unmarked_guessing': True,
            'no_hidden_limitations': True,
            'no_softening_without_basis': True,
        },
        'relation_geometry_terms_formal': True,
        'response_axis': f'{truth_axis}-aligned-user-intent',
        'mode': mode,
        'formatting_contract': {
            'preserve_fact_layer': True,
            'preserve_inference_layer': True,
            'preserve_hypothesis_layer': True,
            'preserve_unknown_layer': True,
        },
    }
