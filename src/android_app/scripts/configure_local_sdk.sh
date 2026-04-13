#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_PROPERTIES="$PROJECT_DIR/local.properties"

candidates=()

if [[ -n "${ANDROID_SDK_ROOT:-}" ]]; then
  candidates+=("$ANDROID_SDK_ROOT")
fi
if [[ -n "${ANDROID_HOME:-}" ]]; then
  candidates+=("$ANDROID_HOME")
fi
candidates+=("$HOME/Android/Sdk" "$HOME/Android/sdk" "/opt/android-sdk" "/usr/lib/android-sdk")

sdk_dir=""
for path in "${candidates[@]}"; do
  if [[ -d "$path" ]]; then
    sdk_dir="$path"
    break
  fi
done

if [[ -z "$sdk_dir" ]]; then
  cat <<MSG
[ERROR] Nie znaleziono katalogu Android SDK.
Sprawdź instalację SDK i ustaw ANDROID_SDK_ROOT lub ANDROID_HOME.
Przykład:
  export ANDROID_SDK_ROOT="$HOME/Android/Sdk"
  export ANDROID_HOME="$HOME/Android/Sdk"
MSG
  exit 1
fi

printf 'sdk.dir=%s\n' "$sdk_dir" > "$LOCAL_PROPERTIES"
echo "[OK] Zapisano $LOCAL_PROPERTIES"
echo "[OK] sdk.dir=$sdk_dir"
