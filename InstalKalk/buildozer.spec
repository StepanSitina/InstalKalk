[app]
title = Instalkalk
package.name = instalkalk
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = .venv, exports, templates
# Zmìň hlavní soubor pro Android
source.main = main_android.py

version = 1.0

# Požadavky na knihovny pro Kivy a DB
requirements = python3,kivy==2.3.0,kivymd==1.1.1,sqlite3,beautifulsoup4,requests

# Android specifikace (min sdk 26 je Android 8.0)
android.api = 33
android.minapi = 26

# Přítup k internetu pro vyhledávání
android.permissions = INTERNET

# Architektury ARM
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1