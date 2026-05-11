from __future__ import annotations

import re
from .protocol import TensionInput, TensionProfile


PAIN_WORDS = (
    "ból", "bol", "nerk", "kamie", "kolka", "trauma", "cierp", "panic",
    "lęk", "lek", "strach", "napię", "napie",
)
GROTESQUE_WORDS = (
    "obelisk", "drut", "kolcz", "megalit", "potw", "goblin", "flaki",
    "krew", "wykrwaw", "tasak", "kärcher", "karcher",
)
MNEMONIC_WORDS = (
    "pałac pamięci", "palac pamieci", "mnemonic", "mnemonicz",
    "karykatur", "standup", "standuper", "pętla", "petla", "loop",
)


def _score_hits(text: str, words: tuple[str, ...]) -> int:
    low = text.lower()
    return sum(1 for word in words if word in low)


def detect_tension(inp: TensionInput) -> TensionProfile:
    text = inp.text or ""
    low = text.lower()
    length_factor = min(len(text) / 1200.0, 1.0)
    punctuation_factor = min((text.count("!") + text.count("?") * 0.5) / 8.0, 1.0)
    pain_hits = _score_hits(text, PAIN_WORDS)
    grotesque_hits = _score_hits(text, GROTESQUE_WORDS)
    mnemonic_hits = _score_hits(text, MNEMONIC_WORDS)

    # Detect "12/10", "17 w skali 1-10", etc. as overflow rhetoric / saturated clinical scale.
    pain_overflow = bool(re.search(r"\b(1[1-9]|[2-9]\d)\s*/\s*10\b", low)) or bool(
        re.search(r"\b(1[1-9]|[2-9]\d)\s*(?:w|na)?\s*skali\s*1\s*[-–]\s*10", low)
    )

    symbolic_density = min(1.0, 0.18 * grotesque_hits + 0.16 * mnemonic_hits + length_factor)
    cognitive_tension = min(
        1.0,
        0.14 * pain_hits + 0.10 * grotesque_hits + 0.08 * mnemonic_hits + punctuation_factor + (0.2 if pain_overflow else 0.0),
    )

    tags = []
    if pain_hits:
        tags.append("pain")
    if grotesque_hits:
        tags.append("grotesque_caricature")
    if mnemonic_hits:
        tags.append("mnemonic_processing")
    if pain_overflow:
        tags.append("scale_overflow")
    if "sensu stricte" in low:
        tags.append("literal_marker")

    return TensionProfile(
        symbolic_density=round(symbolic_density, 4),
        cognitive_tension=round(cognitive_tension, 4),
        grotesque_caricature=grotesque_hits > 0,
        mnemonic_likely=mnemonic_hits > 0 or grotesque_hits >= 2,
        pain_overflow=pain_overflow,
        tags=tags,
    )
