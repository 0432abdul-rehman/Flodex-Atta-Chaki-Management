# Installation Guide

## Desktop App (Python)

1. Install Python 3.8+
2. Open terminal in repository root.
3. Install dependencies:
   ```bash
   pip install -r desktop/requirements.txt
   ```
4. Run app:
   ```bash
   python desktop/main.py
   ```

## Android App

1. Install Android Studio (latest stable).
2. Open folder: `android/`
3. Let Gradle sync.
4. Connect Android phone (USB debugging on) or start emulator.
5. Run app from Android Studio.

## Offline Operation

- Both apps use local SQLite databases.
- No internet is required after installation.
