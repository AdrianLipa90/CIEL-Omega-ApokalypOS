# Runtime Wheelhouse

Place runtime and build-backend wheel files here.

## Required package family
- `setuptools`
- `wheel`
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
PyYAML wheel matching is case-insensitive because pip may save it as `pyyaml-...whl`.
