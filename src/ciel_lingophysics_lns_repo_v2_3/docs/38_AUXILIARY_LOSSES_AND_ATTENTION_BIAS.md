# Auxiliary Losses and Attention Bias

v1.9 defines two model-facing mechanisms.

## Auxiliary losses

Auxiliary tasks teach a model to predict structural features:

```text
L_total = L_lm
        + λ_op L_operator
        + λ_role L_event_roles
        + λ_scope L_scope
        + λ_tame L_tame
        + λ_phase L_phase
        + λ_graph L_graph
```

The weights are configuration values, not claims about reality.

## Attention bias

Given ordinary attention logits:

```text
A_ij = Q_i K_j^T / sqrt(d)
```

CIEL adds a structural bias:

```text
A'_ij = A_ij + B_CIEL(i,j)
```

Reference form:

```text
B_CIEL(i,j) =
    w_op       * operator_link(i,j)
  + w_frame    * event_frame_link(i,j)
  + w_scope    * scope_compatibility(i,j)
  + w_case     * case_role_link(i,j)
  + w_phase    * phase_compatibility(i,j)
  - w_conflict * invariant_conflict(i,j)
```

This is intentionally model-agnostic. The reference implementation returns a numeric bias matrix from CIEL feature tokens. It can be consumed by a custom transformer, adapter, or validator.

## Validator loop

A generated output is accepted only if:

- required operators are preserved,
- event-frame roles are not swapped,
- scope status is resolved or explicitly marked unresolved,
- antonym/synonym phase constraints are respected,
- cross-language reconstruction cost remains below a configured threshold.

When a check fails, the output is not silently rejected. The validator returns a structured report.
