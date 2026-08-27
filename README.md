# Flodex Atta Chaki Management

Flodex is an offline-first voice-enabled flour mill (Atta Chaki) management system for:
- **Android** (`android/`)
- **Desktop (Windows/Mac/Linux)** (`desktop/`)

It manages repeat customers, wheat/flour transactions, paid/unpaid tracking, analytics, loan totals, receipts, and exports.

## Repository Structure

```
Flodex-Atta-Chaki-Management/
├── android/                         # Android (Kotlin + Room)
├── desktop/                         # Desktop (Python + Tkinter + SQLite)
├── docs/
│   ├── INSTALLATION.md
│   ├── USAGE.md
│   └── FEATURES.md
└── README.md
```

## Quick Start

- Desktop: see `docs/INSTALLATION.md`
- Android: open `android/` in Android Studio and run on emulator/device

## Core Business Support

- One-time customer profile storage (name/phone/address/photo path)
- Repeat visit transaction logging (wheat, flour, date, payment status)
- Voice command parsing for Urdu/Punjabi-style commands
- Daily/weekly/monthly summaries
- Unpaid loan tracking and report views
- Excel export + receipt generation
- Theme customization with background color
- 100% local SQLite storage (no internet required)
