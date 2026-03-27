#!/usr/bin/env python3
"""
CIEL/Ω – Monolit empiryczno-dynamiczny (v2.3-synced)
=====================================================
Łączy:
  1. Analizę holonomiczną szeregów czasowych (CR, EQ, solar)
  2. Skanowanie opóźnień τ i δ
  3. Uruchomienie układu fazowego PhaseSystem na dopasowanych fazach
  4. Ocena spójności z literaturą (τ ≈ 15 dni, niska R_H, niska A_ZS)

v2.3 sync: generalized N, gamma[-1], dynamic WT base, wt_fn callback
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.signal import hilbert, detrend

# ── Try matplotlib, skip plots if unavailable ──
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_PLT = True
except ImportError:
    HAS_PLT = False


# ============================================================================
# 1. Funkcje pomocnicze do danych i faz
# ============================================================================

def load_scalar_series(csv_path, time_col, value_col):
    df = pd.read_csv(csv_path)
    df[time_col] = pd.to_datetime(df[time_col], utc=True)
    df = df.set_index(time_col).sort_index()
    return pd.to_numeric(df[value_col], errors='coerce').dropna()

def load_earthquake_activity(csv_path, time_col, mag_col, mode="sum_magnitude"):
    df = pd.read_csv(csv_path)
    df[time_col] = pd.to_datetime(df[time_col], utc=True)
    df = df.set_index(time_col).sort_index()
    mag = pd.to_numeric(df[mag_col], errors='coerce').dropna()
    if mode == "count": return pd.Series(1.0, index=mag.index)
    elif mode == "sum_magnitude": return mag
    elif mode == "energy_proxy": return 10.0 ** (1.5 * mag)
    else: raise ValueError(f"Unknown mode: {mode}")

def bin_series(series, bin_days, agg="mean"):
    rule = f"{bin_days}D"
    return series.resample(rule).mean() if agg == "mean" else series.resample(rule).sum()

def align_series(cr, eq, solar=None):
    parts = [cr.rename("cr"), eq.rename("eq")]
    if solar is not None: parts.append(solar.rename("solar"))
    return pd.concat(parts, axis=1).sort_index().interpolate(method='time').dropna()

def robust_standardize(x):
    med = x.median(); mad = (x - med).abs().median()
    scale = 1.4826 * mad if mad > 0 else x.std(ddof=0)
    return (x - med) / (scale if scale > 0 else 1.0)

def preprocess_signal(x):
    return pd.Series(detrend(robust_standardize(x).values), index=x.index)

def analytic_phase(x):
    return pd.Series(np.angle(hilbert(x.values)), index=x.index)

def shift_by_days(series, days):
    return series.shift(freq=pd.Timedelta(days=days))

def holonomic_defect_ts(phi_cr, phi_eq, phi_sol, tau, delta, w_eq, w_sol):
    parts = [np.exp(1j * phi_cr)]
    parts.append(w_eq * np.exp(1j * shift_by_days(phi_eq, tau)))
    if phi_sol is not None:
        parts.append(w_sol * np.exp(1j * shift_by_days(phi_sol, delta)))
    return pd.concat(parts, axis=1).dropna().sum(axis=1)

def R_H_ts(delta_h, n_channels):
    return np.abs(delta_h.values)**2 / (n_channels**2)

def holonomy_scan(cr_phi, eq_phi, solar_phi, tau_list, delta_list=None, w_eq=1.0, w_sol=1.0):
    rows = []
    if delta_list is None:
        for tau in tau_list:
            dh = holonomic_defect_ts(cr_phi, eq_phi, None, tau, 0, w_eq, w_sol)
            if len(dh) < 10: continue
            r = R_H_ts(dh, 2)
            rows.append({"tau_days": tau, "delta_days": 0,
                         "mean_R_H": float(r.mean()), "min_R_H": float(r.min())})
    else:
        for tau in tau_list:
            for delta in delta_list:
                dh = holonomic_defect_ts(cr_phi, eq_phi, solar_phi, tau, delta, w_eq, w_sol)
                if len(dh) < 10: continue
                r = R_H_ts(dh, 3)
                rows.append({"tau_days": tau, "delta_days": delta,
                             "mean_R_H": float(r.mean()), "min_R_H": float(r.min())})
    return pd.DataFrame(rows)


# ============================================================================
# 2. PhaseSystem (imported from phase_equation_of_motion.py)
# ============================================================================

from phase_equation_of_motion import (
    PhaseInfoSystem as PhaseSystem,
    phase_sector, euler_constraint_violation,
    zeta_schrodinger_anomaly, make_zeta_wt_fn,
    BASE_PHASES,
)


# ============================================================================
# 3. Synthetic data generator
# ============================================================================

def generate_synthetic_data(seed=42, n_points=2000, tau_true=15, noise_std=0.1):
    np.random.seed(seed)
    t = pd.date_range("2000-01-01", periods=n_points, freq="D")
    omega = 2*np.pi / 365.0
    cr = 0.5*(1+np.sin(omega*np.arange(n_points))) + 0.2*np.random.randn(n_points)
    solar = 0.3*(1+0.8*np.sin(omega*np.arange(n_points)/2)) + 0.1*np.random.randn(n_points)
    eq = np.roll(cr, tau_true) + noise_std*np.random.randn(n_points)
    eq[:tau_true] = np.nan
    return (pd.Series(cr, index=t, name="cr"),
            pd.Series(eq, index=t, name="eq"),
            pd.Series(solar, index=t, name="solar"))


# ============================================================================
# 4. Main analysis
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Monolit empiryczno-dynamiczny CIEL/Ω")
    parser.add_argument("--cr-csv", type=Path); parser.add_argument("--cr-time", default="time")
    parser.add_argument("--cr-value", default="value")
    parser.add_argument("--eq-csv", type=Path); parser.add_argument("--eq-time", default="time")
    parser.add_argument("--eq-mag", default="magnitude"); parser.add_argument("--eq-mode", default="sum_magnitude")
    parser.add_argument("--solar-csv", type=Path); parser.add_argument("--solar-time", default="time")
    parser.add_argument("--solar-value", default="value")
    parser.add_argument("--bin-days", type=int, default=5)
    parser.add_argument("--tau-min", type=int, default=-60); parser.add_argument("--tau-max", type=int, default=60)
    parser.add_argument("--tau-step", type=int, default=5)
    parser.add_argument("--delta-min", type=int, default=-365); parser.add_argument("--delta-max", type=int, default=365)
    parser.add_argument("--delta-step", type=int, default=30)
    parser.add_argument("--w-eq", type=float, default=1.0); parser.add_argument("--w-sol", type=float, default=1.0)
    parser.add_argument("--outdir", type=Path, default=Path("monolit_results"))
    parser.add_argument("--synthetic", action="store_true"); parser.add_argument("--synthetic-tau", type=int, default=15)
    parser.add_argument("--no-solar", action="store_true")
    args = parser.parse_args()

    outdir = args.outdir; outdir.mkdir(parents=True, exist_ok=True)

    # Data
    if args.synthetic:
        print("Generowanie danych syntetycznych...")
        cr_raw, eq_raw, solar_raw = generate_synthetic_data(tau_true=args.synthetic_tau)
        use_solar = not args.no_solar
    else:
        if not args.cr_csv or not args.eq_csv:
            print("Brak danych. Użyj --synthetic lub podaj --cr-csv i --eq-csv"); sys.exit(1)
        cr_raw = load_scalar_series(args.cr_csv, args.cr_time, args.cr_value)
        eq_raw = load_earthquake_activity(args.eq_csv, args.eq_time, args.eq_mag, args.eq_mode)
        use_solar = (not args.no_solar) and args.solar_csv is not None
        solar_raw = load_scalar_series(args.solar_csv, args.solar_time, args.solar_value) if use_solar else None

    solar_series = solar_raw if use_solar else None

    # Preprocess
    cr_b = bin_series(cr_raw, args.bin_days, "mean")
    eq_b = bin_series(eq_raw, args.bin_days, "sum")
    solar_b = bin_series(solar_series, args.bin_days, "mean") if solar_series is not None else None
    aligned = align_series(cr_b, eq_b, solar_b)
    signals = pd.DataFrame(index=aligned.index)
    signals["cr"] = preprocess_signal(aligned["cr"])
    signals["eq"] = preprocess_signal(aligned["eq"])
    if use_solar and "solar" in aligned.columns:
        signals["solar"] = preprocess_signal(aligned["solar"])

    phi_cr = analytic_phase(signals["cr"])
    phi_eq = analytic_phase(signals["eq"])
    phi_sol = analytic_phase(signals["solar"]) if use_solar else None

    # Holonomy scan
    tau_list = list(range(args.tau_min, args.tau_max+1, args.tau_step))
    delta_list = list(range(args.delta_min, args.delta_max+1, args.delta_step)) if use_solar else None
    print("Skanowanie opóźnień...")
    scan_df = holonomy_scan(phi_cr, phi_eq, phi_sol, tau_list, delta_list, args.w_eq, args.w_sol)
    scan_df.to_csv(outdir / "holonomy_scan.csv", index=False)

    best_idx = scan_df["mean_R_H"].idxmin()
    best_row = scan_df.loc[best_idx]
    best_tau = int(best_row["tau_days"])
    best_delta = int(best_row.get("delta_days", 0))
    print(f"Optymalne: τ={best_tau} dni, δ={best_delta} dni, mean_R_H={best_row['mean_R_H']:.4f}")

    # Optimal R_H timeseries
    n_ch = 3 if use_solar else 2
    delta_opt = holonomic_defect_ts(phi_cr, phi_eq, phi_sol, best_tau, best_delta, args.w_eq, args.w_sol)
    r_opt = pd.Series(R_H_ts(delta_opt, n_ch), index=delta_opt.index)
    r_opt.to_csv(outdir / "R_H_optimal.csv", header=True)

    # Phase system — init from data phases
    common_idx = delta_opt.index
    last_phases = pd.DataFrame({"phi_cr": phi_cr.reindex(common_idx),
                                "phi_eq_shifted": shift_by_days(phi_eq, best_tau).reindex(common_idx)})
    if use_solar:
        last_phases["phi_sol_shifted"] = shift_by_days(phi_sol, best_delta).reindex(common_idx)
    last_phases = last_phases.dropna()

    n_last = min(30, len(last_phases))
    avg_ph = last_phases.iloc[-n_last:].mean().values if n_last > 0 else last_phases.mean().values

    # Map to 4 phases: CR→γ_A, EQ→γ_C, Solar→γ_Q, γ_T=truth_target
    if use_solar and len(avg_ph) >= 3:
        gamma0 = np.array([avg_ph[0], avg_ph[1], avg_ph[2], 0.0]) % (2*np.pi)
    else:
        gamma0 = np.array([avg_ph[0], avg_ph[1], 0.0, 0.0]) % (2*np.pi)

    print("Uruchamianie układu dynamicznego (v2.3)...")
    phase_sys = PhaseSystem(gamma=gamma0, sigma_zeta=0.5, w_WT=0.15, A_collatz=0.05)
    phase_sys.evolve(200, dt=0.1)

    final = phase_sys.history[-1]
    print(f"Stan końcowy: R_H={final['R_H']:.4f}, A_ZS={final['A_ZS']:.4f}, ε={final['euler_violation']:.4f}")

    traj = pd.DataFrame(phase_sys.history)
    traj.to_csv(outdir / "phase_dynamics_trajectory.csv", index=False)

    # Plots
    if HAS_PLT:
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes[0,0].plot(scan_df["tau_days"], scan_df["mean_R_H"], 'o-')
        axes[0,0].axvline(best_tau, color='r', ls='--', label=f"opt τ={best_tau}")
        axes[0,0].set(xlabel="τ (days)", ylabel="mean R_H", title="Holonomy scan"); axes[0,0].legend()
        axes[0,1].plot(r_opt.index, r_opt.values); axes[0,1].set(title=f"R_H(t) at τ={best_tau}")
        axes[1,0].plot(traj["t"], traj["R_H"], label="R_H"); axes[1,0].plot(traj["t"], traj["A_ZS"], label="A_ZS")
        axes[1,0].set(title="Phase system"); axes[1,0].legend()
        axes[1,1].plot(traj["t"], traj["P_total"]); axes[1,1].axhline(0, color='k', ls='--')
        axes[1,1].set(title="Power balance")
        plt.tight_layout(); plt.savefig(outdir / "monolit_plots.png", dpi=150); plt.close()

    # Summary
    report = {
        "best_tau_days": best_tau, "best_delta_days": best_delta,
        "best_mean_R_H": float(best_row["mean_R_H"]),
        "final_R_H": float(final["R_H"]), "final_A_ZS": float(final["A_ZS"]),
        "final_euler": float(final["euler_violation"]),
        "synthetic": args.synthetic,
        "consistency_tau": "TAK" if abs(best_tau - 15) <= 5 else "NIE",
    }
    with open(outdir / "summary.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nWyniki w: {outdir}")
    for k, v in report.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
