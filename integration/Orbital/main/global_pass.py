from __future__ import annotations

import json
import math

from .dynamics import step
from .extract_geometry import build, repo_root_from_here
from .metrics import (
    chord_tension,
    closure_penalty,
    effective_phase_zeta,
    effective_tau_zeta,
    global_chirality,
    global_coherence,
    radial_spread,
    spectral_observables,
    total_relational_potential,
    zeta_coupling_norm,
    zeta_coupling_norm_raw,
    zeta_tetra_defect,
)
from .registry import load_system


DEFAULT_PARAMS = {
    'dt': 0.0205,
    'tau_eta': 0.0085,
    'tau_reg': 0.0024,
    'sigma': 0.20992708860770198,
    'beta': 0.8858849039288708,
    'gamma': 0.3383621712598693,
    'I0': 0.008114359738066937,
    'mesh_boost': 0.9902072303068182,
    'tension_weight': 0.24841695319131418,
    'closure_weight': 0.08945494489662148,
    'use_zeta_pole': True,
    'zeta_coupling_scale': 0.35,
    'zeta_tetra_weight': 0.50,
    'zeta_amplitude': 0.35,
    'zeta_relax': 0.08,
    'zeta_global_rotation': 0.0,
    'zeta_heisenberg_alpha': 8.0,
    'zeta_i0_scale': 1.0,
    'use_relational_lagrangian': True,
    'kappa_H': 1.0,
    'lambda_tension': 0.15,
    'lambda_distortion': 1.0,
    'lambda_zeta_tetra': 1.0,
    'alpha_spin': 4.0,
    'mu_phi': 0.18,
    'mu_rho': 0.14,
    'epsilon_hom': 0.22,
    'spin_vorticity_gain': 0.20,
    'relax_amp': 0.28,
    'grad_eps': 1e-3,
    'use_euler_leak_rotation': True,
    'D_f': 2.57,
    'euler_angular_gain': 1.0,
    'zeta_phase0': 0.0,
}


def _param(system, key, default):
    return float(system.params.get(key, default))


def snapshot(system) -> dict:
    spec = spectral_observables(system)
    snap = {
        'R_H': global_coherence(system),
        'T_glob': chord_tension(system),
        'Lambda_glob': global_chirality(system),
        'closure_penalty': closure_penalty(system),
        'V_rel_total': total_relational_potential(system),
        'radial_spread': radial_spread(system),
        'mean_spin': sum(s.spin for s in system.sectors.values()) / max(1, len(system.sectors)),
        'spectral_radius_A': spec['spectral_radius_A'],
        'spectral_gap_A': spec['spectral_gap_A'],
        'fiedler_L': spec['fiedler_L'],
        'zeta_enabled': bool(system.zeta_pole is not None),
    }
    if system.zeta_pole is not None:
        snap.update({
            'zeta_tetra_defect': zeta_tetra_defect(system),
            'zeta_effective_tau': effective_tau_zeta(system),
            'zeta_effective_phase': effective_phase_zeta(system),
            'zeta_coupling_norm': zeta_coupling_norm(system),
            'zeta_coupling_norm_raw': zeta_coupling_norm_raw(system),
            'zeta_spin': system.zeta_pole.spin,
            'zeta_rho': system.zeta_pole.rho,
            'D_f': _param(system, 'D_f', 2.57),
            'euler_leak_angle': 0.5 * math.pi * (_param(system, 'D_f', 2.57) - 2.0),
        })
    return snap


def run_global_pass(steps: int = 20, params: dict | None = None) -> dict:
    repo_root = repo_root_from_here()
    payload = build(repo_root)
    out_dir = repo_root / 'reports' / 'global_orbital_coherence_pass'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'real_geometry.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')

    sectors_path = repo_root / 'manifests' / 'sectors_global.json'
    couplings_path = repo_root / 'manifests' / 'couplings_global.json'
    p = dict(DEFAULT_PARAMS)
    if params:
        p.update(params)

    system = load_system(sectors_path, couplings_path, params=p)
    initial = snapshot(system)
    history = [initial]
    for _ in range(steps):
        system = step(system, dt=p['dt'], tau_eta=p['tau_eta'], tau_reg=p['tau_reg'])
        history.append(snapshot(system))
    final = history[-1]
    result = {
        'engine': 'global_orbital_coherence_pass_minimal',
        'steps': steps,
        'params': p,
        'initial': initial,
        'final': final,
        'history': history,
    }
    (out_dir / 'summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')

    md = ['# Global Orbital Coherence Pass', '', 'Read-only diagnostic pass over the imported orbital structure.', '', '## Initial']
    for k, v in initial.items():
        md.append(f'- {k}: {v}' if isinstance(v, bool) else f'- {k}: {v:.6f}')
    md += ['', '## Final']
    for k, v in final.items():
        md.append(f'- {k}: {v}' if isinstance(v, bool) else f'- {k}: {v:.6f}')
    md += ['', '## Notes', '- Geometry is derived from orbital manifests when present.', '- This pass is diagnostic only and does not mutate non-orbital repo content.']
    (out_dir / 'summary.md').write_text('\n'.join(md), encoding='utf-8')
    return result


if __name__ == '__main__':
    print(json.dumps(run_global_pass(), indent=2))
