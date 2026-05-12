from __future__ import annotations
from typing import Dict, Any


def disambiguate_have(y_type: str, context: str = "") -> Dict[str, str]:
    """Rule-based mode selection for have/mieć.

    This is a deterministic seed layer, not a statistical parser.
    """
    y = y_type.lower()
    if y in {"animal", "object", "tool", "artifact", "property_object"}:
        return {"mode": "alienable_possession", "equation": "Own(x,y)"}
    if y in {"body_part", "component", "part"}:
        return {"mode": "inherent_part", "equation": "HasPart(x,y)"}
    if y in {"property", "measure", "temperature", "color", "size"}:
        return {"mode": "property_assignment", "equation": "HasProperty(x,y)"}
    if y in {"problem", "state", "condition", "disease", "emotion"}:
        return {"mode": "state_attachment", "equation": "HasState(x,y)"}
    if y in {"influence", "relation", "role", "permission"}:
        return {"mode": "relational_role", "equation": "HasRelation(x,y)"}
    return {"mode": "unresolved_have", "equation": "Have(x,y)"}


def disambiguate_how_like_as(syntax_role: str, context: str = "") -> Dict[str, str]:
    """Rule-based mode selection for PL jak / EN how-like-as family."""
    s = syntax_role.lower()
    if s in {"question_manner", "manner_question", "how_question"}:
        return {"mode": "manner_query", "equation": "How(T)->Ask(Manner(T))"}
    if s in {"comparison", "similarity", "simile"}:
        return {"mode": "similarity", "equation": "Like(x,y)->Sim(x,y)"}
    if s in {"role", "role_assignment", "as_role"}:
        return {"mode": "role_mapping", "equation": "As(x,role)->AssignRole(x,role)"}
    if s in {"pattern", "as_before", "template"}:
        return {"mode": "pattern_mapping", "equation": "AsBefore(x)->MapPattern(previous->x)"}
    if s in {"conditional", "temporal_condition", "when_if"}:
        return {"mode": "conditional_temporal", "equation": "WhenIf(S1,S2)"}
    return {"mode": "unresolved_how_like_as", "equation": "HowLikeAs(?)"}
