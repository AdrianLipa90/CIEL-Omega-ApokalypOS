"""Consolidated: soul_invariant lives in fields/soul_invariant.py.

This module re-exports everything for backward compatibility.
Do not add new code here — edit fields/soul_invariant.py instead.
"""
from ..fields.soul_invariant import (  # noqa: F401
    SoulInvariant,
    SoulInvariantOperator,
    ZetaRiemannOperator,
)

# CielUnifiedCoreWithSoul was a demo scaffold in the old file — not re-exported.
# If something imports it directly, it needs to be updated to use the canonical classes.

__all__ = ["SoulInvariant", "SoulInvariantOperator", "ZetaRiemannOperator"]
