from __future__ import annotations

from typing import Any


def build_support_view(bridge_summary: dict[str, Any], paths: dict[str, str] | None = None) -> dict[str, Any]:
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
    }
