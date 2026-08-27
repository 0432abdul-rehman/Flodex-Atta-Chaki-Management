# Flodex Features Matrix

## Implemented in Desktop App

- Customer profile CRUD basics with one-time save/reuse by phone
- Transaction recording per visit (date, wheat, flour, amount, payment status)
- Paid/Unpaid tracking and loan report
- Voice command parser for Urdu/Punjabi-style commands and natural inputs
- Daily/weekly/monthly analytics summaries
- Excel export (fallback CSV if openpyxl unavailable)
- Receipt file generation
- Manual data entry UI
- Theme customization (background color)
- Local SQLite database

## Implemented in Android App (MVP Scaffold)

- Kotlin Android project with Room ORM
- Customer add/reuse by phone
- Transaction insertion and daily summary
- Voice command parser integration in main screen
- Offline local database storage
- Required permissions for audio/camera groundwork

## Database Schema

### customers
- `id` (PK)
- `name`
- `phone` (unique)
- `address`
- `photo_path`
- `created_at`

### transactions
- `id` (PK)
- `customer_id` (FK → customers.id)
- `txn_date`
- `wheat_weight`
- `flour_weight`
- `amount`
- `payment_status` (`PAID`/`UNPAID`)
- `notes`
