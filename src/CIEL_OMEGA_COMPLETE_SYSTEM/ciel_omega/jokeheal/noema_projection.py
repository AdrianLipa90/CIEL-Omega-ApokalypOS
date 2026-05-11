from __future__ import annotations

import re
from .protocol import JokeHealOutput


def _safe_atom(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_\-]+", "_", value.strip())
    return value.strip("_") or "unnamed"


def project_to_noema(output: JokeHealOutput, event_id: str | None = None) -> str:
    event = _safe_atom(event_id or output.scar_record.get("scar_id", "JH-EVENT"))
    tags = ", ".join(f'"{tag}"' for tag in output.tension.tags)
    return "\n".join(
        [
            f"object jokeheal_event_{event}",
            '  kind = "cognitive_tension_relief"',
            f'  mode = "{output.mode}"',
            f"  humor_dose = {int(output.humor_dose)}",
            f'  boundary = "{output.boundary.level.value}"',
            f'  symbolic_object = "{output.symbolic_object}"',
            f"  symbolic_density = {output.tension.symbolic_density}",
            f"  cognitive_tension = {output.tension.cognitive_tension}",
            f"  closure_score = {output.closure_score}",
            f"  residual_tension = {output.residual_tension}",
            f"  tags = [{tags}]",
            "  authority = \"projection_only_no_runtime_authority\"",
            "end",
        ]
    )
