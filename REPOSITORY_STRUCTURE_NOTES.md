# Repository Structure Notes

This file is a temporary navigation addendum created to close documentation gaps without rewriting existing top-level files through a limited write path.

## Operationally important folders now explicitly documented

- `scripts/`
- `.github/`
- `.github/workflows/`
- `integration/reports/`

## Primary human-readable anchors

- `README.md` — repository overview
- `docs/INDEX.md` — documentation navigation
- `docs/OPERATIONS.md` — operational layer bridge
- `scripts/README.md` — launcher layer
- `.github/workflows/README.md` — workflow layer
- `integration/reports/README.md` — generated report layer

## Reason this file exists

The repository already had strong architecture and registry documentation but weaker visibility for operational folders.
This addendum makes those layers discoverable immediately.

## Intended future cleanup

Once direct in-place update of existing top-level documents is available, the contents of this addendum should be folded into:

- `README.md`
- `docs/INDEX.md`

and this file may then be reduced or removed.
