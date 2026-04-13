# Android app (wtctg4)

Ten katalog zawiera szablon aplikacji Android (Kotlin + XML) dla CIEL SOT Agent.

## Uruchomienie lokalnie

1. Otwórz `src/android_app` w Android Studio (Hedgehog lub nowsze).
2. Pozwól IDE zsynchronizować Gradle.
3. Uruchom moduł `app` na emulatorze lub urządzeniu.

## Testy

- `./gradlew test` — testy jednostkowe JVM.
- `./gradlew connectedAndroidTest` — testy instrumentacyjne (emulator/urządzenie).
- `./gradlew lint` — kontrola jakości Android lint.

## Przygotowanie do produkcji

1. Ustaw podpisywanie release (`signingConfigs`) przez `keystore.properties` / sekrety CI.
2. Włącz i zweryfikuj shrink/obfuscation (`minifyEnabled true`) dla wydania release.
3. Skonfiguruj pipeline CI z `test`, `lint`, oraz budową `assembleRelease`.
4. Przed publikacją zwiększ `versionCode` i `versionName`.
