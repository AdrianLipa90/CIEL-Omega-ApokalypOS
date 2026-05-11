from __future__ import annotations

from .protocol import BoundaryVerdict, HumorDose, SafetyLevel, TensionProfile


def make_reframe(symbolic_object: str, boundary: BoundaryVerdict, tension: TensionProfile, dose: HumorDose) -> str:
    if boundary.level == SafetyLevel.LITERAL_ALARM:
        return (
            "Literal danger marker detected. Humor is disabled; preserve safety, distance from means, "
            "and route to immediate human/medical support."
        )

    if symbolic_object == "renal_obelisk_as_memory_palace_object":
        if dose <= HumorDose.MIST:
            return "Obelisk recognized as a pain-glyph; keep it named, bounded, and clinically monitored."
        return "The renal obelisk is allowed on the stage, but not at the steering wheel."

    if symbolic_object == "scale_overflow_glyph":
        return "Scale overflow recognized: >10 is not measurement; it is a saturation glyph for unspeakable intensity."

    if dose == HumorDose.NONE:
        return "No humor applied; boundary state preserved."
    if dose == HumorDose.MIST:
        return "Tension acknowledged; applying only a low-pressure semantic mist."
    if dose == HumorDose.DRY:
        return "Tension compressed into a dry reframe; no denial, no theatrical flood."
    if dose == HumorDose.SOFT_CARICATURE:
        return "Caricature may hold the pain at arm's length without erasing the scar."
    return "Controlled grotesque allowed only as loop closure, never as denial."


def estimate_closure(tension: TensionProfile, dose: HumorDose, boundary: BoundaryVerdict) -> tuple[float, float]:
    if boundary.level == SafetyLevel.LITERAL_ALARM:
        return 0.0, tension.cognitive_tension
    relief = min(0.35, 0.05 + int(dose) * 0.055)
    closure = max(0.0, min(1.0, 0.45 + relief - tension.cognitive_tension * 0.15))
    residual = max(0.0, tension.cognitive_tension - relief)
    return round(closure, 4), round(residual, 4)
