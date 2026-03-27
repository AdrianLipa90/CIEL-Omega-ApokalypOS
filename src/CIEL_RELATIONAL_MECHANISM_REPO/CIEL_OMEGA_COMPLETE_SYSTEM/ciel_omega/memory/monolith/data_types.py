"""CIEL/Ω Memory — Core data types: MemoriseD and DataVector.

Split from: unified_memory.py (lines 130–165)
"""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class MemoriseD:
    """Durable memory record after TMP processing."""

    memorise_id: str
    created_at: str
    D_id: str
    D_context: str
    D_sense: Any
    D_associations: List[Any]
    D_timestamp: str
    D_meta: Dict[str, Any]
    D_type: str
    D_attr: Dict[str, Any]
    weights: Dict[str, Any]
    rationale: str = ""
    source: str = "TMP"


class DataVector:
    """Raw input data vector (pre-TMP)."""

    def __init__(
        self,
        context: str,
        sense: Any,
        associations: Optional[List[Any]] = None,
        timestamp: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ):
        self.id = str(uuid.uuid4())
        self.D_C = context
        self.D_S = sense
        self.D_A = associations or []
        self.D_T = timestamp or dt.datetime.utcnow().isoformat()
        self.D_M = meta or {}
