# Android app (wtctg4)

Ten katalog zawiera szablon aplikacji Android (Kotlin + XML) dla CIEL SOT Agent.

## Wymagania kompilacji

- JDK 17 lub 21 (JDK 25 nie jest wspierane przez Android Gradle Plugin).
- Android SDK zainstalowany lokalnie (ustawiony w `local.properties`).
- Dostęp do repozytoriów Maven/Google (`dl.google.com`, `repo.maven.apache.org`).

## Uruchomienie lokalnie

1. Skopiuj `local.properties.example` do `local.properties` i ustaw `sdk.dir`.
2. Otwórz `src/android_app` w Android Studio (Hedgehog lub nowsze).
3. Ustaw JDK projektu na 17 lub 21.
4. Pozwól IDE zsynchronizować Gradle.
5. Uruchom moduł `app` na emulatorze lub urządzeniu.

## Testy

- `./gradlew test` — testy jednostkowe JVM.
- `./gradlew connectedAndroidTest` — testy instrumentacyjne (emulator/urządzenie).
- `./gradlew lint` — kontrola jakości Android lint.

## Przygotowanie do produkcji

1. Ustaw podpisywanie release (`signingConfigs`) przez `keystore.properties` / sekrety CI.
2. Włącz i zweryfikuj shrink/obfuscation (`minifyEnabled true`) dla wydania release.
3. Skonfiguruj pipeline CI z `test`, `lint`, oraz budową `assembleRelease`.
4. Przed publikacją zwiększ `versionCode` i `versionName`.


## Rozwiązywanie problemu "SDK location not found"

Jeżeli widzisz błąd:

`SDK location not found` lub `sdk.dir ... Directory does not exist`,
to znaczy, że `local.properties` wskazuje złą ścieżkę.

Użyj skryptu:

```bash
cd src/android_app
./scripts/configure_local_sdk.sh
```

Następnie zweryfikuj:

```bash
cat local.properties
ls -la "$(cut -d= -f2 local.properties)"
```

I dopiero potem uruchom build:

```bash
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 gradle :app:assembleDebug
```


## Instalacja na telefonie (adb)

Użyj gotowego skryptu, który buduje i instaluje debug APK oraz obsługuje najczęstsze błędy instalacji:

```bash
cd src/android_app
./scripts/install_debug.sh
```

Skrypt automatycznie:
- szuka `adb` najpierw w `PATH`, a potem automatycznie w `sdk.dir/platform-tools/adb`,
- używa `./gradlew` jeśli jest dostępny, w przeciwnym razie systemowego `gradle`,
- konfiguruje `local.properties` (jeśli go nie ma),
- sprawdza podłączone urządzenie i API (min 21),
- buduje `:app:assembleDebug`,
- próbuje `adb install -r`,
- przy `INSTALL_FAILED_UPDATE_INCOMPATIBLE` / `INSTALL_FAILED_VERSION_DOWNGRADE` odinstalowuje starą wersję i instaluje ponownie.
