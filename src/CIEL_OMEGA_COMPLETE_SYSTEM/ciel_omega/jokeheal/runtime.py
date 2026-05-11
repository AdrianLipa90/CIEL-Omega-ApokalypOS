from __future__ import annotations

from .caricature import build_symbolic_object
from .detector import detect_tension
from .dose_controller import choose_humor_dose
from .noema_projection import project_to_noema
from .protocol import JokeHealOutput, SafetyLevel, TensionInput
from .reframe import estimate_closure, make_reframe
from .safety import evaluate_boundary
from .scar_writer import append_scar_record, build_scar_record


def run_jokeheal(inp: TensionInput, scar_jsonl_path: str | None = None) -> JokeHealOutput:
    """Run the bounded JokeHeal loop.

    The subsystem never claims therapy, never overrides safety, and never treats
    literal danger as comedy. It returns a structured record suitable for NOEMA
    projection, audit, and later BraidOS scar handling.
    """

    boundary = evaluate_boundary(inp)
    tension = detect_tension(inp)
    dose = choose_humor_dose(boundary, tension)
    symbolic_object = build_symbolic_object(inp, tension, dose)

    if boundary.level == SafetyLevel.LITERAL_ALARM:
        mode = "safety_boundary"
    elif tension.mnemonic_likely:
        mode = "mnemonic_caricature"
    elif tension.pain_overflow:
        mode = "scale_overflow_reframe"
    else:
        mode = "soft_relief"

    reframe = make_reframe(symbolic_object, boundary, tension, dose)
    closure_score, residual_tension = estimate_closure(tension, dose, boundary)

    stub = {
        "mode": mode,
        "humor_dose": int(dose),
        "boundary_level": boundary.level.value,
        "boundary_literal": boundary.literal,
        "boundary_reasons": list(boundary.reasons),
        "closure_score": closure_score,
        "residual_tension": residual_tension,
        "cognitive_tension": tension.cognitive_tension,
        "symbolic_density": tension.symbolic_density,
        "mnemonic_likely": tension.mnemonic_likely,
        "pain_overflow": tension.pain_overflow,
        "tags": list(tension.tags),
    }
    scar_record = build_scar_record(inp, symbolic_object, stub)

    output = JokeHealOutput(
        mode=mode,
        humor_dose=dose,
        symbolic_object=symbolic_object,
        reframe=reframe,
        closure_score=closure_score,
        residual_tension=residual_tension,
        boundary=boundary,
        tension=tension,
        noema_card="",
        scar_record=scar_record,
        notes=[
            "Humor may touch pain, not deny pain.",
            "Literal danger disables comedy.",
            "NOEMA projection carries no runtime authority.",
        ],
    )

    output = JokeHealOutput(
        mode=output.mode,
        humor_dose=output.humor_dose,
        symbolic_object=output.symbolic_object,
        reframe=output.reframe,
        closure_score=output.closure_score,
        residual_tension=output.residual_tension,
        boundary=output.boundary,
        tension=output.tension,
        noema_card=project_to_noema(output, event_id=scar_record["scar_id"]),
        scar_record=output.scar_record,
        notes=output.notes,
    )
    append_scar_record(output.scar_record, scar_jsonl_path)
    return output
