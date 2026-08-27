"""CQCL vNext living-state program container.

This module is additive. The historical CQCL_Program remains unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True, slots=True)
class CQCL_Living_Program:
    schema: str
    status: str
    program_id: str
    source_state_object_id: str
    nexus_activation_object_id: str
    crystal: Dict[str, Any]
    nexus: Dict[str, Any]
    dictionary: Dict[str, Any]
    htri: Dict[str, Any]
    active_terms: List[Dict[str, Any]]
    semantic_tree: Dict[str, Any]
    state_variables: Dict[str, float]
    intention_candidate: Optional[Dict[str, Any]]
    computation_path: List[str]
    execution_trace: List[Dict[str, Any]]
    authority_grant: bool = False
    execution_admitted: bool = False


__all__ = ["CQCL_Living_Program"]
