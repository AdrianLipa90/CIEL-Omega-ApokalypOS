from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict


@dataclass(frozen=True)
class CIELConstants:
    c: float = 299_792_458.0
    hbar: float = 1.054_571_817e-34
    mu0: float = 4e-7 * math.pi
    eps0: float = 8.854_187_8128e-12
    G: float = 6.67430e-11
    k_B: float = 1.380649e-23

    Lp: float = 1.616_255e-35
    tp: float = 5.391_247e-44
    mp: float = 2.176_434e-8

    lam1: float = 0.1
    lam2: float = 0.05
    lam3: float = 0.2
    alpha: float = 0.01
    beta: float = 0.10
    eta: float = 0.001
    gamma: float = 0.02
    xi: float = 1.0

    ethical_bound: float = 0.90
    cfl_safety: float = 0.4
    min_field_value: float = 1e-15
    max_field_value: float = 1e15

    alpha_c: float = 0.474812
    beta_s: float = 0.856234
    gamma_t: float = 0.345123
    delta_r: float = 0.634567
    lambda_const: float = 0.474812
    gamma_max: float = 0.751234

    consciousness_quantum_phi: float = 0.6180339887

    information_preservation: float = 0.998765
    entanglement_strength: float = 0.723456

    lambda_i: float = 0.723456
    lambda_tau: float = 1.86e43
    lambda_zeta: float = 0.146
    beta_top: float = 6.17e-45
    kappa: float = 2.08e-43
    omega_structure: float = 0.786
    kappa_memory: float = 0.05
    tau_recall: float = 0.1
    alpha_em: float = 1 / 137.035999084

    def __getattr__(self, name: str) -> Any:
        aliases: Dict[str, str] = {
            'C': 'c',
            'HBAR': 'hbar',
            'MU0': 'mu0',
            'EPS0': 'eps0',
            'LP': 'Lp',
            'TP': 'tp',
            'MP': 'mp',
            'h_bar': 'hbar',
            'mu_0': 'mu0',
            'epsilon_0': 'eps0',
            'L_planck': 'Lp',
            't_planck': 'tp',
            'm_planck': 'mp',
            'L_p': 'Lp',
            'T_p': 'tp',
            'M_p': 'mp',
            'lambda_1': 'lam1',
            'lambda_2': 'lam2',
            'lambda_3': 'lam3',
            'lam1': 'lam1',
            'lam2': 'lam2',
            'lam3': 'lam3',
            'life_threshold': 'ethical_bound',
            'ETHICAL_BOUND': 'ethical_bound',
            'E_BOUND': 'ethical_bound',
            'ALPHA_C': 'alpha_c',
            'BETA_S': 'beta_s',
            'GAMMA_T': 'gamma_t',
            'DELTA_R': 'delta_r',
            'LIPA_CONSTANT': 'lambda_const',
            'LAMBDA': 'lambda_const',
            'MAX_COHERENCE': 'gamma_max',
            'GAMMA_MAX': 'gamma_max',
            'CONSCIOUSNESS_QUANTUM': 'alpha_c',
            'SYMBOLIC_COUPLING': 'beta_s',
            'TEMPORAL_FLOW': 'gamma_t',
            'RESONANCE_QUANTUM': 'delta_r',
            'INFORMATION_PRESERVATION': 'information_preservation',
            'ENTANGLEMENT_STRENGTH': 'entanglement_strength',
            'EFFECTIVE_HBAR': 'hbar',
            'EFFECTIVE_C': 'c',
            'EFFECTIVE_G': 'G',
            'LAMBDA_I': 'lambda_i',
            'LAMBDA_TAU': 'lambda_tau',
            'LAMBDA_ZETA': 'lambda_zeta',
            'BETA_TOP': 'beta_top',
            'KAPPA': 'kappa',
            'OMEGA_LIFE': 'omega_structure',
            'OMEGA_STRUCTURE': 'omega_structure',
            'KAPPA_MEMORY': 'kappa_memory',
            'TAU_RECALL': 'tau_recall',
            'ALPHA_EM': 'alpha_em',
        }
        target = aliases.get(name)
        if target is None:
            raise AttributeError(name)
        return getattr(self, target)


DEFAULT_CONSTANTS = CIELConstants()
constants = DEFAULT_CONSTANTS
