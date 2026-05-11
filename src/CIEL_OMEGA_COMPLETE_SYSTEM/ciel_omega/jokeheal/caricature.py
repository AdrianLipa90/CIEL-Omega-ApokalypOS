from __future__ import annotations

from .protocol import HumorDose, TensionInput, TensionProfile


def build_symbolic_object(inp: TensionInput, tension: TensionProfile, dose: HumorDose) -> str:
    text = (inp.text or "").lower()
    if "kamie" in text or "nerk" in text or "obelisk" in text:
        return "renal_obelisk_as_memory_palace_object"
    if tension.pain_overflow:
        return "scale_overflow_glyph"
    if tension.grotesque_caricature:
        return "controlled_grotesque_caricature"
    if tension.mnemonic_likely:
        return "mnemonic_loop_object"
    if dose == HumorDose.NONE:
        return "literal_boundary_marker"
    return "soft_tension_knot"
