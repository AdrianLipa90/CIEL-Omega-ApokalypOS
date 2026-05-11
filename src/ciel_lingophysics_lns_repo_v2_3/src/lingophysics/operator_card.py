from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class OperatorSurface:
    code: str
    lemma: str
    forms: List[str]
    examples: List[str]
    notes: str


@dataclass
class OperatorCard:
    operator_id: str
    family: str
    classes: List[str]
    symbol: str
    arity: str
    equations: List[str]
    surfaces: Dict[str, OperatorSurface]
    dual: Optional[str] = None
    inverse: Optional[str] = None

    def is_functional(self) -> bool:
        return True

    def language_complete(self, code: str) -> bool:
        surface = self.surfaces[code]
        return bool(surface.lemma and surface.forms and surface.examples)

    def is_dual_of(self, other_id: str) -> bool:
        return self.dual == other_id or self.inverse == other_id


def classify_word_card(pos: str, classes: List[str] | None = None) -> str:
    """Return CIEL card layer for a linguistic item.

    A word is not automatically a concept. Some words are semantic bodies;
    others are operators, relations, deictics, logic gates or grammar functions.
    """
    classes = classes or []
    pos_u = pos.upper()
    if pos_u in {"NOUN", "PROPN"} and not any(c.endswith("_operator") for c in classes):
        return "CONCEPT_CARD"
    if pos_u in {"ADP", "SCONJ", "CCONJ", "PART", "AUX"}:
        return "OPERATOR_CARD"
    if any(c in classes for c in ["logic_operator", "spatial_relation", "temporal_relation", "query_operator"]):
        return "OPERATOR_CARD"
    if pos_u == "VERB":
        return "TRANSFORM_OPERATOR_OR_EVENT_CARD"
    return "UNRESOLVED_CARD_TYPE"


def dual_containment_invariant(sentence_a: str, sentence_b: str) -> Dict[str, Any]:
    """Minimal placeholder invariant for examples like:
    'Water is in the glass' and 'The glass contains water'.
    """
    return {
        "sentences": [sentence_a, sentence_b],
        "core_relation": "Containment(x,y)",
        "dual_forms": ["Inside(x,y)", "Contains(y,x)"],
        "surface_equal": False,
        "topological_invariant_equal": True,
    }
