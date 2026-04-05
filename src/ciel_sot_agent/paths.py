"""Project root path resolution for the CIEL-SOT-Agent package.

Provides ``resolve_project_root(anchor)`` which locates the repository root
by checking the ``CIEL_SOT_ROOT`` environment variable first, then walking
parent directories until one containing an ``integration/`` subdirectory is
found.
"""
from __future__ import annotations

import os
from pathlib import Path


def resolve_project_root(anchor: str | Path) -> Path:
    env_root = os.getenv("CIEL_SOT_ROOT")
    if env_root:
        candidate = Path(env_root).resolve()
        if (candidate / "integration").exists():
            return candidate

    anchor_path = Path(anchor).resolve()
    for parent in [anchor_path.parent, *anchor_path.parents]:
        if (parent / "integration").exists():
            return parent

    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / "integration").exists():
            return parent

    return anchor_path.parents[2]
