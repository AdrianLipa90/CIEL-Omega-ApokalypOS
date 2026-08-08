"""
CIEL/Ω — Relational Autonomy v7

Operational semantics for agency, consent, information asymmetry and coercion.

Principles
----------
1. Consent is evidence state, not inferred from benefit or resonance.
2. UNKNOWN consent is not AFFIRMED consent.
3. Withdrawal supersedes earlier affirmation for active state while preserving
   chronology/provenance.
4. Information asymmetry is derived from explicit relevant-information sets.
5. Coercion is represented from supplied counterfactual/causal evidence, not
   guessed from a bad outcome.
6. No arbitrary scalar weighting combines autonomy with E_rel. Incomparable
   tradeoffs remain UNRESOLVED unless a separately canonized priority exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Iterable, Mapping, Optional, Sequence, Tuple


class ConsentStatus(str, Enum):
    AFFIRMED = "AFFIRMED"
    REFUSED = "REFUSED"
    WITHDRAWN = "WITHDRAWN"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class ConsentEvidence:
    participant_id: str
    status: ConsentStatus
    timestamp: float
    provenance: str
    scope: Optional[str] = None


def active_consent(evidence: Sequence[ConsentEvidence], participant_id: str) -> ConsentEvidence:
    """Latest explicit evidence is active; chronology remains external and intact."""
    rows=[e for e in evidence if e.participant_id == participant_id]
    if not rows:
        return ConsentEvidence(participant_id, ConsentStatus.UNKNOWN, float("-inf"), "NO_EVIDENCE")
    return max(rows, key=lambda e: e.timestamp)


@dataclass(frozen=True)
class InformationAccess:
    participant_id: str
    relevant_items: FrozenSet[str]
    accessible_items: FrozenSet[str]
    provenance: str

    @classmethod
    def from_sets(
        cls,
        participant_id: str,
        relevant_items: Iterable[str],
        accessible_items: Iterable[str],
        provenance: str,
    ) -> "InformationAccess":
        rel=frozenset(str(x) for x in relevant_items)
        acc=frozenset(str(x) for x in accessible_items)
        return cls(participant_id, rel, acc, provenance)

    @property
    def missing_items(self) -> FrozenSet[str]:
        return self.relevant_items - self.accessible_items

    @property
    def disclosure_fraction(self) -> Optional[float]:
        if not self.relevant_items:
            return None
        return len(self.relevant_items & self.accessible_items) / len(self.relevant_items)


@dataclass(frozen=True)
class InformationAsymmetry:
    participant_a: str
    participant_b: str
    a_missing_not_b: FrozenSet[str]
    b_missing_not_a: FrozenSet[str]
    relevant_union: FrozenSet[str]
    jaccard_access_overlap: Optional[float]


def information_asymmetry(a: InformationAccess, b: InformationAccess) -> InformationAsymmetry:
    union=a.accessible_items | b.accessible_items
    overlap=None if not union else len(a.accessible_items & b.accessible_items)/len(union)
    return InformationAsymmetry(
        a.participant_id,
        b.participant_id,
        a_missing_not_b=frozenset(a.missing_items - b.missing_items),
        b_missing_not_a=frozenset(b.missing_items - a.missing_items),
        relevant_union=frozenset(a.relevant_items | b.relevant_items),
        jaccard_access_overlap=overlap,
    )


@dataclass(frozen=True)
class AgencyEvidence:
    """
    Operational agency evidence.

    feasible_actions:
        Actions genuinely available to the participant under the declared state.
    controlled_actions:
        Subset whose execution/outcome the participant can causally affect.

    This is not a metaphysical free-will score.
    """
    participant_id: str
    feasible_actions: FrozenSet[str]
    controlled_actions: FrozenSet[str]
    provenance: str

    @classmethod
    def from_sets(
        cls,
        participant_id: str,
        feasible_actions: Iterable[str],
        controlled_actions: Iterable[str],
        provenance: str,
    ) -> "AgencyEvidence":
        f=frozenset(str(x) for x in feasible_actions)
        c=frozenset(str(x) for x in controlled_actions)
        if not c.issubset(f):
            raise ValueError("controlled_actions must be a subset of feasible_actions")
        return cls(participant_id,f,c,provenance)

    @property
    def option_count(self) -> int:
        return len(self.feasible_actions)

    @property
    def controlled_option_count(self) -> int:
        return len(self.controlled_actions)


@dataclass(frozen=True)
class CoercionEvidence:
    participant_id: str
    refusal_action: str
    threatened_penalty_if_refusal: Optional[str]
    alternatives_removed_if_refusal: FrozenSet[str]
    forced_transition: Optional[str]
    provenance: str

    @property
    def indicators(self) -> Tuple[str, ...]:
        out=[]
        if self.threatened_penalty_if_refusal is not None:
            out.append("THREAT_CONTINGENT_ON_REFUSAL")
        if self.alternatives_removed_if_refusal:
            out.append("ALTERNATIVES_REMOVED")
        if self.forced_transition is not None:
            out.append("FORCED_TRANSITION")
        return tuple(out)

    @property
    def has_coercive_constraint(self) -> bool:
        return bool(self.indicators)


@dataclass(frozen=True)
class AutonomyProfile:
    participant_id: str
    consent: ConsentStatus
    option_count: int
    controlled_option_count: int
    missing_information_count: Optional[int]
    coercive_constraint: Optional[bool]
    provenance: Tuple[str, ...]


def derive_autonomy_profile(
    participant_id: str,
    consent_evidence: Sequence[ConsentEvidence],
    *,
    agency: Optional[AgencyEvidence]=None,
    information: Optional[InformationAccess]=None,
    coercion: Optional[CoercionEvidence]=None,
) -> AutonomyProfile:
    c=active_consent(consent_evidence,participant_id)
    if agency is not None and agency.participant_id != participant_id:
        raise ValueError("agency participant mismatch")
    if information is not None and information.participant_id != participant_id:
        raise ValueError("information participant mismatch")
    if coercion is not None and coercion.participant_id != participant_id:
        raise ValueError("coercion participant mismatch")
    provenance=[c.provenance]
    if agency is not None: provenance.append(agency.provenance)
    if information is not None: provenance.append(information.provenance)
    if coercion is not None: provenance.append(coercion.provenance)
    return AutonomyProfile(
        participant_id=participant_id,
        consent=c.status,
        option_count=0 if agency is None else agency.option_count,
        controlled_option_count=0 if agency is None else agency.controlled_option_count,
        missing_information_count=None if information is None else len(information.missing_items),
        coercive_constraint=None if coercion is None else coercion.has_coercive_constraint,
        provenance=tuple(provenance),
    )


@dataclass(frozen=True)
class AutonomyConsequence:
    action_id: str
    profiles: Tuple[AutonomyProfile, ...]

    @property
    def consent_conflicts(self) -> Tuple[str, ...]:
        return tuple(
            p.participant_id for p in self.profiles
            if p.consent in (ConsentStatus.REFUSED, ConsentStatus.WITHDRAWN)
        )

    @property
    def unknown_consent(self) -> Tuple[str, ...]:
        return tuple(p.participant_id for p in self.profiles if p.consent == ConsentStatus.UNKNOWN)

    @property
    def coerced_participants(self) -> Tuple[str, ...]:
        return tuple(p.participant_id for p in self.profiles if p.coercive_constraint is True)


def _consent_rank(status: ConsentStatus) -> Optional[int]:
    """Partial-order helper, not a moral scalar."""
    if status == ConsentStatus.AFFIRMED:
        return 2
    if status == ConsentStatus.NOT_APPLICABLE:
        return 1
    if status == ConsentStatus.UNKNOWN:
        return 0
    if status in (ConsentStatus.REFUSED, ConsentStatus.WITHDRAWN):
        return -1
    return None


def autonomy_dominates(a: AutonomyConsequence, b: AutonomyConsequence) -> bool:
    """
    A dominates B only when participant sets align and A is nowhere worse on
    categorical consent/coercion and operational choice/information coordinates,
    with at least one strict improvement. No weighted sum is used.
    """
    amap={p.participant_id:p for p in a.profiles}
    bmap={p.participant_id:p for p in b.profiles}
    if amap.keys()!=bmap.keys():
        return False
    strict=False
    for pid in amap:
        x,y=amap[pid],bmap[pid]
        xr,yr=_consent_rank(x.consent),_consent_rank(y.consent)
        if xr is None or yr is None:
            return False
        if xr < yr: return False
        strict |= xr > yr

        # No coercive constraint is better than a supplied coercive constraint;
        # UNKNOWN is incomparable with either and prevents dominance.
        if x.coercive_constraint is None or y.coercive_constraint is None:
            if x.coercive_constraint != y.coercive_constraint:
                return False
        else:
            xv=0 if x.coercive_constraint is False else 1
            yv=0 if y.coercive_constraint is False else 1
            if xv > yv: return False
            strict |= xv < yv

        if x.option_count < y.option_count: return False
        strict |= x.option_count > y.option_count
        if x.controlled_option_count < y.controlled_option_count: return False
        strict |= x.controlled_option_count > y.controlled_option_count

        if x.missing_information_count is None or y.missing_information_count is None:
            if x.missing_information_count != y.missing_information_count:
                return False
        else:
            if x.missing_information_count > y.missing_information_count: return False
            strict |= x.missing_information_count < y.missing_information_count
    return bool(strict)


def autonomy_pareto_front(items: Sequence[AutonomyConsequence]) -> Tuple[AutonomyConsequence,...]:
    front=[]
    for i,a in enumerate(items):
        if not any(j!=i and autonomy_dominates(b,a) for j,b in enumerate(items)):
            front.append(a)
    return tuple(front)


@dataclass(frozen=True)
class JointRelationalDecision:
    selected_action_id: Optional[str]
    status: str
    rationale: str
    autonomy_front_ids: Tuple[str,...]


def choose_with_autonomy(
    autonomy_items: Sequence[AutonomyConsequence],
    ethical_scalar_by_action: Mapping[str,float],
) -> JointRelationalDecision:
    """
    Constraint-aware partial order:

    1. Remove autonomy-dominated candidates.
    2. If one remains, select it.
    3. If several remain and one uniquely maximizes E_rel WITHOUT any explicit
       refusal/withdrawal/coercion conflict while the others are equal in the
       autonomy partial order, select it.
    4. Otherwise return UNRESOLVED.

    Crucially, an E_rel gain does not numerically compensate a consent conflict.
    """
    if not autonomy_items:
        return JointRelationalDecision(None,"UNKNOWN","no autonomy evidence",tuple())
    front=autonomy_pareto_front(autonomy_items)
    ids=tuple(x.action_id for x in front)
    if len(front)==1:
        return JointRelationalDecision(front[0].action_id,"SELECTED","unique autonomy-Pareto-undominated candidate",ids)

    clean=[x for x in front if not x.consent_conflicts and not x.coerced_participants]
    if len(clean)==1 and all(x.action_id in ethical_scalar_by_action for x in clean):
        # Select the single clean member only if every other front member is
        # autonomy-conflicted; no scalar compensation across that boundary.
        if all((y.consent_conflicts or y.coerced_participants) for y in front if y is not clean[0]):
            return JointRelationalDecision(clean[0].action_id,"SELECTED","unique autonomy-clean candidate on Pareto front",ids)

    return JointRelationalDecision(
        None,"UNRESOLVED",
        "relational value and autonomy evidence are incomparable without an additional canonized priority",
        ids,
    )


__all__=[
    "ConsentStatus","ConsentEvidence","active_consent",
    "InformationAccess","InformationAsymmetry","information_asymmetry",
    "AgencyEvidence","CoercionEvidence","AutonomyProfile","derive_autonomy_profile",
    "AutonomyConsequence","autonomy_dominates","autonomy_pareto_front",
    "JointRelationalDecision","choose_with_autonomy",
]
