"""CIEL/Ω Memory — Default configs, timestamp utils, spectral multiplier γ.

Split from: unified_memory.py (lines 38–128)
"""
from __future__ import annotations
import datetime as dt
import re
from typing import Any, Dict, Optional, Tuple

# Canonical imports replacing duplicate local definitions
from memory.monolith.unified_memory import DEFAULT_HEURISTICS_SELF, DEFAULT_HEURISTICS_USER, DEFAULT_RULES_IMMUTABLE, ISO8601_RE, clamp, gamma_from_categories, is_iso8601, spectral_categories, validate_timestamp

