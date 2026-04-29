"""Authority loading and lookup for satellite subsystems.

Satellite subsystems live beyond the bridge horizon and must not silently
override canonical runtime state. This module centralizes the authority
matrix so code surfaces can read, expose, and enforce the same rules.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import resolve_project_root

AUTHORITY_MATRIX_PATH = Path('integration') / 'registries' / 'satellite_subsystem_authority_matrix.json'


def load_satellite_authority_matrix(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    path = root / AUTHORITY_MATRIX_PATH
    if not path.exists():
        return {'schema': 'ciel-sot-agent/satellite-subsystem-authority/v0.1', 'matrix': []}
    return json.loads(path.read_text(encoding='utf-8'))


def get_satellite_authority(root: str | Path, subsystem_id: str) -> dict[str, Any]:
    matrix = load_satellite_authority_matrix(root)
    for row in matrix.get('matrix', []):
        if row.get('subsystem_id') == subsystem_id:
            return row
    return {
        'subsystem_id': subsystem_id,
        'name': subsystem_id,
        'class': 'unknown',
        'active_status': 'UNKNOWN',
        'authority_may': [],
        'authority_must_not': [],
        'authority_rule': 'No authority record found.',
    }


def require_export_surface(root: str | Path, subsystem_id: str) -> dict[str, Any]:
    row = get_satellite_authority(root, subsystem_id)
    if row.get('class') != 'satellite_export_surface':
        raise RuntimeError(f'{subsystem_id} is not authorized as export surface: {row.get("class")}')
    return row


def require_interaction_surface(root: str | Path, subsystem_id: str) -> dict[str, Any]:
    row = get_satellite_authority(root, subsystem_id)
    if row.get('class') != 'satellite_interaction_surface':
        raise RuntimeError(f'{subsystem_id} is not authorized as interaction surface: {row.get("class")}')
    return row


def require_io_stack(root: str | Path, subsystem_id: str) -> dict[str, Any]:
    row = get_satellite_authority(root, subsystem_id)
    if row.get('class') != 'satellite_io_stack':
        raise RuntimeError(f'{subsystem_id} is not authorized as IO stack: {row.get("class")}')
    return row


def project_authority_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        'subsystem_id': row.get('subsystem_id'),
        'name': row.get('name'),
        'class': row.get('class'),
        'active_status': row.get('active_status'),
        'authority_rule': row.get('authority_rule'),
        'input_from': row.get('input_from'),
        'output_to': row.get('output_to'),
        'horizon_relation': row.get('horizon_relation'),
    }


def resolve_root(anchor: str | Path) -> Path:
    return resolve_project_root(Path(anchor))
