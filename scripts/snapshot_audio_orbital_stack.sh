#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="/mnt/data/audio_orbital_stack_snapshot.tar.gz"
tar -czf "$OUT" \
  -C "$ROOT" \
  integration/imports/audio_orbital_stack \
  scripts/bootstrap_audio_orbital_stack.py \
  scripts/run_audio_orbital_probe.py
 echo "$OUT"
