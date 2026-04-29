"""CIEL/Ω Memory — Core data types: MemoriseD and DataVector.

Split from: unified_memory.py (lines 130–165)
"""
from __future__ import annotations
import datetime as dt
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Canonical imports replacing duplicate local definitions
from memory.monolith.unified_memory import DataVector, MemoriseD

