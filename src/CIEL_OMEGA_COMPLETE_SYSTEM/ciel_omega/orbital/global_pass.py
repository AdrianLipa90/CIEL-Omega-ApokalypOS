from __future__ import annotations
import json
import math
import sys
from pathlib import Path
from .extract_geometry import build, repo_root_from_here
from .registry import load_system
from .dynamics import step
from .metrics import (global_coherence, chord_tension, global_chirality, closure_penalty,
    spectral_observables, zeta_tetra_defect, effective_tau_zeta, effective_phase_zeta,
    zeta_coupling_norm, zeta_coupling_norm_raw, radial_spread, total_relational_potential)

def _param(system, key, default):
    return float(system.params.get(key, default))
DEFAULT_PARAMS = {
  "dt": 0.0205,
  "tau_eta": 0.0085,
  "tau_reg": 0.0024,
  "sigma": 0.20992708860770198,
  "beta": 0.8858849039288708,
  "gamma": 0.3383621712598693,
  "I0": 0.008114359738066937,
  "mesh_boost": 0.9902072303068182,
  "tension_weight": 0.24841695319131418,
  "closure_weight": 0.08945494489662148,
  "use_zeta_pole": True,
  "zeta_coupling_scale": 0.35,
  "zeta_tetra_weight": 0.50,
  "zeta_amplitude": 0.35,
  "zeta_relax": 0.08,
  "zeta_global_rotation": 0.0,
  "zeta_heisenberg_alpha": 8.0,
  "zeta_i0_scale": 1.0,
  "use_relational_lagrangian": True,
  "kappa_H": 1.0,
  "lambda_tension": 0.15,
  "lambda_distortion": 1.0,
  "lambda_zeta_tetra": 1.0,
  "alpha_spin": 4.0,
  "mu_phi": 0.18,
  "mu_rho": 0.14,
  "epsilon_hom": 0.22,
  "spin_vorticity_gain": 0.20,
  "relax_amp": 0.28,
  "grad_eps": 1e-3,
  "use_euler_leak_rotation": True,
  "D_f": 2.57,
  "euler_angular_gain": 1.0,
  "zeta_phase0": 0.0,
}
def snapshot(system):
    spec = spectral_observables(system)
    snap = {
        "R_H": global_coherence(system),
        "T_glob": chord_tension(system),
        "Lambda_glob": global_chirality(system),
        "closure_penalty": closure_penalty(system),
        "V_rel_total": total_relational_potential(system),
        "radial_spread": radial_spread(system),
        "mean_spin": sum(s.spin for s in system.sectors.values()) / max(1, len(system.sectors)),
        "spectral_radius_A": spec["spectral_radius_A"],
        "spectral_gap_A": spec["spectral_gap_A"],
        "fiedler_L": spec["fiedler_L"],
        "zeta_enabled": bool(system.zeta_pole is not None),
    }
    if system.zeta_pole is not None:
        snap.update({
            "zeta_tetra_defect": zeta_tetra_defect(system),
            "zeta_effective_tau": effective_tau_zeta(system),
            "zeta_effective_phase": effective_phase_zeta(system),
            "zeta_coupling_norm": zeta_coupling_norm(system),
            "zeta_coupling_norm_raw": zeta_coupling_norm_raw(system),
            "zeta_spin": system.zeta_pole.spin,
            "zeta_rho": system.zeta_pole.rho,
            "D_f": _param(system, "D_f", 2.57),
            "euler_leak_angle": 0.5 * math.pi * (_param(system, "D_f", 2.57) - 2.0),
        })
    return snap
def run_global_pass(steps: int = 20, params: dict | None = None) -> dict:
    repo_root = repo_root_from_here(); payload = build(repo_root)
    out_dir = repo_root / "reports" / "global_orbital_coherence_pass"; out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "real_geometry.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    config_dir = repo_root / "manifests" / "orbital"; config_dir.mkdir(parents=True, exist_ok=True)
    sectors_path = config_dir / "sectors_global.json"; couplings_path = config_dir / "couplings_global.json"
    # Merge fresh geometry with persisted berry_phase from previous runs
    fresh_sectors = payload["sectors"]
    if sectors_path.exists():
        try:
            prev = json.loads(sectors_path.read_text(encoding="utf-8"))
            prev_inner = prev.get("sectors", prev) if isinstance(prev, dict) else {}
            for sid, prev_s in prev_inner.items():
                if sid in fresh_sectors.get("sectors", fresh_sectors):
                    target = fresh_sectors["sectors"] if "sectors" in fresh_sectors else fresh_sectors
                    if isinstance(prev_s, dict) and "berry_phase" in prev_s:
                        target[sid]["berry_phase"] = prev_s["berry_phase"]
        except Exception:
            pass
    # Inject entity cards before writing manifests
    try:
        _src = Path(__file__).parents[4] / "src"
        if str(_src) not in sys.path:
            sys.path.insert(0, str(_src))
        from ciel_sot_agent.orch_orbital import build_entity_injection
        fresh_sectors, fresh_couplings = build_entity_injection(
            fresh_sectors.get("sectors", fresh_sectors),
            payload["couplings"].get("couplings", payload["couplings"]),
        )
        fresh_sectors = {"sectors": fresh_sectors}
        fresh_couplings = {"couplings": fresh_couplings}
    except Exception as _ei_exc:
        fresh_couplings = payload["couplings"]
    sectors_path.write_text(json.dumps(fresh_sectors, indent=2), encoding="utf-8")
    couplings_path.write_text(json.dumps(fresh_couplings, indent=2), encoding="utf-8")
    p = dict(DEFAULT_PARAMS)
    if params: p.update(params)
    system = load_system(sectors_path, couplings_path, params=p)
    initial = snapshot(system); history=[initial]
    for _ in range(steps):
        system = step(system, dt=p["dt"], tau_eta=p["tau_eta"], tau_reg=p["tau_reg"])
        history.append(snapshot(system))
    final = history[-1]
    result = {"engine": "global_orbital_coherence_pass_v63_euler_df257", "steps": steps, "params": p, "initial": initial, "final": final, "history": history}
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    # Write-back: persist berry_phase accumulation to sectors_global.json so
    # holonomy carries across sessions instead of resetting to 0 each run.
    _writeback_sectors(system, config_dir / "sectors_global.json")
    md=["# Global Orbital Coherence Pass", "", "Read-only diagnostic pass over the canonical repository structure.", "", "## Initial"]
    for k,v in initial.items(): md.append(f"- {k}: {v}" if isinstance(v,bool) else f"- {k}: {v:.6f}")
    md += ["", "## Final"]
    for k,v in final.items(): md.append(f"- {k}: {v}" if isinstance(v,bool) else f"- {k}: {v:.6f}")
    md += ["", "## Notes", "- Geometry derived from imports + README mesh + AGENT mesh + manifests.", "- v6.3 uses Euler-rotated homology leak with D_f-dependent radial/angular split.", "- berry_phase written back to sectors_global.json after each pass for holonomy continuity."]
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")
    return result
def _writeback_sectors(system, path: Path) -> None:
    """Persist accumulated berry_phase so holonomy carries across sessions.
    Only berry_phase is persisted — phi/tau/rho are always re-derived from geometry on next run."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"sectors": {}}
        sectors_dict = doc.get("sectors", {})
        for sid, sector in system.sectors.items():
            entry = sectors_dict.get(sid, {})
            entry["berry_phase"] = getattr(sector, "berry_phase", 0.0)
            sectors_dict[sid] = entry
        doc["sectors"] = sectors_dict
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    except Exception as e:
        import sys
        print(f"[global_pass] _writeback_sectors failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    print(json.dumps(run_global_pass(), indent=2))