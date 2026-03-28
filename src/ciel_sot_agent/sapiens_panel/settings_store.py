from __future__ import annotations

import json
from pathlib import Path

from .models import PanelSettings


def load_panel_settings(root: str | Path) -> PanelSettings:
    root = Path(root)
    path = root / 'integration' / 'sapiens' / 'settings_defaults.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    return PanelSettings(
        identity=dict(data.get('identity', {})),
        interaction_policy=dict(data.get('interaction_policy', {})),
        orbital_runtime=dict(data.get('orbital_runtime', {})),
        reduction_policy=dict(data.get('reduction_policy', {})),
        ui=dict(data.get('ui', {})),
    )
