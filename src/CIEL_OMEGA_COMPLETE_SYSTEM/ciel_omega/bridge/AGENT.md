# AGENT

This folder is the `bridge` sector of the canonical runtime.

## Primary role
Inter-sector transport and white-thread coupling layer.

## Parent
- [ciel_omega](../README.md)

## Lateral links
- [constraints](../constraints/AGENT.md)
- [runtime](../runtime/AGENT.md)
- [memory](../memory/AGENT.md)
- [fields](../fields/AGENT.md)
- [vocabulary](../vocabulary/AGENT.md)

## Operational rule
- prefer `route` semantics for actions touching this sector
- do not bypass explicit neighboring sectors when a bridge or constraint is required
