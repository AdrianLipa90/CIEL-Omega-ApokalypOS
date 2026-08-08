"""Integration regression: derived local TIR metric -> Hamiltonian geometry."""
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.phase_first_geometry import build_local_tir_hamiltonian_geometry
from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.relational_information_metric import global_phase_projector, KAPPA_INFORMATION


def test_local_tir_builder_uses_quotient_pseudoinverse():
    d=6
    total=4+d
    g=build_local_tir_hamiltonian_geometry(
        theta=1.0,u=0.1,v=-0.2,d_rel=d,grad_V=np.zeros(total)
    )
    rel=g.g_inv[4:,4:]
    expected=(d/(2*KAPPA_INFORMATION))*global_phase_projector(d)
    assert np.allclose(rel,expected)
    assert np.allclose(rel@np.ones(d),0.0,atol=1e-12)
    assert np.allclose(g.d_g_inv[4:],0.0)


def test_local_tir_builder_preserves_source_berry_block():
    d=4
    g=build_local_tir_hamiltonian_geometry(
        theta=1.1,u=0.0,v=0.0,d_rel=d,grad_V=np.zeros(4+d)
    )
    assert g.A.shape==(4+d,)
    assert g.A[0]==0.0
    assert g.A[1] != 0.0
