"""
CIEL/Ω — Local Relational Ethics v6

Purpose:
Prevent a global relational scalar from hiding concentrated harm.

The global scalar E_rel remains:
    E_rel = R_M * A_rel * S_rel

This module adds local observables:
    e_i      : node-level relational ethical contribution
    e_ij     : edge-level relational contribution
    burden_i : loss borne by node i relative to current state

No fixed threshold is used.
A candidate may be globally favorable yet locally regressive; such tradeoffs
are surfaced explicitly instead of being silently averaged away.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np

from .relational_medium import RelationalField, EthicalScalarState

@dataclass(frozen=True)
class LocalEthicalProfile:
    node_values: Tuple[float, ...]
    edge_values: Tuple[Tuple[float, ...], ...]
    global_value: float
    min_node_value: float
    max_node_value: float
    dispersion: float

    @classmethod
    def derive(
        cls,
        field: RelationalField,
        node_alignments: Sequence[float],
        node_stabilities: Sequence[float],
    ) -> "LocalEthicalProfile":
        n=field.medium.cardinality
        if len(node_alignments)!=n or len(node_stabilities)!=n:
            raise ValueError("node observables must match medium cardinality")

        coh=field.node_coherence()
        vals=[]
        for i in range(n):
            A=float(node_alignments[i])
            S=float(node_stabilities[i])
            if not -1.0 <= A <= 1.0:
                raise ValueError("node alignment must lie in [-1,1]")
            if not 0.0 <= S <= 1.0:
                raise ValueError("node stability must lie in [0,1]")
            vals.append(float(coh[i]*A*S))

        edge=np.zeros((n,n),dtype=float)
        local_factor=np.asarray([float(a)*float(s) for a,s in zip(node_alignments,node_stabilities)])
        for i in range(n):
            for j in range(n):
                edge[i,j]=float(field.weights[i,j] * 0.5 * (local_factor[i]+local_factor[j]))

        arr=np.asarray(vals,dtype=float)
        return cls(
            node_values=tuple(float(x) for x in arr),
            edge_values=tuple(tuple(float(x) for x in row) for row in edge),
            global_value=float(np.mean(arr)),
            min_node_value=float(np.min(arr)),
            max_node_value=float(np.max(arr)),
            dispersion=float(np.std(arr)),
        )

@dataclass(frozen=True)
class DistributionalConsequence:
    action_id: str
    current: LocalEthicalProfile
    predicted: LocalEthicalProfile
    node_delta: Tuple[float, ...]
    global_delta: float
    worst_node_delta: float
    harmed_nodes: Tuple[int, ...]
    improved_nodes: Tuple[int, ...]

    @classmethod
    def derive(
        cls,
        action_id: str,
        current: LocalEthicalProfile,
        predicted: LocalEthicalProfile,
    ) -> "DistributionalConsequence":
        if len(current.node_values)!=len(predicted.node_values):
            raise ValueError("profile cardinality mismatch")
        delta=tuple(float(b-a) for a,b in zip(current.node_values,predicted.node_values))
        harmed=tuple(i for i,d in enumerate(delta) if d < 0.0)
        improved=tuple(i for i,d in enumerate(delta) if d > 0.0)
        return cls(
            action_id=action_id,
            current=current,
            predicted=predicted,
            node_delta=delta,
            global_delta=float(predicted.global_value-current.global_value),
            worst_node_delta=float(min(delta)) if delta else 0.0,
            harmed_nodes=harmed,
            improved_nodes=improved,
        )

def pareto_dominates(a: DistributionalConsequence, b: DistributionalConsequence) -> bool:
    av=np.asarray(a.predicted.node_values,dtype=float)
    bv=np.asarray(b.predicted.node_values,dtype=float)
    if av.shape!=bv.shape:
        return False
    return bool(np.all(av >= bv) and np.any(av > bv))

def pareto_front(items: Sequence[DistributionalConsequence]) -> Tuple[DistributionalConsequence,...]:
    front=[]
    for i,a in enumerate(items):
        dominated=False
        for j,b in enumerate(items):
            if i!=j and pareto_dominates(b,a):
                dominated=True
                break
        if not dominated:
            front.append(a)
    return tuple(front)

@dataclass(frozen=True)
class DistributionalDecision:
    selected_action_id: Optional[str]
    pareto_front_ids: Tuple[str,...]
    status: str
    rationale: str
    consequences: Tuple[DistributionalConsequence,...]

def choose_distributionally(
    consequences: Sequence[DistributionalConsequence],
) -> DistributionalDecision:
    if not consequences:
        return DistributionalDecision(None,tuple(),"UNKNOWN","no consequences",tuple())
    front=pareto_front(consequences)
    ids=tuple(x.action_id for x in front)
    if len(front)==1:
        return DistributionalDecision(
            front[0].action_id,ids,"SELECTED",
            "unique Pareto-undominated relational consequence",
            tuple(consequences),
        )
    return DistributionalDecision(
        None,ids,"UNRESOLVED",
        "multiple Pareto-undominated candidates imply a genuine relational tradeoff",
        tuple(consequences),
    )

__all__=[
    "LocalEthicalProfile","DistributionalConsequence",
    "pareto_dominates","pareto_front",
    "DistributionalDecision","choose_distributionally"
]
