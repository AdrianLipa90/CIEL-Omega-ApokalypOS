# AGENT

This folder is the `runtime` sector of the canonical runtime.

## Primary role
Execution and live activation layer.

## Parent
- [ciel_omega](../README.md)

## Lateral links
- [constraints](../constraints/AGENT.md)
- [memory](../memory/AGENT.md)
- [bridge](../bridge/AGENT.md)
- [fields](../fields/AGENT.md)

## Operational rule
- prefer `run` semantics for actions touching this sector
- do not bypass explicit neighboring sectors when a bridge or constraint is required
