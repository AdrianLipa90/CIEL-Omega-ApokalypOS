"""CIEL/Ω Memory — Rule/heuristics weighting engine.

Split from: unified_memory.py (lines 170–228)
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any, Dict
from memory.monolith.defaults import (
    DEFAULT_HEURISTICS_SELF,
    DEFAULT_HEURISTICS_USER,
    DEFAULT_RULES_IMMUTABLE,
    clamp,
)

# Canonical imports replacing duplicate local definitions
from memory.monolith.unified_memory import RuleHeuristicsEngine

