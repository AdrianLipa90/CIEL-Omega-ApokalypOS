# CIEL Orbital Control — Android

This directory contains the Kivy-based Android companion for **CIEL SOT Agent**.

The app connects to a running `ciel-sot-gui` Flask server and displays the key
observables (coherence index, system health, operating mode) in a native mobile UI
following the Quiet Orbital Control visual identity.

---

## Prerequisites

| Tool | Install |
|------|---------|
| Python 3.11+ | <https://python.org> |
| Buildozer ≥ 1.5 | `pip install buildozer` |
| Android SDK / NDK | managed automatically by Buildozer |
| Java (JDK 17) | `sudo apt install openjdk-17-jdk` |

On **Linux Mint / Ubuntu** also install:

```bash
sudo apt update
sudo apt install -y git zip unzip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake \
    libffi-dev libssl-dev python3-pip python3-venv
```

---

## Connecting to the backend

The app polls `GET /api/status` on the Flask backend (`ciel-sot-gui`).

| Scenario | Server URL |
|----------|-----------|
| Same machine (USB ADB) | `http://127.0.0.1:5050` (after `adb forward tcp:5050 tcp:5050`) |
| Same Wi-Fi network | `http://<desktop-ip>:5050` |

To change the server URL, edit `SERVER_URL` in `main.py` before building:

```python
class CIELOrbitalApp(App):
    SERVER_URL = "http://192.168.1.42:5050"
```

---

## Building the APK

```bash
cd packaging/android

# First build (downloads SDK/NDK — takes ~20 min):
buildozer android debug

# Subsequent builds:
buildozer android debug
```

The APK is produced at:

```
packaging/android/.buildozer/android/platform/build-<arch>/dists/ciel_orbital_control/
```

A convenience copy is also placed in:

```
packaging/android/bin/ciel_orbital_control-<version>-debug.apk
```

---

## Deploying to a device

Connect your Android device via USB (with USB debugging enabled), then:

```bash
# Build and install in one step:
buildozer android debug deploy run

# Or install a pre-built APK:
adb install bin/ciel_orbital_control-*-debug.apk
```

---

## ADB port forwarding (same machine)

If the `ciel-sot-gui` server runs on the same machine as the phone is connected to:

```bash
# Forward device port 5050 to host port 5050
adb forward tcp:5050 tcp:5050
```

Then keep `SERVER_URL = "http://127.0.0.1:5050"` (the default).

---

## Release build

```bash
buildozer android release
```

Sign the release APK with your keystore before distributing.

---

## Directory structure

```
packaging/android/
├── main.py              Kivy application (screens, KV layout, status polling)
├── buildozer.spec       Buildozer build configuration
└── README.md            this file
```

---

## Supported Android versions

| Android | API |
|---------|-----|
| 8.0 Oreo | 26 (minimum) |
| 13 Tiramisu | 33 (target) |

Architectures: `arm64-v8a`, `armeabi-v7a`.
