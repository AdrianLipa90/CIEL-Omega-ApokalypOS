#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if ! command -v adb >/dev/null 2>&1; then
  echo "[ERROR] adb nie jest dostępny w PATH. Zainstaluj Android platform-tools."
  exit 1
fi

if ! command -v gradle >/dev/null 2>&1; then
  echo "[ERROR] gradle nie jest dostępny w PATH."
  exit 1
fi

if [[ ! -f local.properties ]]; then
  echo "[INFO] Brak local.properties. Próbuję auto-konfiguracji SDK..."
  ./scripts/configure_local_sdk.sh
fi

ADB_DEVICE_COUNT=$(adb devices | awk 'NR>1 && $2=="device" {count++} END {print count+0}')
if [[ "$ADB_DEVICE_COUNT" -lt 1 ]]; then
  echo "[ERROR] Nie wykryto urządzenia adb w stanie 'device'."
  echo "        Włącz debugowanie USB i zaakceptuj klucz RSA na telefonie."
  exit 1
fi

DEVICE_API=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
if [[ -n "$DEVICE_API" && "$DEVICE_API" -lt 21 ]]; then
  echo "[ERROR] Urządzenie ma API $DEVICE_API, a aplikacja wymaga minSdk 21."
  exit 1
fi

echo "[INFO] Buduję APK debug..."
gradle :app:assembleDebug

APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
if [[ ! -f "$APK_PATH" ]]; then
  echo "[ERROR] Nie znaleziono $APK_PATH"
  exit 1
fi

echo "[INFO] Instaluję APK (adb install -r)..."
set +e
INSTALL_OUTPUT=$(adb install -r "$APK_PATH" 2>&1)
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
  adb uninstall com.ciel.sotagent.debug >/dev/null 2>&1 || true
  adb uninstall com.ciel.sotagent >/dev/null 2>&1 || true
  adb install "$APK_PATH"
  echo "[OK] Ponowna instalacja zakończona sukcesem."
  exit 0
fi

if echo "$INSTALL_OUTPUT" | grep -q "INSTALL_FAILED_VERSION_DOWNGRADE"; then
  echo "[WARN] Wykryto downgrade wersji. Odinstalowuję poprzednią wersję i instaluję ponownie..."
  adb uninstall com.ciel.sotagent.debug >/dev/null 2>&1 || true
  adb uninstall com.ciel.sotagent >/dev/null 2>&1 || true
  adb install "$APK_PATH"
  echo "[OK] Instalacja po odinstalowaniu zakończona sukcesem."
  exit 0
fi

echo "[ERROR] Instalacja nie powiodła się. Sprawdź log powyżej."
exit "$INSTALL_CODE"
