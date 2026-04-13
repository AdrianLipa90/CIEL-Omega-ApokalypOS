#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if [[ ! -f local.properties ]]; then
  echo "[INFO] Brak local.properties. Próbuję auto-konfiguracji SDK..."
  ./scripts/configure_local_sdk.sh
fi

SDK_DIR=""
if [[ -f local.properties ]]; then
  SDK_DIR="$(cut -d= -f2- local.properties | head -n1)"
fi
if [[ -z "$SDK_DIR" && -n "${ANDROID_SDK_ROOT:-}" ]]; then
  SDK_DIR="$ANDROID_SDK_ROOT"
fi
if [[ -z "$SDK_DIR" && -n "${ANDROID_HOME:-}" ]]; then
  SDK_DIR="$ANDROID_HOME"
fi

ADB_BIN=""
if command -v adb >/dev/null 2>&1; then
  ADB_BIN="$(command -v adb)"
elif [[ -n "$SDK_DIR" && -x "$SDK_DIR/platform-tools/adb" ]]; then
  ADB_BIN="$SDK_DIR/platform-tools/adb"
fi

if [[ -z "$ADB_BIN" ]]; then
  echo "[ERROR] adb nie jest dostępny w PATH i nie znaleziono go w SDK ($SDK_DIR/platform-tools/adb)."
  echo "        Dodaj do PATH: export PATH=\"$SDK_DIR/platform-tools:\$PATH\""
  exit 1
fi

GRADLE_BIN=""
if [[ -x "./gradlew" ]]; then
  GRADLE_BIN="./gradlew"
elif command -v gradle >/dev/null 2>&1; then
  GRADLE_BIN="$(command -v gradle)"
fi

if [[ -z "$GRADLE_BIN" ]]; then
  echo "[ERROR] Nie znaleziono gradle/gradlew. Zainstaluj Gradle albo dodaj gradle wrapper."
  exit 1
fi

ADB_DEVICE_COUNT=$($ADB_BIN devices | awk 'NR>1 && $2=="device" {count++} END {print count+0}')
if [[ "$ADB_DEVICE_COUNT" -lt 1 ]]; then
  echo "[ERROR] Nie wykryto urządzenia adb w stanie 'device'."
  echo "        Włącz debugowanie USB i zaakceptuj klucz RSA na telefonie."
  exit 1
fi

DEVICE_API=$($ADB_BIN shell getprop ro.build.version.sdk | tr -d '\r')
if [[ -n "$DEVICE_API" && "$DEVICE_API" -lt 29 ]]; then
  echo "[ERROR] Urządzenie ma API $DEVICE_API, a aplikacja wymaga minSdk 29."
  exit 1
fi

echo "[INFO] Buduję APK debug przez: $GRADLE_BIN"
$GRADLE_BIN :app:assembleDebug

APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
if [[ ! -f "$APK_PATH" ]]; then
  echo "[ERROR] Nie znaleziono $APK_PATH"
  exit 1
fi

echo "[INFO] Instaluję APK przez: $ADB_BIN install -r"
set +e
INSTALL_OUTPUT=$($ADB_BIN install -r "$APK_PATH" 2>&1)
INSTALL_CODE=$?
set -e

if [[ "$INSTALL_CODE" -eq 0 ]]; then
  echo "$INSTALL_OUTPUT"
  echo "[OK] Instalacja zakończona sukcesem."
  exit 0
fi

echo "$INSTALL_OUTPUT"

if echo "$INSTALL_OUTPUT" | grep -q "INSTALL_FAILED_UPDATE_INCOMPATIBLE"; then
  echo "[WARN] Konflikt podpisu z już zainstalowaną aplikacją. Odinstalowuję i instaluję ponownie..."
  $ADB_BIN uninstall com.ciel.sotagent.debug >/dev/null 2>&1 || true
  $ADB_BIN uninstall com.ciel.sotagent >/dev/null 2>&1 || true
  $ADB_BIN install "$APK_PATH"
  echo "[OK] Ponowna instalacja zakończona sukcesem."
  exit 0
fi

if echo "$INSTALL_OUTPUT" | grep -q "INSTALL_FAILED_VERSION_DOWNGRADE"; then
  echo "[WARN] Wykryto downgrade wersji. Odinstalowuję poprzednią wersję i instaluję ponownie..."
  $ADB_BIN uninstall com.ciel.sotagent.debug >/dev/null 2>&1 || true
  $ADB_BIN uninstall com.ciel.sotagent >/dev/null 2>&1 || true
  $ADB_BIN install "$APK_PATH"
  echo "[OK] Instalacja po odinstalowaniu zakończona sukcesem."
  exit 0
fi

echo "[ERROR] Instalacja nie powiodła się. Sprawdź log powyżej."
exit "$INSTALL_CODE"
