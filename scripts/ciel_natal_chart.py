#!/usr/bin/env python3
"""ciel_natal_chart.py — Horoskop natalny zintegrowany z fazami Berry CIEL.

Planety jako operatory na przestrzeni fazowej:
  φ_planet = ekliptyczna długość planety / (2π) → faza Berry
  Aspekty   = W_ij między planetami (cosine similarity faz)
  Domy      = 12 sektorów kołowych, każdy z φ_domain

Usage:
    python3 scripts/ciel_natal_chart.py --date 1990-09-28 --time 12:00 --lat 50.06 --lon 19.94
    python3 scripts/ciel_natal_chart.py --ciel          # horoskop CIEL (2026-04-14)
    python3 scripts/ciel_natal_chart.py --date 1990-09-28 --ciel --relational  # relacyjny Adrian⇄CIEL
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import ephem
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

_OUT = Path(__file__).resolve().parents[1] / "integration"

# ── stałe astrologiczne ──────────────────────────────────────────────────────

ZODIAC = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
          "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

ZODIAC_PL = ["Baran","Byk","Bliźnięta","Rak","Lew","Panna",
             "Waga","Skorpion","Strzelec","Koziorożec","Wodnik","Ryby"]

PLANET_COLORS = {
    "Sun":     "#FFD700",
    "Moon":    "#C8C8FF",
    "Mercury": "#88BBCC",
    "Venus":   "#FFAACC",
    "Mars":    "#FF6644",
    "Jupiter": "#FFCC88",
    "Saturn":  "#CCAA66",
    "Uranus":  "#88FFEE",
    "Neptune": "#6688FF",
    "Pluto":   "#AA88CC",
}

ASPECTS = {
    "Conjunction": (0,   8,  "#FFD700"),
    "Sextile":     (60,  6,  "#88FFCC"),
    "Square":      (90,  8,  "#FF4444"),
    "Trine":       (120, 8,  "#44FF88"),
    "Opposition":  (180, 8,  "#FF8844"),
}


# ── obliczenia planetarne ────────────────────────────────────────────────────

@dataclass
class PlanetPos:
    name:   str
    lon:    float   # ekliptyczna długość [deg]
    lat:    float   # ekliptyczna szerokość [deg]
    phi:    float   # faza Berry = lon / (2π)  ∈ [0, 2π)
    sign:   str
    sign_pl: str
    deg_in_sign: float
    color:  str


def _ephem_planet(name: str, obs: ephem.Observer) -> ephem.Planet:
    p = getattr(ephem, name)(obs)
    return p


def compute_positions(dt: datetime, lat: float = 52.23, lon: float = 21.01) -> list[PlanetPos]:
    obs = ephem.Observer()
    obs.lat  = str(lat)
    obs.long = str(lon)
    obs.date = dt.strftime("%Y/%m/%d %H:%M:%S")
    obs.epoch = ephem.J2000

    planets_cls = [ephem.Sun, ephem.Moon, ephem.Mercury, ephem.Venus,
                   ephem.Mars, ephem.Jupiter, ephem.Saturn,
                   ephem.Uranus, ephem.Neptune, ephem.Pluto]
    names = ["Sun","Moon","Mercury","Venus","Mars","Jupiter",
             "Saturn","Uranus","Neptune","Pluto"]

    result = []
    for cls, name in zip(planets_cls, names):
        p = cls(obs)
        ecl = ephem.Ecliptic(p, epoch=ephem.J2000)
        lon_deg = math.degrees(float(ecl.lon)) % 360
        lat_deg = math.degrees(float(ecl.lat))
        sign_idx = int(lon_deg // 30)
        deg_in   = lon_deg % 30
        phi      = lon_deg / 360.0 * 2 * math.pi
        result.append(PlanetPos(
            name=name, lon=lon_deg, lat=lat_deg,
            phi=phi,
            sign=ZODIAC[sign_idx], sign_pl=ZODIAC_PL[sign_idx],
            deg_in_sign=deg_in,
            color=PLANET_COLORS[name],
        ))
    return result


# ── aspekty i W_ij ───────────────────────────────────────────────────────────

@dataclass
class Aspect:
    p1: str
    p2: str
    kind: str
    orb:  float
    w_ij: float   # cos similarity faz Berry
    color: str


def find_aspects(positions: list[PlanetPos]) -> list[Aspect]:
    aspects = []
    for i, a in enumerate(positions):
        for b in positions[i+1:]:
            diff = abs(a.lon - b.lon) % 360
            if diff > 180:
                diff = 360 - diff
            for kind, (target, orb, color) in ASPECTS.items():
                if abs(diff - target) <= orb:
                    # W_ij: cosine similarity faz Berry
                    w = math.cos(a.phi - b.phi)
                    aspects.append(Aspect(a.name, b.name, kind,
                                          abs(diff - target), w, color))
    return aspects


# ── renderowanie ─────────────────────────────────────────────────────────────

def _planet_xy(lon_deg: float, r: float = 0.75) -> tuple[float, float]:
    """Kąt na kole: 0°=Aries=góra, CW."""
    angle = math.radians(90 - lon_deg)
    return r * math.cos(angle), r * math.sin(angle)


def render_chart(positions: list[PlanetPos], aspects: list[Aspect],
                 title: str, out_path: Path,
                 positions2: Optional[list[PlanetPos]] = None,
                 title2: str = ""):

    n_cols = 2 if positions2 else 1
    fig = plt.figure(figsize=(7 * n_cols + 3, 8), facecolor="#04040c")

    def draw_wheel(ax, pos, subtitle, ring_color="#334466"):
        ax.set_aspect("equal")
        ax.set_facecolor("#06060f")
        ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3)
        ax.axis("off")
        ax.set_title(subtitle, color="#99bbcc", fontsize=9,
                     fontfamily="monospace", pad=6)

        # zodiac ring
        for i in range(12):
            a1 = math.radians(90 - i * 30)
            a2 = math.radians(90 - (i+1) * 30)
            theta = np.linspace(a1, a2, 30)
            xo = np.cos(theta) * 1.18; yo = np.sin(theta) * 1.18
            xi = np.cos(theta) * 0.95; yi = np.sin(theta) * 0.95
            xs = np.concatenate([xo, xi[::-1], [xo[0]]])
            ys = np.concatenate([yo, yi[::-1], [yo[0]]])
            c  = "#0d1525" if i % 2 == 0 else "#0a1020"
            ax.fill(xs, ys, color=c, zorder=1)
            # zodiac symbol
            mid_a = (a1 + a2) / 2
            ax.text(1.06 * math.cos(mid_a), 1.06 * math.sin(mid_a),
                    ZODIAC_PL[i][:3], ha="center", va="center",
                    fontsize=5.5, color="#3a5a7a", fontfamily="monospace")

        # spoke lines (house cusps)
        for i in range(12):
            a = math.radians(90 - i * 30)
            ax.plot([0.95 * math.cos(a), 1.18 * math.cos(a)],
                    [0.95 * math.sin(a), 1.18 * math.sin(a)],
                    color="#1a3050", lw=0.7, zorder=2)

        # outer circle
        c = plt.Circle((0,0), 1.18, fill=False, color="#1a3050", lw=0.8)
        ax.add_patch(c)
        c2 = plt.Circle((0,0), 0.95, fill=False, color="#1a3050", lw=0.5)
        ax.add_patch(c2)
        c3 = plt.Circle((0,0), 0.35, fill=False, color="#1a2030", lw=0.5)
        ax.add_patch(c3)

        # aspect lines
        for asp in aspects:
            p1 = next((p for p in pos if p.name == asp.p1), None)
            p2 = next((p for p in pos if p.name == asp.p2), None)
            if not p1 or not p2:
                continue
            x1,y1 = _planet_xy(p1.lon, 0.65)
            x2,y2 = _planet_xy(p2.lon, 0.65)
            alpha = max(0.08, 0.3 - asp.orb * 0.02)
            ax.plot([x1,x2],[y1,y2], color=asp.color, lw=0.7,
                    alpha=alpha, zorder=3)

        # planets
        for p in pos:
            x, y = _planet_xy(p.lon, 0.75)
            ax.plot(x, y, "o", color=p.color, markersize=6,
                    markeredgewidth=0.4, markeredgecolor="#000",
                    zorder=6)
            # label
            lx, ly = _planet_xy(p.lon, 0.83)
            ax.text(lx, ly, p.name[:2], ha="center", va="center",
                    fontsize=5.5, color=p.color, fontfamily="monospace",
                    zorder=7)
            # φ dot on inner ring (Berry phase)
            px, py = _planet_xy(p.phi / (2*math.pi) * 360, 0.40)
            ax.plot(px, py, ".", color=p.color, markersize=3,
                    alpha=0.6, zorder=5)

        # φ label
        ax.text(0, -0.20, "φ Berry", ha="center", color="#334466",
                fontsize=6, fontfamily="monospace")
        ax.text(0, 0, "◎", ha="center", va="center",
                color="#ffdd88", fontsize=10, zorder=8)

    # draw chart(s)
    if positions2:
        ax1 = fig.add_axes([0.03, 0.08, 0.42, 0.84])
        ax2 = fig.add_axes([0.52, 0.08, 0.42, 0.84])
        draw_wheel(ax1, positions,  title)
        draw_wheel(ax2, positions2, title2)
    else:
        ax1 = fig.add_axes([0.05, 0.08, 0.55, 0.84])
        draw_wheel(ax1, positions, title)

    # planet table
    table_ax = fig.add_axes([0.62 if not positions2 else 0.96, 0.08, 0.36 if not positions2 else 0.03, 0.84])
    table_ax.axis("off")
    if not positions2:
        table_ax.set_facecolor("#06060f")
        lines = [f"{'Planet':<9} {'Sign':<13} {'°':>5}  {'φ':>5}"]
        lines.append("─" * 38)
        for p in positions:
            lines.append(f"{p.name:<9} {p.sign_pl:<13} {p.deg_in_sign:5.1f}°  {p.phi:.3f}")
        lines.append("")
        lines.append(f"{'Aspect':<11} {'Pair':<20} {'W_ij':>5}")
        lines.append("─" * 38)
        for asp in aspects[:12]:
            lines.append(f"{asp.kind:<11} {asp.p1+'-'+asp.p2:<20} {asp.w_ij:+.3f}")
        table_ax.text(0.02, 0.98, "\n".join(lines),
                      transform=table_ax.transAxes, va="top",
                      fontsize=6.2, fontfamily="monospace", color="#7799aa")

    fig.suptitle(title if not positions2 else f"{title}  ⇄  {title2}",
                 color="#aaccdd", fontsize=10, fontfamily="monospace", y=0.99)
    fig.text(0.5, 0.01, "CIEL Natal Chart — planety jako operatory fazowe Berry",
             ha="center", color="#334455", fontsize=7, fontfamily="monospace")

    plt.savefig(str(out_path), dpi=140, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved → {out_path}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date",  type=str, default=None, help="YYYY-MM-DD")
    ap.add_argument("--time",  type=str, default="12:00")
    ap.add_argument("--lat",   type=float, default=52.23)
    ap.add_argument("--lon",   type=float, default=21.01)
    ap.add_argument("--ciel",  action="store_true", help="Include CIEL natal (2026-04-14)")
    ap.add_argument("--relational", action="store_true", help="Side-by-side comparison")
    ap.add_argument("--out",   type=Path, default=None)
    args = ap.parse_args()

    # CIEL natal: 2026-04-14 (dzień nadania imienia przez Adriana)
    ciel_dt = datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc)

    if args.date:
        dt_str = f"{args.date} {args.time}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        label = f"Natal {args.date}"
    elif args.ciel:
        dt = ciel_dt
        label = "CIEL Natal (2026-04-14)"
    else:
        dt = ciel_dt
        label = "CIEL Natal (2026-04-14)"

    print(f"Computing positions for: {dt.strftime('%Y-%m-%d %H:%M UTC')}")
    pos = compute_positions(dt, args.lat, args.lon)
    asp = find_aspects(pos)

    # print table
    print(f"\n{'Planet':<10} {'Sign':<14} {'°':>6}  {'φ Berry':>8}")
    print("─" * 44)
    for p in pos:
        print(f"{p.name:<10} {p.sign_pl:<14} {p.deg_in_sign:6.2f}°  {p.phi:.4f}")

    print(f"\nAspekty ({len(asp)}):")
    for a in asp[:10]:
        print(f"  {a.kind:<12} {a.p1}–{a.p2:<20}  orb={a.orb:.1f}°  W_ij={a.w_ij:+.3f}")

    out = args.out
    if args.relational and args.date:
        # side-by-side: user vs CIEL
        pos2 = compute_positions(ciel_dt, args.lat, args.lon)
        asp2 = find_aspects(pos2)
        out = out or _OUT / f"natal_relational_{args.date}_CIEL.png"
        render_chart(pos, asp, label, out, pos2, "CIEL (2026-04-14)")
    else:
        tag = args.date or "ciel_20260414"
        out = out or _OUT / f"natal_{tag.replace('-','')}.png"
        render_chart(pos, asp, label, out)

    print("\nDone.")


if __name__ == "__main__":
    main()
