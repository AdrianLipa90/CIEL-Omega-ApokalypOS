# OMEGA internal interface canon

## Single canonical internal execution axis

The internal Omega execution axis is now:

`CIELOrchestrator -> CIELClient -> UnifiedSystem`

### Meaning
- `CIELOrchestrator` is the human-facing top-level control surface.
- `CIELClient` is the minimal local communication surface.
- `UnifiedSystem` is the composite surface that binds orchestrator, client, and bridge into one testable object.

## Anti-pattern removed
`UnifiedSystem` no longer fabricates dummy fallback orchestrator stand-ins.
A missing orchestrator is now an error in architecture, not something to be silently imitated.

## Consequence for refactor
Any new local entrypoint or package-facing helper should delegate into one of these three surfaces rather than creating a fourth parallel control surface.
