from __future__ import annotations

from pathlib import Path
from typing import Any

from ..satellite_authority import require_interaction_surface, project_authority_summary


def build_support_view(bridge_summary: dict[str, Any], paths: dict[str, str] | None = None, *, root: str | Path | None = None) -> dict[str, Any]:
    root = Path(root) if root is not None else Path(__file__).resolve().parents[3]
    authority = project_authority_summary(require_interaction_surface(root, 'SAT-SAPIENS-0001'))
    return {
        'health_manifest': bridge_summary.get('health_manifest', {}),
        'recommended_control': bridge_summary.get('recommended_control', {}),
        'source_paths': bridge_summary.get('source_paths', {}),
        'artifact_paths': paths or {},
        'recommended_actions': [
            'Run Bridge Update',
            'Rebuild Manifests',
            'Export Current Bundle',
            'Reset Session',
        ],
        'satellite_authority': authority,
    }
