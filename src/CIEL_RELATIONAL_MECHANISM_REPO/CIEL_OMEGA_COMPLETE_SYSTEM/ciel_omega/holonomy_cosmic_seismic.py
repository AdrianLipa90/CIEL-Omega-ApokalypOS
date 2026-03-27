#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Holonomic testbed for cosmic-ray / seismic / solar coupling.

Purpose
-------
Given three time series
    1) cosmic-ray intensity (or its filtered / normalized proxy),
    2) earthquake activity,
    3) solar activity,
compute a phase-holonomy diagnostic inspired by the user's Metatime/CIEL
framework:

    Δ_H(t; τ, δ) = exp(i φ_CR(t))
                 + w_EQ exp(i φ_EQ(t + τ))
                 + w_SOL exp(i φ_SOL(t + δ))

    R_H(t; τ, δ) = |Δ_H(t; τ, δ)|^2 / N^2

with optional White-Thread amplitude between channels.

This script does NOT assume access to Homola's raw data files.  It is designed
so that public cosmic-ray / earthquake / solar time series can be dropped in as
CSV and tested directly.

Typical use
-----------
python holonomy_cosmic_seismic.py \
    --cr-csv cosmic_ray.csv --cr-time time --cr-value counts \
    --eq-csv earthquakes.csv --eq-time time --eq-mag magnitude \
    --solar-csv solar.csv --solar-time time --solar-value sunspots \
    --outdir results

Expected input formats
----------------------
Cosmic-ray CSV:
    time,value

Solar CSV:
    time,value

Earthquake catalog CSV:
    time,magnitude

Notes
-----
- Earthquakes are converted to a global activity proxy by binning in time and
  summing magnitudes (or counts, configurable).
- Phases are extracted from detrended / standardized signals via Hilbert
  transform.
- The default lag scan includes τ = 15 days as the primary hypothesis.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd
from scipy.signal import detrend, hilbert
import matplotlib.pyplot as plt


# -----------------------------------------------------------------------------
# Data containers
# -----------------------------------------------------------------------------

@dataclass
class SeriesSpec:
    csv_path: Path
    time_col: str
    value_col: str


@dataclass
class EarthquakeSpec:
    csv_path: Path
    time_col: str
    magnitude_col: str
    mode: str = "sum_magnitude"  # "count" | "sum_magnitude" | "energy_proxy"


@dataclass
class HolonomyConfig:
    bin_days: int = 5
    tau_days_default: int = 15
    delta_days_default: int = 0
    tau_scan_days: Sequence[int] = tuple(range(-60, 65, 5))
    delta_scan_days: Sequence[int] = tuple(range(-365 * 3, 365 * 3 + 1, 30))
    w_eq: float = 1.0
    w_sol: float = 1.0
    beta_white_thread: float = 1.0
    use_solar: bool = True


# -----------------------------------------------------------------------------
# Loading and preprocessing
# -----------------------------------------------------------------------------

def _ensure_datetime_index(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df = df.dropna(subset=[time_col]).sort_values(time_col)
    df = df.set_index(time_col)
    return df


def load_scalar_series(spec: SeriesSpec) -> pd.Series:
    df = pd.read_csv(spec.csv_path)
    df = _ensure_datetime_index(df, spec.time_col)
    if spec.value_col not in df.columns:
        raise KeyError(f"Column '{spec.value_col}' not found in {spec.csv_path}")
    s = pd.to_numeric(df[spec.value_col], errors="coerce").dropna()
    s.name = spec.value_col
    return s


def load_earthquake_activity(spec: EarthquakeSpec) -> pd.Series:
    df = pd.read_csv(spec.csv_path)
    df = _ensure_datetime_index(df, spec.time_col)
    if spec.magnitude_col not in df.columns:
        raise KeyError(f"Column '{spec.magnitude_col}' not found in {spec.csv_path}")
    mag = pd.to_numeric(df[spec.magnitude_col], errors="coerce").dropna()

    if spec.mode == "count":
        activity = pd.Series(1.0, index=mag.index, name="eq_count")
    elif spec.mode == "sum_magnitude":
        activity = mag.rename("eq_sum_magnitude")
    elif spec.mode == "energy_proxy":
        # Crude seismological energy proxy: log10(E) ~ 1.5M + const
        activity = (10.0 ** (1.5 * mag)).rename("eq_energy_proxy")
    else:
        raise ValueError(f"Unknown earthquake mode: {spec.mode}")

    return activity


def bin_series(series: pd.Series, bin_days: int, agg: str = "mean") -> pd.Series:
    rule = f"{bin_days}D"
    if agg == "mean":
        return series.resample(rule).mean()
    if agg == "sum":
        return series.resample(rule).sum()
    if agg == "median":
        return series.resample(rule).median()
    raise ValueError(f"Unknown aggregation: {agg}")


def align_series(cr: pd.Series, eq: pd.Series, solar: Optional[pd.Series] = None) -> pd.DataFrame:
    parts = [cr.rename("cr"), eq.rename("eq")]
    if solar is not None:
        parts.append(solar.rename("solar"))
    df = pd.concat(parts, axis=1).sort_index()
    return df.interpolate(method="time").dropna()


def robust_standardize(x: pd.Series) -> pd.Series:
    x = pd.Series(x).astype(float)
    med = x.median()
    mad = (x - med).abs().median()
    scale = 1.4826 * mad if mad > 0 else x.std(ddof=0)
    if scale == 0 or np.isnan(scale):
        scale = 1.0
    z = (x - med) / scale
    return z


def preprocess_signal(x: pd.Series) -> pd.Series:
    z = robust_standardize(x)
    y = pd.Series(detrend(z.values), index=z.index)
    return y


# -----------------------------------------------------------------------------
# Phase / holonomy machinery
# -----------------------------------------------------------------------------

def analytic_phase(x: pd.Series) -> pd.Series:
    h = hilbert(x.values)
    phase = np.angle(h)
    return pd.Series(phase, index=x.index)


def wrap_angle(theta: np.ndarray | pd.Series) -> np.ndarray:
    theta = np.asarray(theta)
    return (theta + np.pi) % (2 * np.pi) - np.pi


def phase_distance(phi_a: pd.Series, phi_b: pd.Series) -> pd.Series:
    d = wrap_angle(phi_a.values - phi_b.values)
    return pd.Series(np.abs(d), index=phi_a.index)


def white_thread_amplitude(phi_a: pd.Series, phi_b: pd.Series, beta: float = 1.0) -> pd.Series:
    d = phase_distance(phi_a, phi_b)
    return np.cos(d / 2.0) * np.exp(-beta * d)


def shift_by_days(series: pd.Series, days: int) -> pd.Series:
    return series.copy().shift(freq=pd.Timedelta(days=days))


def holonomic_defect(
    phi_cr: pd.Series,
    phi_eq: pd.Series,
    phi_sol: Optional[pd.Series],
    tau_days: int,
    delta_days: int,
    w_eq: float,
    w_sol: float,
    use_solar: bool = True,
) -> pd.Series:
    eq_shifted = shift_by_days(phi_eq, tau_days)
    parts = [np.exp(1j * phi_cr)]
    parts.append(w_eq * np.exp(1j * eq_shifted))

    if use_solar and phi_sol is not None:
        sol_shifted = shift_by_days(phi_sol, delta_days)
        parts.append(w_sol * np.exp(1j * sol_shifted))

    df = pd.concat(parts, axis=1).dropna()
    delta = df.sum(axis=1)
    delta.name = "Delta_H"
    return delta


def holonomy_measure(delta_h: pd.Series, n_channels: int) -> pd.Series:
    r = np.abs(delta_h.values) ** 2 / (n_channels ** 2)
    return pd.Series(r, index=delta_h.index, name="R_H")


def euler_closure_error(phases_df: pd.DataFrame) -> pd.Series:
    # Effective closure error to nearest multiple of 2π
    phi_sum = phases_df.sum(axis=1).values
    nearest = 2 * np.pi * np.round(phi_sum / (2 * np.pi))
    err = np.abs(phi_sum - nearest)
    return pd.Series(err, index=phases_df.index, name="euler_error")


# -----------------------------------------------------------------------------
# Scans
# -----------------------------------------------------------------------------

def score_tau_scan(
    phi_cr: pd.Series,
    phi_eq: pd.Series,
    tau_days: Iterable[int],
    beta: float,
) -> pd.DataFrame:
    rows = []
    for tau in tau_days:
        eq_shifted = shift_by_days(phi_eq, tau)
        aligned = pd.concat([phi_cr.rename("cr"), eq_shifted.rename("eq")], axis=1).dropna()
        if len(aligned) < 10:
            continue
        wt = white_thread_amplitude(aligned["cr"], aligned["eq"], beta=beta)
        delta = np.exp(1j * aligned["cr"]) + np.exp(1j * aligned["eq"])
        r_h = holonomy_measure(pd.Series(delta, index=aligned.index), n_channels=2)
        rows.append({
            "tau_days": tau,
            "mean_R_H": float(r_h.mean()),
            "mean_white_thread": float(wt.mean()),
            "median_white_thread": float(wt.median()),
        })
    return pd.DataFrame(rows).sort_values("tau_days")


def score_tau_delta_scan(
    phi_cr: pd.Series,
    phi_eq: pd.Series,
    phi_sol: pd.Series,
    tau_days: Iterable[int],
    delta_days: Iterable[int],
    w_eq: float,
    w_sol: float,
) -> pd.DataFrame:
    rows = []
    for tau in tau_days:
        for delta in delta_days:
            delta_h = holonomic_defect(
                phi_cr=phi_cr,
                phi_eq=phi_eq,
                phi_sol=phi_sol,
                tau_days=tau,
                delta_days=delta,
                w_eq=w_eq,
                w_sol=w_sol,
                use_solar=True,
            )
            if len(delta_h) < 10:
                continue
            r_h = holonomy_measure(delta_h, n_channels=3)
            rows.append({
                "tau_days": tau,
                "delta_days": delta,
                "mean_R_H": float(r_h.mean()),
                "min_R_H": float(r_h.min()),
                "std_R_H": float(r_h.std(ddof=0)),
            })
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# Plotting / reporting
# -----------------------------------------------------------------------------

def save_main_plots(
    outdir: Path,
    signals: pd.DataFrame,
    phases: pd.DataFrame,
    r_h_default: pd.Series,
    tau_scan: pd.DataFrame,
    tau_delta_scan: Optional[pd.DataFrame] = None,
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    # Signals
    plt.figure(figsize=(10, 5))
    for col in signals.columns:
        plt.plot(signals.index, signals[col], label=col)
    plt.title("Preprocessed signals")
    plt.xlabel("time")
    plt.ylabel("standardized / detrended")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "signals_preprocessed.png", dpi=180)
    plt.close()

    # Phases
    plt.figure(figsize=(10, 5))
    for col in phases.columns:
        plt.plot(phases.index, phases[col], label=col)
    plt.title("Instantaneous phases")
    plt.xlabel("time")
    plt.ylabel("phase [rad]")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "phases.png", dpi=180)
    plt.close()

    # Default R_H
    plt.figure(figsize=(10, 5))
    plt.plot(r_h_default.index, r_h_default.values)
    plt.title("R_H for default lag setup")
    plt.xlabel("time")
    plt.ylabel("R_H")
    plt.tight_layout()
    plt.savefig(outdir / "R_H_default.png", dpi=180)
    plt.close()

    # Tau scan
    plt.figure(figsize=(8, 4.5))
    plt.plot(tau_scan["tau_days"], tau_scan["mean_R_H"], marker="o", label="mean_R_H")
    plt.axvline(15, linestyle="--", label="15 d")
    plt.xlabel("tau_days")
    plt.ylabel("mean_R_H")
    plt.title("Tau scan")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "tau_scan_mean_R_H.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.plot(tau_scan["tau_days"], tau_scan["mean_white_thread"], marker="o", label="mean WT")
    plt.axvline(15, linestyle="--", label="15 d")
    plt.xlabel("tau_days")
    plt.ylabel("mean white-thread amplitude")
    plt.title("Tau scan — White Thread amplitude")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "tau_scan_white_thread.png", dpi=180)
    plt.close()

    # Tau/delta heatmap if present
    if tau_delta_scan is not None and len(tau_delta_scan) > 0:
        pivot = tau_delta_scan.pivot(index="tau_days", columns="delta_days", values="mean_R_H")
        plt.figure(figsize=(10, 6))
        plt.imshow(pivot.values, aspect="auto", origin="lower")
        plt.colorbar(label="mean_R_H")
        plt.title("Tau / delta scan heatmap")
        plt.xlabel("delta_days index")
        plt.ylabel("tau_days index")
        plt.tight_layout()
        plt.savefig(outdir / "tau_delta_heatmap.png", dpi=180)
        plt.close()


# -----------------------------------------------------------------------------
# Main pipeline
# -----------------------------------------------------------------------------

def run_pipeline(
    cr_spec: SeriesSpec,
    eq_spec: EarthquakeSpec,
    solar_spec: Optional[SeriesSpec],
    cfg: HolonomyConfig,
    outdir: Path,
) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)

    cr_raw = load_scalar_series(cr_spec)
    eq_raw = load_earthquake_activity(eq_spec)
    solar_raw = load_scalar_series(solar_spec) if solar_spec is not None else None

    cr_b = bin_series(cr_raw, cfg.bin_days, agg="mean")
    eq_agg = "sum" if eq_spec.mode != "count" else "sum"
    eq_b = bin_series(eq_raw, cfg.bin_days, agg=eq_agg)
    sol_b = bin_series(solar_raw, cfg.bin_days, agg="mean") if solar_raw is not None else None

    aligned = align_series(cr_b, eq_b, sol_b)

    signals = pd.DataFrame(index=aligned.index)
    signals["cr"] = preprocess_signal(aligned["cr"])
    signals["eq"] = preprocess_signal(aligned["eq"])
    if cfg.use_solar and "solar" in aligned.columns:
        signals["solar"] = preprocess_signal(aligned["solar"])

    phases = pd.DataFrame(index=signals.index)
    phases["phi_cr"] = analytic_phase(signals["cr"])
    phases["phi_eq"] = analytic_phase(signals["eq"])
    if cfg.use_solar and "solar" in signals.columns:
        phases["phi_solar"] = analytic_phase(signals["solar"])

    # Default holonomy using Homola-inspired tau=15d starting point
    delta_h_default = holonomic_defect(
        phi_cr=phases["phi_cr"],
        phi_eq=phases["phi_eq"],
        phi_sol=phases.get("phi_solar"),
        tau_days=cfg.tau_days_default,
        delta_days=cfg.delta_days_default,
        w_eq=cfg.w_eq,
        w_sol=cfg.w_sol,
        use_solar=cfg.use_solar,
    )
    n_channels = 3 if (cfg.use_solar and "phi_solar" in phases.columns) else 2
    r_h_default = holonomy_measure(delta_h_default, n_channels=n_channels)

    # Two-channel tau scan (CR vs EQ)
    tau_scan = score_tau_scan(
        phi_cr=phases["phi_cr"],
        phi_eq=phases["phi_eq"],
        tau_days=cfg.tau_scan_days,
        beta=cfg.beta_white_thread,
    )

    tau_delta_scan = None
    if cfg.use_solar and "phi_solar" in phases.columns:
        tau_delta_scan = score_tau_delta_scan(
            phi_cr=phases["phi_cr"],
            phi_eq=phases["phi_eq"],
            phi_sol=phases["phi_solar"],
            tau_days=cfg.tau_scan_days,
            delta_days=cfg.delta_scan_days,
            w_eq=cfg.w_eq,
            w_sol=cfg.w_sol,
        )

    # Euler-like closure error for the default alignment
    phases_default = pd.DataFrame(index=delta_h_default.index)
    phases_default["phi_cr"] = phases["phi_cr"].reindex(delta_h_default.index)
    phases_default["phi_eq_shifted"] = shift_by_days(phases["phi_eq"], cfg.tau_days_default).reindex(delta_h_default.index)
    if cfg.use_solar and "phi_solar" in phases.columns:
        phases_default["phi_solar_shifted"] = shift_by_days(phases["phi_solar"], cfg.delta_days_default).reindex(delta_h_default.index)
    euler_err = euler_closure_error(phases_default.dropna())

    # White thread for default tau
    eq_shifted = shift_by_days(phases["phi_eq"], cfg.tau_days_default)
    aligned_default = pd.concat([phases["phi_cr"].rename("cr"), eq_shifted.rename("eq")], axis=1).dropna()
    wt_default = white_thread_amplitude(aligned_default["cr"], aligned_default["eq"], beta=cfg.beta_white_thread)

    # Save outputs
    signals.to_csv(outdir / "signals_preprocessed.csv")
    phases.to_csv(outdir / "phases.csv")
    r_h_default.to_csv(outdir / "R_H_default.csv", header=True)
    euler_err.to_csv(outdir / "euler_error_default.csv", header=True)
    wt_default.to_csv(outdir / "white_thread_default.csv", header=True)
    tau_scan.to_csv(outdir / "tau_scan.csv", index=False)
    if tau_delta_scan is not None:
        tau_delta_scan.to_csv(outdir / "tau_delta_scan.csv", index=False)

    save_main_plots(outdir, signals, phases, r_h_default, tau_scan, tau_delta_scan)

    best_tau_row = tau_scan.loc[tau_scan["mean_R_H"].idxmin()].to_dict() if len(tau_scan) else None
    best_tau_wt_row = tau_scan.loc[tau_scan["mean_white_thread"].idxmax()].to_dict() if len(tau_scan) else None

    summary = {
        "config": asdict(cfg),
        "n_samples_aligned": int(len(signals)),
        "default_tau_days": cfg.tau_days_default,
        "default_delta_days": cfg.delta_days_default,
        "default_mean_R_H": float(r_h_default.mean()),
        "default_median_R_H": float(r_h_default.median()),
        "default_mean_euler_error": float(euler_err.mean()) if len(euler_err) else None,
        "default_mean_white_thread": float(wt_default.mean()) if len(wt_default) else None,
        "best_tau_by_mean_R_H": best_tau_row,
        "best_tau_by_mean_white_thread": best_tau_wt_row,
    }

    if tau_delta_scan is not None and len(tau_delta_scan):
        best_3ch = tau_delta_scan.loc[tau_delta_scan["mean_R_H"].idxmin()].to_dict()
        summary["best_tau_delta_by_mean_R_H"] = best_3ch

    with open(outdir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Holonomic CR–EQ–Solar pipeline")

    p.add_argument("--cr-csv", type=Path, required=True)
    p.add_argument("--cr-time", type=str, required=True)
    p.add_argument("--cr-value", type=str, required=True)

    p.add_argument("--eq-csv", type=Path, required=True)
    p.add_argument("--eq-time", type=str, required=True)
    p.add_argument("--eq-mag", type=str, required=True)
    p.add_argument("--eq-mode", type=str, default="sum_magnitude", choices=["count", "sum_magnitude", "energy_proxy"])

    p.add_argument("--solar-csv", type=Path, default=None)
    p.add_argument("--solar-time", type=str, default="time")
    p.add_argument("--solar-value", type=str, default="value")

    p.add_argument("--outdir", type=Path, default=Path("results_holonomy"))
    p.add_argument("--bin-days", type=int, default=5)
    p.add_argument("--tau-default", type=int, default=15)
    p.add_argument("--delta-default", type=int, default=0)
    p.add_argument("--tau-min", type=int, default=-60)
    p.add_argument("--tau-max", type=int, default=60)
    p.add_argument("--tau-step", type=int, default=5)
    p.add_argument("--delta-min", type=int, default=-1095)
    p.add_argument("--delta-max", type=int, default=1095)
    p.add_argument("--delta-step", type=int, default=30)
    p.add_argument("--w-eq", type=float, default=1.0)
    p.add_argument("--w-sol", type=float, default=1.0)
    p.add_argument("--beta", type=float, default=1.0)
    p.add_argument("--no-solar", action="store_true")

    return p.parse_args()


def main() -> None:
    args = parse_args()

    cr_spec = SeriesSpec(args.cr_csv, args.cr_time, args.cr_value)
    eq_spec = EarthquakeSpec(args.eq_csv, args.eq_time, args.eq_mag, args.eq_mode)
    solar_spec = None if args.no_solar or args.solar_csv is None else SeriesSpec(args.solar_csv, args.solar_time, args.solar_value)

    cfg = HolonomyConfig(
        bin_days=args.bin_days,
        tau_days_default=args.tau_default,
        delta_days_default=args.delta_default,
        tau_scan_days=tuple(range(args.tau_min, args.tau_max + 1, args.tau_step)),
        delta_scan_days=tuple(range(args.delta_min, args.delta_max + 1, args.delta_step)),
        w_eq=args.w_eq,
        w_sol=args.w_sol,
        beta_white_thread=args.beta,
        use_solar=not args.no_solar,
    )

    summary = run_pipeline(cr_spec, eq_spec, solar_spec, cfg, args.outdir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
