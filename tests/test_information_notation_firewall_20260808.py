"""Notation firewall: scalar phase offset != vector residual information current."""
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary import (
    CurrentSectors,
    InformationFieldState,
    CanonicalRelationalState,
    classify_declared_residual_current,
)


def test_residual_spatial_current_is_vector_field():
    shape=(2,2,2)
    z=np.zeros(shape+(3,))
    sectors=CurrentSectors(z,z,z,z)
    state=InformationFieldState(np.ones(shape),z,sectors,dx=1.0)
    assert state.residual_current.shape==shape+(3,)
    assert state.total_current.shape==shape+(3,)
    assert classify_declared_residual_current(sectors).status=="EXPLICIT_SECTOR_DECLARATION"


def test_hamiltonian_phase_offset_is_scalar():
    state=CanonicalRelationalState(
        q=np.zeros(2),p=np.zeros(2),J=1.0,J0_phase_offset=0.25,I_phi=2.0
    )
    assert np.isscalar(state.J0_phase_offset)
    assert not isinstance(state.J0_phase_offset,np.ndarray)


def test_two_objects_cannot_be_confused_by_shape():
    shape=(1,1,1)
    z=np.zeros(shape+(3,))
    field=InformationFieldState(np.ones(shape),z,CurrentSectors(z,z,z,z),dx=1.0)
    canonical=CanonicalRelationalState(np.zeros(2),np.zeros(2),1.0,0.0,1.0)
    assert field.residual_current.ndim==4
    assert np.isscalar(canonical.J0_phase_offset)
