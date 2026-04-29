#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

DIST_BUNDLE_DIR="${CIEL_BUNDLE_DIST:-$ROOT_DIR/dist_bundle}"
OUT_DIR="${CIEL_INSTALLER_DIST:-$ROOT_DIR/dist_installer}"

mkdir -p "$OUT_DIR"

if [[ ! -f "$DIST_BUNDLE_DIR/ciel-omega" || ! -f "$DIST_BUNDLE_DIR/ciel-cli" ]]; then
  "$PYTHON_BIN" "$ROOT_DIR/scripts/build_bundle.py"
fi

rm -f "$OUT_DIR/payload.tar.gz" "$OUT_DIR/payload.o" "$OUT_DIR/ciel-installer-linux"

tar -czf "$OUT_DIR/payload.tar.gz" -C "$DIST_BUNDLE_DIR" .

(
  cd "$OUT_DIR"
  ld -r -b binary -o payload.o payload.tar.gz
)

cc -O2 -s -Wl,-z,noexecstack -o "$OUT_DIR/ciel-installer-linux" \
  "$ROOT_DIR/scripts/installer_elf_linux.c" \
  "$OUT_DIR/payload.o"

chmod +x "$OUT_DIR/ciel-installer-linux"

echo "Built: $OUT_DIR/ciel-installer-linux"
