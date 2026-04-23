[app]
title = Kalkulyator
package.name = kalkulyator
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = 1
android.accept_sdk_license = True
android.build_tools_version = 33.0.2

[buildozer]
log_level = 2
warn_on_root = 1
