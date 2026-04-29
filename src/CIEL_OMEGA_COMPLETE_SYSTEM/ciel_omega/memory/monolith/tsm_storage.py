"""CIEL/Ω Memory — TSM durable store (SQLite).

Split from: unified_memory.py (lines 296–388)
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict
from memory.monolith.data_types import MemoriseD

# Canonical imports replacing duplicate local definitions
from memory.monolith.unified_memory import TSMWriterSQL

