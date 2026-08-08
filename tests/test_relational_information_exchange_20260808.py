"""Regression tests for conservative field-node information exchange."""
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.information_dynamics import (
    InformationFieldState, zero_sectors,
)
from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.relational_information_exchange import (
    RelationalInformationNode, conservative_exchange_step,
)


def test_closed_system_field_node_exchange_is_conservative():
    shape=(3,3,3)
    dx=0.5
    rho=np.ones(shape)
    z=np.zeros(shape+(3,))
    state=InformationFieldState(rho,z,zero_sectors(shape),dx)

    Fx=np.zeros((shape[0]+1,shape[1],shape[2]))
    Fy=np.zeros((shape[0],shape[1]+1,shape[2]))
    Fz=np.zeros((shape[0],shape[1],shape[2]+1))

    nodes=(
        RelationalInformationNode("a",2.0,"fixture"),
        RelationalInformationNode("b",3.0,"fixture"),
    )
    sa=np.full(shape,0.1)
    sb=np.full(shape,-0.04)

    _,after,receipt=conservative_exchange_step(
        state,(Fx,Fy,Fz),nodes,{"a":sa,"b":sb},0.02
    )
    assert abs(receipt.balance_residual) < 1e-12
    assert abs(receipt.total_after_plus_outflow-receipt.total_before) < 1e-12
    assert after[0].information_content < 2.0
    assert after[1].information_content > 3.0


def test_boundary_outflow_is_included_in_combined_balance():
    shape=(2,2,2)
    dx=0.25
    rho=np.ones(shape)
    z=np.zeros(shape+(3,))
    state=InformationFieldState(rho,z,zero_sectors(shape),dx)

    Fx=np.zeros((shape[0]+1,shape[1],shape[2]))
    Fy=np.zeros((shape[0],shape[1]+1,shape[2]))
    Fz=np.zeros((shape[0],shape[1],shape[2]+1))
    Fx[-1]=0.3

    nodes=(RelationalInformationNode("a",1.0,"fixture"),)
    sa=np.zeros(shape)
    _,_,receipt=conservative_exchange_step(
        state,(Fx,Fy,Fz),nodes,{"a":sa},0.01
    )
    assert receipt.boundary_outflow > 0
    assert abs(receipt.balance_residual) < 1e-12


def test_unattributed_source_partition_is_rejected():
    shape=(2,2,2)
    dx=1.0
    rho=np.ones(shape)
    z=np.zeros(shape+(3,))
    state=InformationFieldState(rho,z,zero_sectors(shape),dx)
    faces=(np.zeros((3,2,2)),np.zeros((2,3,2)),np.zeros((2,2,3)))
    nodes=(RelationalInformationNode("a",1.0,"fixture"),)
    try:
        conservative_exchange_step(state,faces,nodes,{"b":np.zeros(shape)},0.1)
    except ValueError:
        pass
    else:
        raise AssertionError("unattributed source partition must fail")
