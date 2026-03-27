#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
INSTALL_LLAMA="${INSTALL_LLAMA:-0}"
LLAMA_BACKEND="${LLAMA_BACKEND:-cpu}"

"$PYTHON_BIN" -m venv "$VENV_DIR"

"$VENV_DIR/bin/python" -m pip install --upgrade pip

if [ "$INSTALL_LLAMA" = "1" ]; then
  if [ "$LLAMA_BACKEND" = "cuda" ]; then
    CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 "$VENV_DIR/bin/pip" install -e ".[llama]"
  else
    "$VENV_DIR/bin/pip" install -e ".[llama]"
  fi
else
  "$VENV_DIR/bin/pip" install -e .
fi

echo ""
echo "Installed."
echo "Run UI:   $VENV_DIR/bin/ciel-omega"
echo "Run CLI:  $VENV_DIR/bin/ciel-cli list"
echo ""
