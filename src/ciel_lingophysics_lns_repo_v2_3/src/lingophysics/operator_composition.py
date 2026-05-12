from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CompositionResult:
    expression: str
    invariant: Optional[str]
    valid: bool
    note: str = ""


def containment_equivalence(expr_a: str, expr_b: str) -> CompositionResult:
    a = expr_a.replace(" ", "")
    b = expr_b.replace(" ", "")
    pairs = {
        ("Inside(Water,Glass)", "Contains(Glass,Water)"),
        ("Inside(x,y)", "Contains(y,x)"),
    }
    if (a, b) in pairs or (b, a) in pairs:
        return CompositionResult(
            expression=f"{expr_a} ≃ {expr_b}",
            invariant="Containment(x,y)",
            valid=True,
            note="Dual topological containment invariant preserved.",
        )
    return CompositionResult(
        expression=f"{expr_a} ? {expr_b}",
        invariant=None,
        valid=False,
        note="No built-in containment equivalence found.",
    )


def negate_operator(expr: str) -> str:
    """Return explicit negation without collapsing to inverse."""
    return f"Not({expr})"
