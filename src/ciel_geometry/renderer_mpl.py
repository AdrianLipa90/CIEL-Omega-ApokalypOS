"""Matplotlib Poincaré disk renderer — interactive orbital cockpit (Foundation Pack P6 MVP).

Usage:
    python -m ciel_geometry.renderer_mpl              # static snapshot
    python -m ciel_geometry.renderer_mpl --live       # auto-refresh every 5s
    python -m ciel_geometry.renderer_mpl --save out.png
"""

from __future__ import annotations

import argparse
import math
import time
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.collections import LineCollection
import numpy as np

from .layout import build_layout, DiskLayout, DiskNode

# ── Palette ────────────────────────────────────────────────────────────────────
_BG          = "#0a0a1a"
_DISK_EDGE   = "#1a2a4a"
_GRID_COLOR  = "#101830"
_EDGE_COLOR  = "#1e3a5f"

_HORIZON_COLOR = {
    "SEALED":        "#e05050",
    "POROUS":        "#4aafff",
    "TRANSMISSIVE":  "#f0d060",
    "OBSERVATIONAL": "#808080",
}

_SECTOR_COLOR    = "#40a0ff"
_SECTOR_GLOW     = "#80c8ff"
_MODE_ACCENT = {
    "deep":     "#40ff80",
    "standard": "#f0d060",
    "safe":     "#ff6040",
}

_FONT = "monospace"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _node_label(node: DiskNode) -> str:
    return node.label[:14]


def _health_bar(ax: plt.Axes, x: float, y: float, value: float, label: str, color: str) -> None:
    w = 0.18
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w * value, 0.018,
        boxstyle="round,pad=0.002",
        facecolor=color, edgecolor="none", alpha=0.85,
        transform=ax.transAxes, zorder=10,
    ))
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, 0.018,
        boxstyle="round,pad=0.002",
        facecolor="none", edgecolor=color, linewidth=0.5, alpha=0.4,
        transform=ax.transAxes, zorder=10,
    ))
    ax.text(x + w + 0.005, y + 0.009, f"{label} {value:.2f}",
            color=color, fontsize=6.5, va="center", fontfamily=_FONT,
            transform=ax.transAxes, zorder=11)


# ── Core render ────────────────────────────────────────────────────────────────

def render(layout: DiskLayout, ax: Optional[plt.Axes] = None, fig: Optional[plt.Figure] = None) -> plt.Figure:
    """Render DiskLayout onto a matplotlib figure. Returns the figure."""
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(9, 9), facecolor=_BG)
        ax.set_facecolor(_BG)

    ax.set_xlim(-1.12, 1.12)
    ax.set_ylim(-1.12, 1.12)
    ax.set_aspect("equal")
    ax.axis("off")

    # ── Unit disk boundary ──
    circle = Circle((0, 0), 1.0, fill=False, edgecolor=_DISK_EDGE, linewidth=1.2, zorder=1)
    ax.add_patch(circle)

    # Faint concentric rings
    for r in (0.25, 0.5, 0.75):
        ring = Circle((0, 0), r, fill=False, edgecolor=_GRID_COLOR, linewidth=0.4, linestyle=":", zorder=1)
        ax.add_patch(ring)

    # Faint radial lines (every 60°)
    for deg in range(0, 360, 60):
        rad = math.radians(deg)
        ax.plot([0, math.cos(rad)], [0, math.sin(rad)],
                color=_GRID_COLOR, linewidth=0.3, linestyle=":", zorder=1)

    # ── Geodesic edges ──
    for edge in layout.edges:
        pts = np.array(edge.arc_points)
        alpha = 0.15 + 0.5 * edge.weight
        ax.plot(pts[:, 0], pts[:, 1],
                color=_EDGE_COLOR, linewidth=0.8 + edge.weight * 1.2,
                alpha=min(0.9, alpha), zorder=2, solid_capstyle="round")

    # ── Nodes ──
    sectors = [n for n in layout.nodes if n.node_type == "sector"]
    entities = [n for n in layout.nodes if n.node_type == "entity"]

    # Entity dots (small, behind sectors)
    for node in entities:
        color = _HORIZON_COLOR.get(node.horizon_class, "#808080")
        r = 0.022 + node.size * 0.018
        ax.add_patch(Circle((node.x, node.y), r,
                             facecolor=color, edgecolor="none", alpha=0.55, zorder=3))

    # Entity labels (only TRANSMISSIVE + SEALED — high importance)
    for node in entities:
        if node.horizon_class in ("TRANSMISSIVE", "SEALED"):
            color = _HORIZON_COLOR.get(node.horizon_class, "#808080")
            ax.text(node.x, node.y + 0.045, _node_label(node),
                    color=color, fontsize=5.5, ha="center", va="bottom",
                    fontfamily=_FONT, alpha=0.85, zorder=5,
                    path_effects=[pe.withStroke(linewidth=1.5, foreground=_BG)])

    # Sector nodes (larger, glowing)
    for node in sectors:
        r_outer = 0.045 + node.size * 0.03
        r_inner = r_outer * 0.55
        # Glow
        for mult, alpha in ((2.4, 0.08), (1.6, 0.15), (1.0, 1.0)):
            ax.add_patch(Circle((node.x, node.y), r_outer * mult,
                                 facecolor=_SECTOR_GLOW, edgecolor="none",
                                 alpha=alpha, zorder=4 if mult < 1.1 else 3))
        # Core
        ax.add_patch(Circle((node.x, node.y), r_inner,
                             facecolor=_BG, edgecolor=_SECTOR_COLOR,
                             linewidth=1.0, zorder=5))
        # Label
        ax.text(node.x, node.y - r_outer - 0.04, _node_label(node),
                color=_SECTOR_COLOR, fontsize=7, ha="center", va="top",
                fontfamily=_FONT, fontweight="bold", zorder=6,
                path_effects=[pe.withStroke(linewidth=2, foreground=_BG)])
        # Dominant spin hint
        spin = node.meta.get("dominant_spin", "")
        if spin:
            ax.text(node.x, node.y + r_outer + 0.02, spin[:6],
                    color=_SECTOR_GLOW, fontsize=5, ha="center", va="bottom",
                    fontfamily=_FONT, alpha=0.6, zorder=6)

    # ── HUD — top left ──
    m = layout.metadata
    mode = m.get("mode", "standard")
    accent = _MODE_ACCENT.get(mode, "#f0d060")

    ax.text(0.02, 0.98, "CIEL ORBITAL", color=accent, fontsize=9,
            fontfamily=_FONT, fontweight="bold", va="top",
            transform=ax.transAxes, zorder=10)
    ax.text(0.02, 0.945, f"mode: {mode.upper()}",
            color=accent, fontsize=7, fontfamily=_FONT, va="top",
            transform=ax.transAxes, zorder=10, alpha=0.8)

    ts = m.get("timestamp", "")
    if ts:
        ax.text(0.02, 0.915, ts[:19],
                color="#406080", fontsize=5.5, fontfamily=_FONT, va="top",
                transform=ax.transAxes, zorder=10)

    # Health bars
    _health_bar(ax, 0.02, 0.865, float(m.get("system_health", 0)), "health", "#40c060")
    _health_bar(ax, 0.02, 0.840, float(m.get("coherence_index", 0)), "coher", "#4aafff")

    cp = float(m.get("closure_penalty", 0))
    cp_norm = min(1.0, cp / 6.0)
    _health_bar(ax, 0.02, 0.815, cp_norm, f"close {cp:.2f}", "#f08040")

    # ── Legend — bottom right ──
    legend_x, legend_y = 0.72, 0.04
    for i, (hc, color) in enumerate(_HORIZON_COLOR.items()):
        ax.add_patch(Circle((0, 0), 1, transform=ax.transAxes,
                             facecolor="none", edgecolor="none"))  # dummy for zorder
        ax.plot([], [])  # dummy
        ax.text(legend_x, legend_y + i * 0.03, f"● {hc}",
                color=color, fontsize=5.5, fontfamily=_FONT,
                transform=ax.transAxes, zorder=10, va="bottom")

    # Node count
    ax.text(0.98, 0.02, f"{m.get('node_count', 0)} nodes  {m.get('edge_count', 0)} edges",
            color="#304050", fontsize=5.5, fontfamily=_FONT, ha="right",
            transform=ax.transAxes, zorder=10)

    if standalone:
        fig.tight_layout(pad=0.3)
    return fig


# ── Entry point ────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CIEL Poincaré Disk Renderer")
    p.add_argument("--live", action="store_true", help="Auto-refresh every N seconds")
    p.add_argument("--interval", type=float, default=5.0, help="Refresh interval in seconds (--live)")
    p.add_argument("--save", type=str, default="", help="Save to file instead of showing")
    p.add_argument("--no-entities", action="store_true", help="Show only sector nodes")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    include_entities = not args.no_entities

    matplotlib.rcParams["toolbar"] = "None"

    if args.save:
        layout = build_layout(include_entities=include_entities)
        fig = render(layout)
        fig.savefig(args.save, dpi=150, facecolor=_BG, bbox_inches="tight")
        print(f"Saved: {args.save}")
        return

    if args.live:
        fig, ax = plt.subplots(figsize=(9, 9), facecolor=_BG)
        plt.ion()
        fig.canvas.manager.set_window_title("CIEL Orbital — live")

        while plt.fignum_exists(fig.number):
            ax.clear()
            ax.set_facecolor(_BG)
            layout = build_layout(include_entities=include_entities)
            render(layout, ax=ax, fig=fig)
            fig.canvas.draw()
            fig.canvas.flush_events()
            # Non-blocking wait
            deadline = time.time() + args.interval
            while time.time() < deadline and plt.fignum_exists(fig.number):
                plt.pause(0.1)
        return

    # Static
    layout = build_layout(include_entities=include_entities)
    fig = render(layout)
    fig.canvas.manager.set_window_title("CIEL Orbital")
    plt.show()


if __name__ == "__main__":
    main()
