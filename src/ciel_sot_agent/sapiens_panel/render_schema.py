from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import PanelState


def to_render_dict(state: PanelState) -> dict[str, Any]:
    return asdict(state)
