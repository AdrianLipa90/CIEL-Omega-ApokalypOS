"""CIEL/Ω Memory — unified orchestrator compatibility surface.

The canonical implementation lives in ``unified_memory.py``.  Importing the
legacy braid runtime during constructor startup can perform heavyweight runtime
initialisation before the first memory capture.  This compatibility surface
keeps memory construction deterministic and defers braid activation to the
explicit braid/nonlocal layers used by the engine.
"""
from __future__ import annotations

import sys
from typing import Any

from memory.monolith import unified_memory as _canonical


class UnifiedMemoryOrchestrator(_canonical.UnifiedMemoryOrchestrator):
    """Construct canonical memory without eager legacy braid-runtime boot.

    CIEL already owns explicit braid and nonlocal runtime surfaces.  The
    monolith's optional legacy adapter is therefore not required during object
    construction and, on CI hosts, can block constructor completion.  We make
    those optional imports unavailable only for the duration of ``super``
    construction, then restore the process import state exactly.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        sentinel = object()
        adapter_key = "core.braid.adapter"
        defaults_key = "core.braid.defaults"
        old_adapter_module = sys.modules.get(adapter_key, sentinel)
        old_defaults_module = sys.modules.get(defaults_key, sentinel)
        old_adapter = _canonical.KernelAdapter
        old_make_default_runtime = _canonical.make_default_runtime

        try:
            _canonical.KernelAdapter = None
            _canonical.make_default_runtime = None
            sys.modules[adapter_key] = None
            sys.modules[defaults_key] = None
            super().__init__(*args, **kwargs)
        finally:
            _canonical.KernelAdapter = old_adapter
            _canonical.make_default_runtime = old_make_default_runtime
            if old_adapter_module is sentinel:
                sys.modules.pop(adapter_key, None)
            else:
                sys.modules[adapter_key] = old_adapter_module
            if old_defaults_module is sentinel:
                sys.modules.pop(defaults_key, None)
            else:
                sys.modules[defaults_key] = old_defaults_module


__all__ = ["UnifiedMemoryOrchestrator"]
