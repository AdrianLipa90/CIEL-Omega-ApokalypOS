#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNTIME_WHEELS="$ROOT/vendor/wheels/runtime"

if [[ ! -d "$RUNTIME_WHEELS" ]]; then
  echo "[ERROR] Missing runtime wheelhouse: $RUNTIME_WHEELS" >&2
  exit 1
fi

missing=0
for pattern in "numpy-*.whl" "PyYAML-*.whl"; do
  if ! compgen -G "$RUNTIME_WHEELS/$pattern" > /dev/null; then
    echo "[ERROR] Missing required runtime wheel matching: $pattern" >&2
    missing=1
  fi
done

if [[ $missing -ne 0 ]]; then
  echo "[ERROR] Offline runtime bootstrap cannot continue until required wheels are populated." >&2
  exit 1
fi

python -m pip install --no-index --find-links "$RUNTIME_WHEELS" -e "$ROOT"

if compgen -G "$RUNTIME_WHEELS/flask-*.whl" > /dev/null; then
  python -m pip install --no-index --find-links "$RUNTIME_WHEELS" -e "$ROOT[gui]"
fi

echo "[OK] Offline runtime bootstrap finished using local wheelhouse only."
