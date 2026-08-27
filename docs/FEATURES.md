# Flodex Features Matrix

## Desktop App

- Customer profile save/reuse (name, phone, address, photo path)
- Transaction recording per visit (date, wheat, flour, amount, payment status)
- Payment lifecycle support (`UNPAID` to `PAID` updates)
- Loan calculator/report and due payment reminders
- Voice wake-word command parser (`Flodex`)
- Voice command execution for:
  - customer lookup
  - transaction weight capture
  - daily/weekly/monthly/all summaries
  - unpaid report
  - customer history and natural query fallback
- Microphone command capture + text-to-speech (dependency-based)
- Monthly export to Excel (CSV fallback)
- Receipt generation in TXT and PDF + print trigger
- Manual data entry interface
- Theme customization (color + optional image)
- Optional OpenCV-based face-photo detection and matching helper
- Local SQLite database

## Android App

- Kotlin Android project with Room ORM
- Customer add/reuse by phone
- Transaction insertion with wheat/flour/amount/payment
- Daily/weekly/monthly/all summary actions
- Voice command parser integration on main screen
- Unpaid summary response command
- Offline local database storage
- Permissions groundwork for audio/camera

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
