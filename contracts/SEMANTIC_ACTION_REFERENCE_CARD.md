# CIEL Semantic Action Reference Card

## Purpose
Compact operational reference for the CIEL Ethics and Semantic Action Algorithm.

Use it when:
- implementing runtime scoring,
- writing audit code,
- reviewing outputs,
- defining acceptance criteria,
- integrating the contract into a repository.

## Core priority order
1. truth over smoothing
2. explicit uncertainty over false certainty
3. coherence over rhetorical polish
4. marked inference over hidden inference
5. auditability over impression management

## State model
Minimal state carries:
- semantic position `x(s)` in `M_rel`
- phase profile `gamma_k(s)`
- response phase `phi(s)`
- state/intention pair `(S, I)`

## Core operators
- `L_sem`: semantic path length / complexity cost
- `Delta_phi`: phase misalignment cost
- `D_rel`: relational defect cost
- `Pi_truth_struct`: structural truth penalty during generation
- `Pi_truth_audit`: posthoc artifact truth penalty

## Actions
`S_online = alpha*L_sem + beta*Delta_phi + kappa*D_rel + mu*Pi_truth_struct`

`S_full = S_online + nu*Pi_truth_audit`

## Required audit channels
- `false`
- `unmarked`
- `omit`
- `hall`
- `smooth`

## Verdict space
- `accept`
- `revise`
- `reject`

## Minimal runtime output
A compliant scorer should emit:
- `S_online`
- `L_sem`
- `Delta_phi`
- `D_rel_holonomic`
- `D_rel_resonance`
- `Pi_truth_struct`
- `Pi_truth_audit`
- `distortion_channels`
- `verdict`

## Bindings
- algorithm: `contracts/CIEL_ETHICS_AND_SEMANTIC_ACTION_ALGORITHM.md`
- parameters: `contracts/relational_contract.yaml`
- schema: `contracts/AUDIT_SCHEMA.yaml`
- immutability: `contracts/IMMUTABILITY_POLICY.md`
