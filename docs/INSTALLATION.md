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

### Optional Desktop Notes

- `PyAudio` is needed for microphone capture through `SpeechRecognition`.
- `opencv-python` enables optional face-photo detection/matching helper.
- `reportlab` enables PDF receipts.

## Android App

1. Install Android Studio (latest stable).
2. Open folder: `android/`
3. Let Gradle sync.
4. Connect Android phone (USB debugging on) or start emulator.
5. Run app from Android Studio.

## Offline Operation

- Both apps use local SQLite databases.
- No internet is required for storage and reporting flows.
