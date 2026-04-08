# Runtime Wheelhouse

Place runtime wheel files here.

## Required package family
- `numpy`
- `PyYAML`

## Optional package family
- `flask` (for GUI extra)

## Install path
Used by:
- `tools/bootstrap/bootstrap_offline_runtime.sh`
- `tools/bootstrap/bootstrap_offline_dev.sh`

## Rule
Do not treat this directory as a valid offline runtime wheelhouse until the required `.whl` files are physically present.
