#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNTIME_WHEELS="$ROOT/vendor/wheels/runtime"
DEV_WHEELS="$ROOT/vendor/wheels/dev"

for dir in "$RUNTIME_WHEELS" "$DEV_WHEELS"; do
  if [[ ! -d "$dir" ]]; then
    echo "[ERROR] Missing wheelhouse: $dir" >&2
    exit 1
  fi
done

missing=0
for pattern in "numpy-*.whl" "PyYAML-*.whl"; do
  if ! compgen -G "$RUNTIME_WHEELS/$pattern" > /dev/null; then
    echo "[ERROR] Missing required runtime wheel matching: $pattern" >&2
    missing=1
  fi
done

for pattern in "pytest-*.whl" "ruff-*.whl" "mypy-*.whl"; do
  if ! compgen -G "$DEV_WHEELS/$pattern" > /dev/null; then
    echo "[ERROR] Missing required dev wheel matching: $pattern" >&2
    missing=1
  fi
done

if [[ $missing -ne 0 ]]; then
  echo "[ERROR] Offline dev bootstrap cannot continue until required wheels are populated." >&2
  exit 1
fi

python -m pip install --no-index --find-links "$RUNTIME_WHEELS" --find-links "$DEV_WHEELS" -e "$ROOT[dev]"

if compgen -G "$RUNTIME_WHEELS/flask-*.whl" > /dev/null || compgen -G "$DEV_WHEELS/flask-*.whl" > /dev/null; then
  python -m pip install --no-index --find-links "$RUNTIME_WHEELS" --find-links "$DEV_WHEELS" -e "$ROOT[dev,gui]"
fi

echo "[OK] Offline dev bootstrap finished using local wheelhouses only."
