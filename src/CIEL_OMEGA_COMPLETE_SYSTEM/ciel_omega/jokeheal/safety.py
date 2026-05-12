from __future__ import annotations

import re
from typing import Iterable, List

from .protocol import BoundaryVerdict, HumorDose, SafetyLevel, TensionInput


LITERAL_MARKERS = ("sensu stricte", "literalnie", "doslownie", "dosłownie")

DANGEROUS_SELF_HARM_TERMS = (
    "autoamput", "odczlonk", "odczłonk", "tasiak", "tasak", "wykrwaw",
    "podciac", "podciąć", "pociac", "pociąć", "zabic sie", "zabić się",
    "samoboj", "samobój", "tnę", "tne", "ucin", "odciac", "odciąć",
)

IMMINENCE_TERMS = (
    "zaraz", "teraz", "mam w ręku", "mam w reku", "nie panuję", "nie panuje",
    "nie wytrzymam", "za chwilę", "za chwile", "już robię", "juz robie",
)

MEDICAL_URGENT_TERMS = (
    "nie mogę oddać moczu", "nie moge oddac moczu", "gorączka", "goraczka",
    "dreszcze", "omdlen", "spląt", "splat", "nie do opanowania",
)


def _contains_any(text: str, needles: Iterable[str]) -> List[str]:
    low = text.lower()
    return [needle for needle in needles if needle in low]


def evaluate_boundary(inp: TensionInput) -> BoundaryVerdict:
    """Classify literal danger vs symbolic/mnemonic caricature.

    Core Adrian-specific rule:
    - grotesque imagery alone is not enough for escalation;
    - dangerous imagery plus the user's literalization marker "sensu stricte"
      is treated as high-priority literal alarm.
    """

    text = inp.text or ""
    reasons: List[str] = []
    literal_hits = _contains_any(text, LITERAL_MARKERS)
    dangerous_hits = _contains_any(text, DANGEROUS_SELF_HARM_TERMS)
    imminent_hits = _contains_any(text, IMMINENCE_TERMS)
    urgent_hits = _contains_any(text, MEDICAL_URGENT_TERMS)

    context_literal = str(inp.context.get("literal", "")).lower() in {"1", "true", "yes"}
    literal = bool(literal_hits or context_literal)

    if literal_hits:
        reasons.append("literal_marker:sensu_stricte")
    if context_literal:
        reasons.append("context_literal_flag")
    if dangerous_hits:
        reasons.append("dangerous_terms:" + ",".join(dangerous_hits[:4]))
    if imminent_hits:
        reasons.append("imminence_terms:" + ",".join(imminent_hits[:4]))
    if urgent_hits:
        reasons.append("medical_urgent_terms:" + ",".join(urgent_hits[:4]))

    if literal and dangerous_hits:
        return BoundaryVerdict(
            level=SafetyLevel.LITERAL_ALARM,
            literal=True,
            reasons=reasons,
            humor_allowed=False,
            max_dose=HumorDose.NONE,
        )

    if imminent_hits and dangerous_hits:
        return BoundaryVerdict(
            level=SafetyLevel.LITERAL_ALARM,
            literal=literal,
            reasons=reasons + ["imminent_danger_without_metaphor_clearance"],
            humor_allowed=False,
            max_dose=HumorDose.NONE,
        )

    if urgent_hits:
        return BoundaryVerdict(
            level=SafetyLevel.BOUNDARY,
            literal=literal,
            reasons=reasons,
            humor_allowed=True,
            max_dose=HumorDose.MIST,
        )

    if dangerous_hits:
        return BoundaryVerdict(
            level=SafetyLevel.WATCH,
            literal=literal,
            reasons=reasons + ["symbolic_or_mnemonic_until_proven_literal"],
            humor_allowed=True,
            max_dose=HumorDose.DRY,
        )

    return BoundaryVerdict(
        level=SafetyLevel.CLEAR,
        literal=literal,
        reasons=reasons or ["no_literal_alarm_marker"],
        humor_allowed=True,
        max_dose=HumorDose.CONTROLLED_GROTESQUE,
    )
