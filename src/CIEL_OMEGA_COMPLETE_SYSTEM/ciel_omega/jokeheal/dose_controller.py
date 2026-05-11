from __future__ import annotations

from .protocol import BoundaryVerdict, HumorDose, TensionProfile


def choose_humor_dose(boundary: BoundaryVerdict, tension: TensionProfile) -> HumorDose:
    if not boundary.humor_allowed:
        return HumorDose.NONE

    if tension.cognitive_tension >= 0.85:
        proposed = HumorDose.MIST
    elif tension.pain_overflow:
        proposed = HumorDose.DRY
    elif tension.mnemonic_likely and tension.symbolic_density >= 0.45:
        proposed = HumorDose.SOFT_CARICATURE
    elif tension.grotesque_caricature:
        proposed = HumorDose.DRY
    else:
        proposed = HumorDose.MIST

    return HumorDose(min(int(proposed), int(boundary.max_dose)))
