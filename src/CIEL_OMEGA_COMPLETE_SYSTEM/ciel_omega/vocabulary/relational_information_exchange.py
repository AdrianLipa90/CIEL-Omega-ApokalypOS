"""
CIEL/TIR — Conservative relational information exchange v1

Closes the continuous-field <-> discrete-node information bookkeeping without
inventing a mechanical force coefficient.

Field law:
    partial_t rho_I + div J_I = sigma_I

For declared node source densities sigma_i(x,t), define node information
content Q_i with
    dQ_i/dt = - integral sigma_i dV

so that
    d/dt [ integral rho_I dV + sum_i Q_i ] = - boundary_outflow

when sigma_I = sum_i sigma_i.

Interpretation:
- positive sigma_i injects information into the field and removes the same
  amount from node i;
- negative sigma_i removes information from the field and adds it to node i.

This is exact bookkeeping for a declared source partition. It does NOT assert
that Q_i is mass, energy or mechanical momentum and it does NOT create an
acceleration law.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence, Tuple
import numpy as np

from .information_dynamics import (
    InformationFieldState,
    ContinuityReceipt,
    continuity_step_from_faces,
)


@dataclass(frozen=True)
class RelationalInformationNode:
    node_id: str
    information_content: float
    provenance: str


@dataclass(frozen=True)
class ExchangeReceipt:
    dt: float
    node_before: Tuple[Tuple[str,float], ...]
    node_after: Tuple[Tuple[str,float], ...]
    field_before: float
    field_after: float
    boundary_outflow: float
    total_before: float
    total_after_plus_outflow: float
    balance_residual: float


def partition_source_density(
    node_source_densities: Mapping[str,np.ndarray],
    expected_shape: Tuple[int,int,int],
) -> np.ndarray:
    if not node_source_densities:
        return np.zeros(expected_shape,dtype=float)
    total=np.zeros(expected_shape,dtype=float)
    for node_id,arr in node_source_densities.items():
        a=np.asarray(arr,dtype=float)
        if a.shape != expected_shape:
            raise ValueError(f"source shape mismatch for node {node_id}")
        total += a
    return total


def conservative_exchange_step(
    state: InformationFieldState,
    faces,
    nodes: Sequence[RelationalInformationNode],
    node_source_densities: Mapping[str,np.ndarray],
    dt: float,
):
    """
    Perform one conservative field/node information exchange step.

    Every supplied source partition must correspond to exactly one supplied node
    and vice versa. This prevents hidden/unattributed source terms.
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    node_map={n.node_id:n for n in nodes}
    if len(node_map) != len(nodes):
        raise ValueError("duplicate node_id")
    if set(node_source_densities) != set(node_map):
        raise ValueError("node/source partition must match exactly")

    sigma=partition_source_density(node_source_densities,state.rho.shape)
    field_after, field_receipt=continuity_step_from_faces(state,faces,sigma,dt)

    volume=state.dx**3
    after_nodes=[]
    for node_id in sorted(node_map):
        n=node_map[node_id]
        source_integral=float(np.sum(np.asarray(node_source_densities[node_id],dtype=float))*volume)
        after_nodes.append(RelationalInformationNode(
            node_id=n.node_id,
            information_content=float(n.information_content - dt*source_integral),
            provenance=n.provenance,
        ))

    node_before=sum(float(n.information_content) for n in nodes)
    node_after=sum(float(n.information_content) for n in after_nodes)
    total_before=state.total_information + node_before
    # During dt, outward boundary flux leaves the combined system.
    total_after_plus_outflow=field_after.total_information + node_after + dt*field_receipt.boundary_outflow
    residual=float(total_after_plus_outflow-total_before)

    receipt=ExchangeReceipt(
        dt=float(dt),
        node_before=tuple((n.node_id,float(n.information_content)) for n in sorted(nodes,key=lambda x:x.node_id)),
        node_after=tuple((n.node_id,float(n.information_content)) for n in after_nodes),
        field_before=float(state.total_information),
        field_after=float(field_after.total_information),
        boundary_outflow=float(field_receipt.boundary_outflow),
        total_before=float(total_before),
        total_after_plus_outflow=float(total_after_plus_outflow),
        balance_residual=residual,
    )
    return field_after, tuple(after_nodes), receipt


__all__=[
    "RelationalInformationNode","ExchangeReceipt",
    "partition_source_density","conservative_exchange_step",
]
