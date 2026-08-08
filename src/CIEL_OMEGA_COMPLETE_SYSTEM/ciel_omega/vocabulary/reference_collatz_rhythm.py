"""Source-reference twin-prime Collatz rhythm harness.

Parent: Hilbert_Kahler_Phase_Intention_Hamiltonian, eqs. (54)-(56).

For twin-prime seed s=(p,p+2), define paired orbit
    O_s(k)=(C^k(p),C^k(p+2)) = (a_k,b_k)
and the document's convenient reference rhythm
    rho_ref(k) = [log(1+a_k)+log(1+b_k)] /
                 [1+log(1+a_k+b_k)].

The source explicitly says this is one convenient reference rule, not a unique
canonical law. This module therefore labels every output REFERENCE_RULE and
provides a GeneratorInputContract-compatible wrapper that cannot pass the canon
gate unless a future derivation promotes a different law with provenance.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Tuple


def is_prime(n: int) -> bool:
    n=int(n)
    if n<2: return False
    if n%2==0: return n==2
    r=int(math.isqrt(n))
    for d in range(3,r+1,2):
        if n%d==0: return False
    return True


def validate_twin_prime_seed(p: int) -> tuple[int,int]:
    p=int(p); q=p+2
    if not (is_prime(p) and is_prime(q)):
        raise ValueError("seed must be a twin-prime pair (p,p+2)")
    return p,q


def collatz_step(n: int) -> int:
    n=int(n)
    if n<=0: raise ValueError("Collatz state must be positive")
    return n//2 if n%2==0 else 3*n+1


def collatz_iterate(n: int,k: int) -> int:
    n=int(n); k=int(k)
    if k<0: raise ValueError("k must be nonnegative")
    for _ in range(k):
        n=collatz_step(n)
    return n


def paired_collatz_state(seed_p: int,k: int) -> tuple[int,int]:
    p,q=validate_twin_prime_seed(seed_p)
    return collatz_iterate(p,k),collatz_iterate(q,k)


def reference_rho_from_pair(a_k: int,b_k: int) -> float:
    a=int(a_k); b=int(b_k)
    if a<=0 or b<=0: raise ValueError("paired Collatz states must be positive")
    return float((math.log1p(a)+math.log1p(b))/(1.0+math.log1p(a+b)))


def reference_rho(seed_p: int,k: int) -> float:
    a,b=paired_collatz_state(seed_p,k)
    return reference_rho_from_pair(a,b)


@dataclass(frozen=True)
class ReferenceRhythmReceipt:
    seed: tuple[int,int]
    k: int
    paired_state: tuple[int,int]
    rho_s: float
    status: str
    canonical_law_status: str
    provenance: str


def reference_rhythm_receipt(seed_p: int,k: int) -> ReferenceRhythmReceipt:
    seed=validate_twin_prime_seed(seed_p); pair=paired_collatz_state(seed_p,k)
    rho=reference_rho_from_pair(*pair)
    return ReferenceRhythmReceipt(
        seed=seed,k=int(k),paired_state=pair,rho_s=rho,
        status="SOURCE_REFERENCE_RULE_EXECUTABLE",
        canonical_law_status="OPEN_NOT_PROMOTED",
        provenance="Hilbert_Kahler_Phase_Intention_Hamiltonian eqs 54-56",
    )


def reference_rhythm_contract_input(seed_p: int,k: int):
    """Return contract input explicitly labeled REFERENCE_RULE."""
    from .generator_input_contract import reference_rhythm_input
    r=reference_rhythm_receipt(seed_p,k)
    return reference_rhythm_input(
        r.rho_s,
        f"{r.provenance}; seed={r.seed}; k={r.k}; paired_state={r.paired_state}",
        law_id="HILBERT_KAHLER_EQ56_REFERENCE_ONLY",
    )


__all__=[
    "is_prime","validate_twin_prime_seed","collatz_step","collatz_iterate",
    "paired_collatz_state","reference_rho_from_pair","reference_rho",
    "ReferenceRhythmReceipt","reference_rhythm_receipt","reference_rhythm_contract_input",
]
