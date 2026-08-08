"""
CIEL/NOEMA bridge for relational ethics.

Important separation:
    E_rel : semantic/ethical scalar, DERIVED
    V36   : native PhaseNav/NOEMA stream coordinate, RUNTIME_PROVENANCE

The V36 produced by StreamMemoryRouter is NOT used to assign moral value.
It records the event in the same stream/M0-M11 trajectory as other NOEMA events.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .relational_medium import EthicalScalarState, EthicalGradient

@dataclass(frozen=True)
class EthicalStreamRecord:
    event_id: str
    raw_sha256: str
    vector_sha256: str
    ethical_scalar: float
    ethical_delta: Optional[float]
    semantic_origin: str
    v36_role: str

def ethical_event_payload(
    state: EthicalScalarState,
    *,
    gradient: Optional[EthicalGradient]=None,
    action_id: Optional[str]=None,
    provenance: Optional[Dict[str,Any]]=None,
) -> Dict[str,Any]:
    return {
        "source":"CIEL_RELATIONAL_ETHICS",
        "event_type":"relational_ethics_state",
        "semantic_origin":"DERIVED",
        "ethical_scalar":{
            "E_rel":state.value,
            "R_M":state.relational_coherence,
            "A_rel":state.alignment,
            "S_rel":state.stability,
        },
        "ethical_gradient":None if gradient is None else {
            "delta":gradient.delta,
            "rate":gradient.rate,
        },
        "action_id":action_id,
        "v36_role":"RUNTIME_PROVENANCE_ONLY",
        "provenance":provenance or {},
    }

def commit_ethics_to_noema(
    router,
    state: EthicalScalarState,
    *,
    gradient: Optional[EthicalGradient]=None,
    action_id: Optional[str]=None,
    provenance: Optional[Dict[str,Any]]=None,
    timestamp_ns: Optional[int]=None,
) -> EthicalStreamRecord:
    """
    `router` is the existing StreamMemoryRouter instance.
    No second memory format is created.
    """
    payload=ethical_event_payload(
        state,
        gradient=gradient,
        action_id=action_id,
        provenance=provenance,
    )
    commit=router.ingest(payload,timestamp_ns=timestamp_ns)
    return EthicalStreamRecord(
        event_id=commit.event_id,
        raw_sha256=commit.raw_sha256,
        vector_sha256=commit.vector_sha256,
        ethical_scalar=float(state.value),
        ethical_delta=None if gradient is None else float(gradient.delta),
        semantic_origin="DERIVED",
        v36_role="RUNTIME_PROVENANCE_ONLY",
    )

__all__=["EthicalStreamRecord","ethical_event_payload","commit_ethics_to_noema"]
