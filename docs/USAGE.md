# Usage Guide

## Customer Management

1. Go to **Customers** tab (Desktop) or main screen fields (Android).
2. Enter Name, Phone, Address, and optional Photo path.
3. Save customer. Existing phone numbers automatically reuse customer profile.

## Manual Transaction Entry

1. Select/save customer.
2. Enter wheat, flour, amount, and payment status.
3. Save transaction.
4. If customer pays later, use **Mark Selected Paid** (Desktop).

## Voice Commands

Command examples:
- `Flodex, Ali Hassan ka data nikalo`
- `Flodex Ali ko 40 KG add karo`
- `Flodex aaj ka data de`
- `Flodex is hafta ka data de`
- `Flodex is mahina ka data de`
- `Flodex unpaid report de`

Desktop voice tab supports:
- typed commands
- microphone capture (if speech dependencies installed)
- spoken responses (TTS)

## Reports, Loans, and Daily Progress

- Daily/weekly/monthly/all-time summaries shown in reports.
- Loan report lists unpaid customers.
- Due reminders highlight old unpaid balances.
- Custom query box handles natural language queries (period and unpaid/customer questions).

## Export, Receipts, and Print

- Export current month to Excel.
- Generate TXT or PDF receipt for selected transaction.
- Print the last generated receipt from the app.

## Customization

- Apply custom color theme.
- Apply custom background image (`.png/.gif` supported by Tkinter).

## Face Matching (Optional)

- In Customer tab choose **Match Customer by Face Photo**.
- If OpenCV is available and a face is detected, Flodex attempts photo-path matching.
