"""CIEL/Ω Memory — TMP Kernel: two-phase analysis (A1 + A2).

Split from: unified_memory.py (lines 234–290)
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from memory.monolith.data_types import DataVector
from memory.monolith.defaults import (
    gamma_from_categories,
    spectral_categories,
    validate_timestamp,
)
from memory.monolith.rules_engine import RuleHeuristicsEngine

# Canonical imports replacing duplicate local definitions
from memory.monolith.unified_memory import TMPKernel

