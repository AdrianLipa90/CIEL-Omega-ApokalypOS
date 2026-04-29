# Dev Wheelhouse

Place developer and test wheel files here.

## Required package family
- `pytest`
- `ruff`
- `mypy`

## Optional package family
- `flask` (when GUI tests or dev GUI bootstrap are required)

## Install path
Used by:
- `tools/bootstrap/bootstrap_offline_dev.sh`

## Rule
Do not treat this directory as a valid offline dev wheelhouse until the required `.whl` files are physically present.
