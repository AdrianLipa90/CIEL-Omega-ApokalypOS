"""
CIEL/Ω — Emergent Ethical Decision Dynamics v5

Ethical decision semantics are derived ONLY from the relational scalar:

    E_rel = R_M * A_rel * S_rel

V36 / M0-M11 are attached as trajectory/provenance channels.
They DO NOT decide moral value and DO NOT break ethical ties unless a future,
independently derived semantic map proves that relation.

This removes the arbitrary coordinate-chart dependency from decision semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

from .relational_medium import RelationalField, EthicalScalarState

@dataclass(frozen=True)
class CandidateAction:
    action_id: str
    intention: Tuple[float, ...]
    predicted_effect: Tuple[float, ...]
    predicted_field: RelationalField
    predicted_stability: float

@dataclass(frozen=True)
class CandidateEvaluation:
    action_id: str
    current_scalar: float
    predicted_scalar: float
    delta_scalar: float
    predicted_state: EthicalScalarState

def evaluate_candidate(
    current: EthicalScalarState,
    candidate: CandidateAction,
) -> Optional[CandidateEvaluation]:
    predicted=EthicalScalarState.derive(
        candidate.predicted_field,
        candidate.intention,
        candidate.predicted_effect,
        candidate.predicted_stability,
    )
    if predicted is None:
        return None
    return CandidateEvaluation(
        action_id=candidate.action_id,
        current_scalar=float(current.value),
        predicted_scalar=float(predicted.value),
        delta_scalar=float(predicted.value-current.value),
        predicted_state=predicted,
    )

@dataclass(frozen=True)
class DecisionResult:
    selected_action_id: Optional[str]
    ranking: Tuple[CandidateEvaluation, ...]
    status: str
    rationale: str

def choose_action(
    current: EthicalScalarState,
    candidates: Sequence[CandidateAction],
) -> DecisionResult:
    """
    Non-arbitrary ethical decision:
      - derive E_rel for each candidate consequence;
      - maximize predicted E_rel;
      - if top E_rel values are exactly indistinguishable, return UNRESOLVED.

    No threshold, name-based rule, V36 distance, insertion order, or action_id
    is allowed to decide an ethical tie.
    """
    evaluated=[e for c in candidates if (e:=evaluate_candidate(current,c)) is not None]
    if not evaluated:
        return DecisionResult(None,tuple(),"UNKNOWN","no derivable candidate consequence")

    ranked=tuple(sorted(evaluated,key=lambda e:-e.predicted_scalar))
    best_value=ranked[0].predicted_scalar
    winners=tuple(e for e in ranked if abs(e.predicted_scalar-best_value) <= 1e-15)

    if len(winners) != 1:
        return DecisionResult(
            None,ranked,"UNRESOLVED",
            "multiple candidates are indistinguishable under the relational ethical scalar"
        )

    return DecisionResult(
        winners[0].action_id,
        ranked,
        "SELECTED",
        "unique maximum of derived relational ethical scalar"
    )

def decision_tree_view(result: DecisionResult) -> Dict[str,object]:
    """Human-readable projection of the same scalar computation; no extra rules."""
    return {
        "root":"current relational field",
        "branches":[
            {
                "action_id":e.action_id,
                "predicted_E_rel":e.predicted_scalar,
                "delta_E_rel":e.delta_scalar,
            }
            for e in result.ranking
        ],
        "selected":result.selected_action_id,
        "status":result.status,
        "rationale":result.rationale,
    }

__all__=[
    "CandidateAction","CandidateEvaluation","DecisionResult",
    "evaluate_candidate","choose_action","decision_tree_view"
]
