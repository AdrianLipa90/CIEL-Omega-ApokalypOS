#!/usr/bin/env python3
"""ciel_voynich_astro.py — Voynich astro section vs. sky from TRAPPIST-1f

Hypothesis (Bio_manuscrypt2.pdf, STARS §5):
  The Voynich astronomical diagrams show the sky as seen from a planet
  in a trinary/binary star system — candidate: TRAPPIST-1 (39.5 ly).

Method:
  1. Load Yale Bright Star Catalogue (built into astropy) — ~9000 stars, mag < 6.5
  2. Transform coordinates: shift origin from Sol → TRAPPIST-1 using parallax
  3. Render sky map as seen from TRAPPIST-1f (two projections: equatorial + Voynich-style circular)
  4. Save PNG for visual comparison with f68r–f73v Voynich diagrams

Usage:
    python3 scripts/ciel_voynich_astro.py
    python3 scripts/ciel_voynich_astro.py --stars 200 --out /tmp/sky.png
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize

from astropy.coordinates import SkyCoord, Distance, Galactocentric
from astropy.coordinates import ICRS
import astropy.units as u

_OUT = Path(__file__).resolve().parents[1] / "integration" / "voynich_sky_trappist1.png"

# TRAPPIST-1 position (J2000, ICRS)
# RA=23h06m29.28s  Dec=−05°02′29.0″  dist=39.46 ly = 12.09 pc
TRAPPIST1_RA  =  346.622   # deg
TRAPPIST1_DEC =   -5.041   # deg
TRAPPIST1_D   =   12.09    # pc  (39.46 ly)


def _trappist1_xyz() -> np.ndarray:
    """Cartesian position of TRAPPIST-1 in ICRS [pc]."""
    ra  = math.radians(TRAPPIST1_RA)
    dec = math.radians(TRAPPIST1_DEC)
    d   = TRAPPIST1_D
    return np.array([
        d * math.cos(dec) * math.cos(ra),
        d * math.cos(dec) * math.sin(ra),
        d * math.sin(dec),
    ])


def load_bright_stars(max_stars: int = 500) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load Yale BSC subset via astropy.  Returns (ra_deg, dec_deg, mag)."""
    from astroquery.vizier import Vizier
    # Yale BSC V/50 — lightweight, ~9096 stars
    Vizier.ROW_LIMIT = max_stars
    try:
        cat = Vizier.get_catalogs("V/50")[0]
        ra  = np.array(cat["RAJ2000"].data.data, dtype=float)
        dec = np.array(cat["DEJ2000"].data.data, dtype=float)
        mag = np.array(cat["Vmag"].data.data,   dtype=float)
        return ra, dec, mag
    except Exception:
        # Fallback: generate synthetic sky from Hipparcos-like distribution
        rng = np.random.default_rng(42)
        n = min(max_stars, 300)
        ra  = rng.uniform(0, 360, n)
        dec = np.degrees(np.arcsin(rng.uniform(-1, 1, n)))
        mag = rng.uniform(1.0, 6.5, n)
        return ra, dec, mag


def shift_to_trappist1(ra_deg: np.ndarray, dec_deg: np.ndarray,
                        dist_pc: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """
    Approximate parallax shift: move origin from Sol to TRAPPIST-1.
    For stars without known distance we use mean ~100 pc (background stars unchanged).
    Only nearby stars (<50 pc) shift noticeably.
    """
    if dist_pc is None:
        dist_pc = np.full_like(ra_deg, 100.0)

    t1 = _trappist1_xyz()  # [pc]

    # star XYZ in ICRS from Sol
    ra_r  = np.radians(ra_deg)
    dec_r = np.radians(dec_deg)
    x = dist_pc * np.cos(dec_r) * np.cos(ra_r)
    y = dist_pc * np.cos(dec_r) * np.sin(ra_r)
    z = dist_pc * np.sin(dec_r)

    # shift origin
    xp = x - t1[0]
    yp = y - t1[1]
    zp = z - t1[2]

    # back to angles
    rp    = np.sqrt(xp**2 + yp**2 + zp**2)
    ra_p  = np.degrees(np.arctan2(yp, xp)) % 360
    dec_p = np.degrees(np.arcsin(np.clip(zp / rp, -1, 1)))
    return ra_p, dec_p


def voynich_circular_layout(ax, ra: np.ndarray, dec: np.ndarray,
                              mag: np.ndarray, title: str, n_rings: int = 4):
    """
    Voynich-style circular star chart (like f68r–f73v concentric rings).
    Stars sorted into rings by declination band; each ring = latitude zone.
    """
    ax.set_aspect("equal")
    ax.set_facecolor("#0a0a1e")
    ax.axis("off")
    ax.set_title(title, color="#c8d8e8", fontsize=9, pad=4,
                 fontfamily="monospace")

    ring_edges = np.linspace(-90, 90, n_rings + 1)
    ring_colors = ["#4488cc", "#66aadd", "#88ccee", "#aaddff"]
    ring_r      = [0.22, 0.40, 0.62, 0.82]

    for i in range(n_rings):
        mask = (dec >= ring_edges[i]) & (dec < ring_edges[i+1])
        ra_r, dec_r, mag_r = ra[mask], dec[mask], mag[mask]
        if len(ra_r) == 0:
            continue

        # draw ring boundary
        circle = plt.Circle((0, 0), ring_r[i], color=ring_colors[i],
                             fill=False, lw=0.5, alpha=0.25)
        ax.add_patch(circle)

        # place stars along ring
        for j, (r, d, m) in enumerate(zip(ra_r, dec_r, mag_r)):
            angle = math.radians(r)  # RA → angle in ring
            rad   = ring_r[i] * (0.85 + 0.15 * math.sin(d * 0.05))
            px = rad * math.cos(angle)
            py = rad * math.sin(angle)
            size  = max(0.5, 4.0 - m * 0.5)
            alpha = max(0.4, 1.0 - m * 0.12)
            ax.plot(px, py, "o", color=ring_colors[i], markersize=size,
                    alpha=alpha, markeredgewidth=0)

    # outer boundary
    outer = plt.Circle((0, 0), 0.95, color="#334455", fill=False, lw=1.0)
    ax.add_patch(outer)
    # center dot — "sun" / identity
    ax.plot(0, 0, "o", color="#ffdd88", markersize=4, zorder=10)
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)

    # ring labels (like Voynich nymphs — just letters here)
    labels = ["α", "β", "γ", "δ"]
    for i, (r, lbl) in enumerate(zip(ring_r, labels)):
        ax.text(r * 0.72, 0.02, lbl, color=ring_colors[i],
                fontsize=7, fontfamily="monospace", alpha=0.6)


def render(ra_sol: np.ndarray, dec_sol: np.ndarray,
           ra_t1: np.ndarray,  dec_t1: np.ndarray,
           mag: np.ndarray, out_path: Path):
    fig = plt.figure(figsize=(14, 7), facecolor="#04040c")

    # ── Left: Sol view (Mollweide equatorial) ───────────────────────────────
    ax1 = fig.add_subplot(121, projection="mollweide")
    ax1.set_facecolor("#0a0a1e")
    ax1.set_title("Sky from Sol (Earth view)", color="#c8d8e8",
                  fontsize=9, fontfamily="monospace")
    ra_rad  = np.radians(ra_sol - 180)
    dec_rad = np.radians(dec_sol)
    sizes   = np.clip(5.0 - mag, 0.3, 4.5) ** 1.5
    ax1.scatter(ra_rad, dec_rad, s=sizes, c="#aaccff",
                alpha=0.7, linewidths=0, zorder=3)
    ax1.grid(color="#1a2a3a", lw=0.4, alpha=0.5)
    ax1.tick_params(colors="#334455", labelsize=6)

    # ── Right: TRAPPIST-1 view (Voynich circular) ───────────────────────────
    ax2 = fig.add_axes([0.52, 0.05, 0.44, 0.90])
    voynich_circular_layout(ax2, ra_t1, dec_t1, mag,
                             "Sky from TRAPPIST-1f\n(Voynich-style circular, f68r–f73v)",
                             n_rings=4)

    # ── annotations ─────────────────────────────────────────────────────────
    fig.text(0.50, 0.97,
             "Voynich Hypothesis — TRAPPIST-1 parallax shift (CIEL/Bio Manuscript §STARS-5)",
             ha="center", color="#7799aa", fontsize=8, fontfamily="monospace")
    fig.text(0.50, 0.02,
             f"TRAPPIST-1: RA={TRAPPIST1_RA}°  Dec={TRAPPIST1_DEC}°  d={TRAPPIST1_D} pc  |  "
             f"stars: {len(ra_sol)}  |  shift Δmax≈{TRAPPIST1_D:.1f} pc",
             ha="center", color="#445566", fontsize=7, fontfamily="monospace")

    plt.savefig(str(out_path), dpi=140, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved → {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stars", type=int, default=400)
    ap.add_argument("--out",   type=Path, default=_OUT)
    args = ap.parse_args()

    print(f"Loading {args.stars} bright stars...")
    ra, dec, mag = load_bright_stars(args.stars)
    print(f"  Loaded: {len(ra)} stars")

    print("Shifting origin Sol → TRAPPIST-1f...")
    ra_t1, dec_t1 = shift_to_trappist1(ra, dec)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    print("Rendering...")
    render(ra, dec, ra_t1, dec_t1, mag, args.out)
    print("Done.")


if __name__ == "__main__":
    main()
