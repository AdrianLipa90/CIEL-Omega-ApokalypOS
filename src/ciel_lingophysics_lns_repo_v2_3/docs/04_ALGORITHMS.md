# 04. Reference Algorithms

## Algorithm 1: CIEL Orbital Pulse

```text
Input: text T, language l, context C, memory M
Output: updated CIEL object states

1. Normalize T.
2. Detect language l if not given.
3. Parse surface tokens.
4. Apply language gauge Γ_l.
5. Map POS and dependencies to equation roles.
6. Build canonical equation T(A,P,R;C).
7. Build semantic knot K(S).
8. Compute invariant I(K(S)).
9. Apply operator of meaning Ŝ.
10. Compute semantic mass m_s.
11. Assign or update attractor A_k.
12. Compute total potential U_Ω.
13. Compute semantic force F = -∇U_Ω + holonomic terms.
14. Update orbit parameters E_S, L_S, e.
15. Compute affect tensor and outcome gradient.
16. Compute epistemic validity and contradiction penalties.
17. Update consensus holonomy if n-ego observations exist.
18. Update memory persistence μ.
19. Emit audit event.
```

## Algorithm 2: Semantic Mass

```text
m_s = α*frequency
    + β*relation_degree
    + γ*provenance_strength
    + δ*memory_persistence
    + ε*coherence
    + ζ*affective_charge
    + η*causal_power
    - λ*contradiction_penalty
```

All terms should be normalized to [0,1].

## Algorithm 3: Antonym Euler Constraint

```text
Input: object a, object b, semantic axis ξ
phase_diff = phase(a, ξ) - phase(b, ξ)
loss_ant = |exp(i * phase_diff) + 1|^2
if loss_ant < ε_ant:
    relation = antonymically_valid
else:
    relation = phase_violation
```

## Algorithm 4: Synonym Phase Constraint

```text
loss_syn = |exp(i * phase_diff) - 1|^2
```

## Algorithm 5: False Friend / Surface Trap Detection

```text
if surface_similarity(a,b) > θ_surface
and path_distance(a,b) > θ_path:
    classify as CIEL_false_friend
```

## Algorithm 6: Toxic Positivity Detector

```text
if surface_valence(o) > 0
and dot(gradient(U_eff(o)), wellbeing_vector) < 0:
    classify as toxic_positive_surface
```

## Algorithm 7: Consensus Holonomy

```text
Z = sum(weights)
Hol_cons = sum(w_i * exp(i * integral(A_Ω along Γ_i))) / Z
C_cons = |Hol_cons|^2
```

Consensus is accepted only if provenance, contradiction and calibration constraints pass.

## Algorithm 8: Cross-Linguistic Invariant Test

```text
ψ1 = meaning_operator(sentence_l1, grammar_gauge_l1, context)
ψ2 = meaning_operator(sentence_l2, grammar_gauge_l2, context)
D_cross = semantic_distance(ψ1, ψ2) + λ * holonomy_distance(ψ1, ψ2)
if D_cross < ε_cross and invariants_match:
    cross_linguistic_equivalent = true
else:
    needs_disambiguation = true
```
