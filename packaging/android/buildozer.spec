[app]
# Application metadata
title = CIEL Orbital Control
package.name = ciel_orbital_control
package.domain = org.ciel

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,yaml

# Version
version = 0.1.0

# Requirements: Kivy plus CIEL agent core (no heavy ML on Android by default)
requirements = python3,kivy==2.3.0,pyyaml,requests

# Android orientation
orientation = portrait

# Android permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API
android.minapi = 26
android.api = 33
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# Icons and presplash (replace with actual assets before release)
# android.icon.filename = %(source.dir)s/assets/icon.png
# android.presplash.filename = %(source.dir)s/assets/presplash.png

# Buildozer options
log_level = 2
warn_on_root = 1

[buildozer]
# Buildozer version requirement
# buildozer >= 1.5.0
