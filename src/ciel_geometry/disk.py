"""Map orbital coordinates to Poincaré disk positions (x, y) ∈ (-1, 1)²."""

from __future__ import annotations

import math


def poincare_radius(theta: float) -> float:
    """Map polar angle θ ∈ [0, π/2) to Poincaré disk radius ρ ∈ [0, 1).

    Replicates integration/Orbital/main/metrics.py:poincare_radius.
    θ=0 → ρ=0 (center), θ→π/2 → ρ→1 (boundary).
    """
    theta = max(0.0, min(theta, math.pi / 2.0 - 1e-9))
    return math.tanh(math.tan(theta / 2.0))


def poincare_distance(theta_a: float, phi_a: float, theta_b: float, phi_b: float) -> float:
    """Hyperbolic distance between two points on the Poincaré disk.

    Replicates integration/Orbital/main/metrics.py:poincare_distance.
    """
    ra = min(0.999999, abs(poincare_radius(theta_a)))
    rb = min(0.999999, abs(poincare_radius(theta_b)))
    dphi = phi_b - phi_a
    num = ra**2 + rb**2 - 2.0 * ra * rb * math.cos(dphi)
    den = max(1e-12, (1.0 - ra**2) * (1.0 - rb**2))
    arg = max(1.0, 1.0 + 2.0 * num / den)
    return math.acosh(arg)


def sector_to_disk(theta: float, phi: float) -> tuple[float, float]:
    """Convert sector (theta, phi) spherical coords to Poincaré disk (x, y)."""
    rho = poincare_radius(theta)
    return rho * math.cos(phi), rho * math.sin(phi)


def entity_to_disk(coupling: float, phase: float) -> tuple[float, float]:
    """Convert entity (coupling_ciel, phase) to Poincaré disk (x, y).

    coupling_ciel is already in [0, 1] — used directly as ρ.
    phase is the azimuthal angle φ.
    """
    rho = min(0.999, max(0.0, coupling))
    return rho * math.cos(phase), rho * math.sin(phase)


def geodesic_arc(
    x1: float, y1: float,
    x2: float, y2: float,
    steps: int = 20,
) -> list[tuple[float, float]]:
    """Sample points along the geodesic arc between two Poincaré disk points.

    For points close to the center or to each other, falls back to a straight line.
    Returns a list of (x, y) including endpoints.
    """
    # Straight-line fallback when either point is near center or points are close
    if math.hypot(x1, y1) < 0.01 or math.hypot(x2, y2) < 0.01:
        return _straight_line(x1, y1, x2, y2, steps)

    r1_sq = x1**2 + y1**2
    r2_sq = x2**2 + y2**2

    # Check if points are collinear through origin (degenerate geodesic = diameter)
    cross = x1 * y2 - x2 * y1
    if abs(cross) < 1e-9:
        return _straight_line(x1, y1, x2, y2, steps)

    # Find the Euclidean circle whose arc is the hyperbolic geodesic.
    # The center (cx, cy) satisfies: |center - p1|² = |center - p2|² = R² (equidistant)
    # and center lies on the perpendicular bisector of p1-p2 and is outside unit disk.
    # Using the inversion formula: center = (p1* + p2*) / 2 after some algebra.
    # Simpler: use parametric linear interpolation in hyperbolic space.
    denom = 2.0 * cross
    cx = (y2 * (1 + r1_sq) - y1 * (1 + r2_sq)) / denom
    cy = (x1 * (1 + r2_sq) - x2 * (1 + r1_sq)) / denom
    R = math.sqrt((cx - x1)**2 + (cy - y1)**2)

    if R < 1e-9 or R > 50.0:
        return _straight_line(x1, y1, x2, y2, steps)

    # Parameterise by angle around center
    a1 = math.atan2(y1 - cy, x1 - cx)
    a2 = math.atan2(y2 - cy, x2 - cx)

    # Choose shorter arc
    da = a2 - a1
    if da > math.pi:
        da -= 2 * math.pi
    elif da < -math.pi:
        da += 2 * math.pi

    pts = []
    for i in range(steps + 1):
        t = i / steps
        a = a1 + t * da
        px = cx + R * math.cos(a)
        py = cy + R * math.sin(a)
        # Clamp inside unit disk
        r = math.hypot(px, py)
        if r >= 1.0:
            px, py = px / r * 0.999, py / r * 0.999
        pts.append((px, py))
    return pts


def _straight_line(x1: float, y1: float, x2: float, y2: float, steps: int) -> list[tuple[float, float]]:
    return [(x1 + (x2 - x1) * i / steps, y1 + (y2 - y1) * i / steps) for i in range(steps + 1)]
