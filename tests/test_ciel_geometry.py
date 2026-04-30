"""Tests for ciel_geometry — Foundation Pack P5 geometry engine."""

import math
import pytest

from ciel_geometry.disk import (
    poincare_radius,
    poincare_distance,
    sector_to_disk,
    entity_to_disk,
    geodesic_arc,
)
from ciel_geometry.loader import load_sectors, load_couplings, load_bridge_state
from ciel_geometry.layout import build_layout


# --- disk.py ---

def test_poincare_radius_center():
    assert poincare_radius(0.0) == pytest.approx(0.0, abs=1e-9)


def test_poincare_radius_near_boundary():
    # tanh(tan(θ/2)) → 1 only as θ → π/2; at π/2 - 0.001 it's ~0.76
    rho_small = poincare_radius(0.1)
    rho_large = poincare_radius(1.4)
    assert rho_small < rho_large < 1.0


def test_poincare_radius_monotone():
    thetas = [0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3]
    rhos = [poincare_radius(t) for t in thetas]
    assert all(rhos[i] < rhos[i + 1] for i in range(len(rhos) - 1))


def test_sector_to_disk_inside_unit():
    for theta in [0.3, 0.7, 1.1, 1.45, 1.55]:
        for phi in [0.0, 1.0, 2.5, 4.0, 5.5]:
            x, y = sector_to_disk(theta, phi)
            assert math.hypot(x, y) < 1.0, f"({x}, {y}) outside unit disk for theta={theta}, phi={phi}"


def test_entity_to_disk_inside_unit():
    for coupling in [0.0, 0.3, 0.7, 0.97, 1.0]:
        for phase in [0.0, 1.0, 3.14, 5.0]:
            x, y = entity_to_disk(coupling, phase)
            r = math.hypot(x, y)
            assert r < 1.0 + 1e-9, f"({x}, {y}) outside unit disk, r={r}"


def test_poincare_distance_same_point():
    d = poincare_distance(0.5, 1.0, 0.5, 1.0)
    assert d == pytest.approx(0.0, abs=1e-6)


def test_poincare_distance_positive():
    d = poincare_distance(0.3, 0.0, 1.0, 2.0)
    assert d > 0.0


def test_geodesic_arc_endpoints():
    x1, y1 = 0.3, 0.2
    x2, y2 = -0.4, 0.5
    pts = geodesic_arc(x1, y1, x2, y2, steps=10)
    assert len(pts) == 11
    assert pts[0] == pytest.approx((x1, y1), abs=1e-9)
    assert pts[-1] == pytest.approx((x2, y2), abs=1e-3)


def test_geodesic_arc_all_inside_disk():
    pts = geodesic_arc(0.4, 0.1, -0.3, 0.6, steps=20)
    for x, y in pts:
        assert math.hypot(x, y) <= 1.0 + 1e-6


# --- loader.py ---

def test_load_sectors_nonempty():
    sectors = load_sectors()
    assert len(sectors) > 0


def test_load_sectors_fields():
    sectors = load_sectors()
    for s in sectors.values():
        assert 0.0 <= s.theta <= math.pi
        assert 0.0 <= s.phi <= 2 * math.pi + 0.01
        assert s.orbital_type in ("S", "F", "P")


def test_load_couplings_nonempty():
    couplings = load_couplings()
    assert len(couplings) > 0


def test_load_couplings_values_in_range():
    couplings = load_couplings()
    for (src, dst), w in couplings.items():
        assert 0.0 <= w <= 1.0 + 1e-6, f"coupling {src}→{dst} = {w} out of range"


def test_load_bridge_state_fields():
    state = load_bridge_state()
    assert 0.0 <= state.coherence_index <= 1.0 + 1e-3
    assert 0.0 <= state.system_health <= 1.0 + 1e-3
    assert state.mode in ("deep", "standard", "safe")


# --- layout.py ---

def test_build_layout_returns_nodes():
    layout = build_layout(include_entities=False)
    assert len(layout.nodes) > 0


def test_build_layout_sectors_inside_disk():
    layout = build_layout(include_entities=False)
    for node in layout.nodes:
        r = math.hypot(node.x, node.y)
        assert r < 1.0, f"node {node.id} at ({node.x:.3f}, {node.y:.3f}) outside unit disk"


def test_build_layout_edges():
    layout = build_layout(include_entities=False)
    assert len(layout.edges) > 0
    for edge in layout.edges:
        assert edge.weight > 0.0
        assert len(edge.arc_points) > 1


def test_build_layout_with_entities():
    layout = build_layout(include_entities=True, entity_limit=10)
    node_types = {n.node_type for n in layout.nodes}
    assert "sector" in node_types


def test_build_layout_metadata():
    layout = build_layout(include_entities=False)
    assert "coherence_index" in layout.metadata
    assert "system_health" in layout.metadata
    assert "mode" in layout.metadata
    assert layout.metadata["node_count"] == len(layout.nodes)
    assert layout.metadata["edge_count"] == len(layout.edges)


def test_build_layout_to_json():
    layout = build_layout(include_entities=False)
    j = layout.to_json()
    assert '"nodes"' in j
    assert '"edges"' in j
    assert '"metadata"' in j


# --- renderer_mpl.py ---

def test_renderer_mpl_renders_to_figure():
    import matplotlib
    matplotlib.use("Agg")
    from ciel_geometry.renderer_mpl import render
    layout = build_layout(include_entities=True, entity_limit=5)
    fig = render(layout)
    assert fig is not None
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_renderer_mpl_save(tmp_path):
    import subprocess, sys
    out = tmp_path / "test_disk.png"
    result = subprocess.run(
        [sys.executable, "-m", "ciel_geometry.renderer_mpl", "--save", str(out)],
        capture_output=True, text=True,
        env={**__import__("os").environ, "MPLBACKEND": "Agg"},
        cwd="/home/adrian/Pulpit/CIEL_TESTY/CIEL1",
    )
    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert out.stat().st_size > 10_000


# --- semantic_mass.py (P3) ---

def test_semantic_mass_table_nonempty():
    from ciel_geometry.semantic_mass import build_mass_table
    table = build_mass_table(include_entities=False)
    assert len(table) > 0

def test_semantic_mass_values_positive():
    from ciel_geometry.semantic_mass import build_mass_table
    for r in build_mass_table(include_entities=False):
        assert r.M_sem > 0.0
        assert r.orbit_period > 0.0
        assert 0.0 <= r.orbit_radius < 1.0

def test_semantic_mass_sorted_desc():
    from ciel_geometry.semantic_mass import build_mass_table
    table = build_mass_table(include_entities=False)
    masses = [r.M_sem for r in table]
    assert all(masses[i] >= masses[i+1] for i in range(len(masses)-1))

def test_semantic_mass_kepler_rule():
    from ciel_geometry.semantic_mass import build_mass_table
    for r in build_mass_table(include_entities=False):
        # T² ∝ a³/M → T² * M ≈ a³
        ratio = (r.orbit_period**2 * r.M_sem) / max(1e-12, r.orbit_radius**3)
        assert 0.5 < ratio < 2.0, f"{r.id}: Kepler ratio {ratio:.3f} out of expected range"


# --- subjective_time.py (P3) ---

def test_subjective_time_nonempty():
    from ciel_geometry.subjective_time import compute_subjective_times
    recs = compute_subjective_times(include_entities=False)
    assert len(recs) > 0

def test_subjective_time_positive():
    from ciel_geometry.subjective_time import compute_subjective_times
    for r in compute_subjective_times(include_entities=False):
        assert r.tau_scale > 0.0
        assert r.winding_rate > 0.0

def test_subjective_time_boundary_slower():
    from ciel_geometry.subjective_time import compute_subjective_times
    recs = {r.id: r for r in compute_subjective_times(include_entities=False)}
    # constraints (r~0.27) should have higher tau than runtime (r~0.75)
    assert recs['sector:constraints'].tau_scale > recs['sector:runtime'].tau_scale

def test_subjective_time_from_bridge():
    from ciel_geometry.subjective_time import compute_from_bridge
    recs = compute_from_bridge()
    assert len(recs) > 0
    for r in recs:
        assert r.tau_scale > 0.0
