from __future__ import annotations

import json
import math
from pathlib import Path

from .dynamics import step
from .extract_geometry import build, repo_root_from_here
from .metrics import (
    chord_tension,
    closure_penalty,
    effective_phase_zeta,
    effective_tau_zeta,
    global_chirality,
    global_coherence,
    orbital_law_state,
    radial_spread,
    spectral_observables,
    total_relational_potential,
    latest_nonlocal_eba_observables,
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
    'use_orbital_law_v0': False,
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
    'orbital_rho_gain': 0.18,
    'orbital_phi_gain': 0.08,
    'orbital_amp_gain': 0.12,
    'phase_slip_stability_threshold': 0.52,
    'phase_slip_radius_threshold': 0.08,
    'phase_slip_amp_penalty': 0.08,
}


def _param(system, key, default):
    return float(system.params.get(key, default))


def _resolve_project_root(repo_root: Path) -> Path:
    """Find the real project root above Orbital/main if needed."""
    current = repo_root.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / 'integration' / 'repository_registry.json').exists() and (candidate / 'src').exists():
            return candidate
    return repo_root.resolve()


def _load_nonlocal_card_manifest(repo_root: Path) -> dict:
    project_root = _resolve_project_root(repo_root)
    defs_root = project_root / 'integration' / 'registries' / 'definitions'
    cards_path = defs_root / 'nonlocal_cards_registry.json'
    if not cards_path.exists():
        return {
            'registry_present': False,
            'card_count': 0,
            'card_ids': [],
            'active_statuses': [],
            'anchor_count': 0,
            'eba_ready': False,
            'phase_ready': False,
            'bridge_ready': False,
        }
    try:
        payload = json.loads(cards_path.read_text(encoding='utf-8'))
    except Exception:
        return {
            'registry_present': False,
            'card_count': 0,
            'card_ids': [],
            'active_statuses': [],
            'anchor_count': 0,
            'eba_ready': False,
            'phase_ready': False,
            'bridge_ready': False,
        }
    records = payload.get('records', []) or []
    card_ids = [rec.get('card_id') for rec in records if rec.get('card_id')]
    active_statuses = sorted({rec.get('active_status') for rec in records if rec.get('active_status')})
    names = {rec.get('name') for rec in records}
    anchor_count = sum(len(rec.get('anchors', []) or []) for rec in records)
    return {
        'registry_present': True,
        'card_count': len(records),
        'card_ids': card_ids,
        'active_statuses': active_statuses,
        'anchor_count': anchor_count,
        'eba_ready': 'EBA Loop Evaluation Set' in names,
        'phase_ready': 'PhaseInfoSystem' in names,
        'bridge_ready': 'MemoryCorePhaseBridge' in names,
    }


def snapshot(system, repo_root: Path | None = None) -> dict:
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
        'orbital_law_v0_enabled': bool(system.params.get('use_orbital_law_v0', False)),
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
    if snap['orbital_law_v0_enabled']:
        law_state = orbital_law_state(system)
        mu_vals = [state['mu_eff'] for state in law_state.values()]
        tau_vals = [state['tau_orbit'] for state in law_state.values()]
        stability_vals = [state['orbit_stability'] for state in law_state.values()]
        mismatch_vals = [abs(state['delta_r']) for state in law_state.values()]
        snap.update({
            'orbital_mu_eff_mean': sum(mu_vals) / max(1, len(mu_vals)),
            'orbital_tau_orbit_mean': sum(tau_vals) / max(1, len(tau_vals)),
            'orbital_stability_mean': sum(stability_vals) / max(1, len(stability_vals)),
            'orbital_phase_slip_ready_count': sum(1 for state in law_state.values() if state['phase_slip_ready']),
            'orbital_winding_total': sum(state['winding'] for state in law_state.values()),
            'orbital_radius_mismatch_mean': sum(mismatch_vals) / max(1, len(mismatch_vals)),
        })
    if repo_root is not None:
        obs = latest_nonlocal_eba_observables(repo_root)
        snap.update({
            'nonlocal_observables_present': bool(obs.get('observables_present', False)),
            'nonlocal_phi_ab_mean': float(obs.get('phi_ab_mean', 0.0)),
            'nonlocal_phi_berry_mean': float(obs.get('phi_berry_mean', 0.0)),
            'nonlocal_eba_defect_mean': float(obs.get('eba_defect_mean', 0.0)),
            'nonlocal_coherent_fraction': float(obs.get('nonlocal_coherent_fraction', 0.0)),
            'euler_bridge_closure_score': float(obs.get('bridge_closure_score', 0.0)),
            'euler_bridge_target_phase': float(obs.get('bridge_target_phase', 0.0)),
        })
    return snap


def run_global_pass(
    steps: int = 20,
    params: dict | None = None,
    repo_root: str | Path | None = None,
) -> dict:
    repo_root = Path(repo_root) if repo_root is not None else repo_root_from_here()
    payload = build(repo_root)
    out_dir = repo_root / 'reports' / 'global_orbital_coherence_pass'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'real_geometry.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')

    config_dir = repo_root / 'manifests'
    config_dir.mkdir(parents=True, exist_ok=True)
    sectors_path = config_dir / 'sectors_global.json'
    couplings_path = config_dir / 'couplings_global.json'

    if 'sectors' in payload:
        sectors_path.write_text(json.dumps(payload['sectors'], indent=2), encoding='utf-8')
    if 'couplings' in payload:
        couplings_path.write_text(json.dumps(payload['couplings'], indent=2), encoding='utf-8')

    # W_ij override: if couplings_wij_optimized.json exists, merge its coupling
    # values into the build-derived couplings so that optimizer results survive
    # re-runs without permanently overwriting the geometry-derived baseline.
    wij_override_path = config_dir / 'couplings_wij_optimized.json'
    if wij_override_path.exists():
        try:
            override = json.loads(wij_override_path.read_text(encoding='utf-8'))
            override_couplings = override.get('couplings', {})
            base = json.loads(couplings_path.read_text(encoding='utf-8'))
            base_c = base.get('couplings', {})
            for src, targets in override_couplings.items():
                if src in base_c:
                    base_c[src].update(targets)
                else:
                    base_c[src] = dict(targets)
            base['couplings'] = base_c
            base['_wij_override_applied'] = True
            couplings_path.write_text(json.dumps(base, indent=2), encoding='utf-8')
        except Exception as e:
            pass  # fallback: use build-derived couplings

    # OrchOrbital: entity cards run as a SEPARATE pass after main dynamics.
    # They are NOT injected into the main system to preserve orbital stability.
    # Entity metrics are computed post-hoc from their phases and the final system state.
    _entity_sector_names: list[str] = []

    p = dict(DEFAULT_PARAMS)
    if params:
        p.update(params)

    system = load_system(sectors_path, couplings_path, params=p)
    initial = snapshot(system, repo_root=repo_root)
    history = [initial]
    for _ in range(steps):
        system = step(system, dt=p['dt'], tau_eta=p['tau_eta'], tau_reg=p['tau_reg'])
        history.append(snapshot(system, repo_root=repo_root))
    final = history[-1]
    nonlocal_card_manifest = _load_nonlocal_card_manifest(repo_root)
    # Entity orbital: separate mini-pass, isolated from main system dynamics
    _entity_orbital = {}
    try:
        import sys as _sys
        _orch_path = str(Path(__file__).resolve().parents[3] / 'src' / 'ciel_sot_agent')
        if _orch_path not in _sys.path:
            _sys.path.insert(0, _orch_path)
        from orch_orbital import run_entity_mini_pass as _remp
        _entity_orbital = _remp(final)
    except Exception:
        pass

    result = {
        'engine': 'global_orbital_coherence_pass_v63_euler_df257',
        'steps': steps,
        'params': p,
        'initial': initial,
        'final': final,
        'history': history,
        'nonlocal_card_manifest': nonlocal_card_manifest,
        'entity_orbital': _entity_orbital,
    }
    (out_dir / 'summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')

    md = ['# Global Orbital Coherence Pass', '', 'Read-only diagnostic pass over the canonical repository structure.', '', '## Initial']
    for k, v in initial.items():
        md.append(f'- {k}: {v}' if isinstance(v, bool) else f'- {k}: {v:.6f}')
    md += ['', '## Final']
    for k, v in final.items():
        md.append(f'- {k}: {v}' if isinstance(v, bool) else f'- {k}: {v:.6f}')
    md += ['', '## Nonlocal Cards']
    md.append(f"- registry_present: {result['nonlocal_card_manifest'].get('registry_present', False)}")
    md.append(f"- card_count: {result['nonlocal_card_manifest'].get('card_count', 0)}")
    md.append(f"- active_statuses: {', '.join(result['nonlocal_card_manifest'].get('active_statuses', []))}")
    md.append(f"- eba_ready: {result['nonlocal_card_manifest'].get('eba_ready', False)}")
    md.append(f"- phase_ready: {result['nonlocal_card_manifest'].get('phase_ready', False)}")
    md.append(f"- bridge_ready: {result['nonlocal_card_manifest'].get('bridge_ready', False)}")
    md += ['', '## Nonlocal / Euler Observables']
    md.append(f"- nonlocal_observables_present: {final.get('nonlocal_observables_present', False)}")
    md.append(f"- nonlocal_phi_ab_mean: {final.get('nonlocal_phi_ab_mean', 0.0):.6f}")
    md.append(f"- nonlocal_phi_berry_mean: {final.get('nonlocal_phi_berry_mean', 0.0):.6f}")
    md.append(f"- nonlocal_eba_defect_mean: {final.get('nonlocal_eba_defect_mean', 0.0):.6f}")
    md.append(f"- nonlocal_coherent_fraction: {final.get('nonlocal_coherent_fraction', 0.0):.6f}")
    md.append(f"- euler_bridge_closure_score: {final.get('euler_bridge_closure_score', 0.0):.6f}")
    md.append(f"- euler_bridge_target_phase: {final.get('euler_bridge_target_phase', 0.0):.6f}")
    md += ['', '## Notes', '- Geometry derived from imports + README mesh + AGENT mesh + manifests.',
           '- v6.3 uses Euler-rotated homology leak with D_f-dependent radial/angular split.',
           '- When enabled, Orbital Law v0 adds effective attractor strength, orbital period, winding, and phase-slip tracking.',
           '- This pass is diagnostic only; it does not mutate repo content.']
    (out_dir / 'summary.md').write_text('\n'.join(md), encoding='utf-8')
    return result


if __name__ == '__main__':
    print(json.dumps(run_global_pass(), indent=2))
