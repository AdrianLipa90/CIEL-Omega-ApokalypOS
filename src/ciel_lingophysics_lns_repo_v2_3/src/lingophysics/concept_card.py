from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class LanguageSurface:
    code: str
    lemma: str
    pos: str
    synonyms: List[str]
    antonyms: List[str]
    forms: List[str]
    contexts: List[str]
    operators: Dict[str, str]


@dataclass
class ConceptCard:
    concept_id: str
    canonical_label: str
    semantic_mass: float
    languages: Dict[str, LanguageSurface]
    relations: List[Dict[str, Any]]

    def required_language_complete(self, code: str) -> bool:
        surface = self.languages[code]
        return bool(surface.lemma and surface.pos and surface.forms and surface.contexts and surface.operators)

    def antonym_phase_constraint(self, epsilon: float = 0.2) -> bool:
        # Placeholder invariant: every language surface must contain at least one antonym axis seed.
        return all(len(surface.antonyms) > 0 for surface in self.languages.values())
