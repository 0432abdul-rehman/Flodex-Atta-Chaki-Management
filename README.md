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

## Delivered Features

- One-time customer profile storage and customer reuse
- Per-visit transaction records (wheat, flour, amount, payment status)
- Manual entry + voice command flow with wake-word style parsing (`Flodex ...`)
- Daily/weekly/monthly/all-time reports
- Loan/unpaid tracking and due reminders
- Receipt generation (TXT + PDF) and receipt print trigger
- Excel export (CSV fallback)
- Theme color + background image support
- Optional face-photo matching helper (OpenCV)
- 100% local SQLite storage for both platforms

## Quick Start

- Desktop: see `docs/INSTALLATION.md`
- Android: open `android/` in Android Studio and run on emulator/device
