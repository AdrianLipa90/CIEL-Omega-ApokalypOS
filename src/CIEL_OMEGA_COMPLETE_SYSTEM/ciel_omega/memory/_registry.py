"""Module singleton registry — load once, return cached.

Replaces scattered spec_from_file_location calls across the codebase.
Every module loaded through here is guaranteed to exist exactly once in
sys.modules under a stable name, regardless of how many callers request it.

Usage:
    from ciel_omega.memory._registry import get_module, get_encoder, get_holonomic
"""
from __future__ import annotations

import importlib.util as ilu
import sys
import threading
from pathlib import Path

_LOCK = threading.Lock()
_MEM_DIR = Path(__file__).parent


def get_module(name: str, filename: str):
    """Load a memory module by filename, cached in sys.modules under name."""
    with _LOCK:
        if name in sys.modules:
            return sys.modules[name]
        path = _MEM_DIR / filename
        spec = ilu.spec_from_file_location(name, path)
        mod = ilu.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod


# ── Typed accessors ───────────────────────────────────────────────────────────

def get_encoder():
    """Return the singleton CIELEncoder instance."""
    mod = get_module("ciel_encoder", "ciel_encoder.py")
    return mod.get_encoder()


def get_holonomic():
    """Return a HolonomicMemory instance (shared DB connection pool via WAL)."""
    mod = get_module("holonomic_memory", "holonomic_memory.py")
    return mod.HolonomicMemory()


def get_calibration():
    """Return cached CIELCalibration (TTL=300s)."""
    mod = get_module("ciel_calibration", "ciel_calibration.py")
    return mod.get_calibration()


def get_semantic_scorer():
    """Return the semantic_scorer module."""
    return get_module("semantic_scorer", "semantic_scorer.py")
