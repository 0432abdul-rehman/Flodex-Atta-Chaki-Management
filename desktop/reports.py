import platform
import subprocess
from pathlib import Path
from typing import Iterable, Mapping, Tuple


def export_transactions_excel(rows: Iterable[Mapping], output_path: str) -> str:
    try:
        from openpyxl import Workbook
    except ImportError:
        return export_transactions_csv(rows, output_path.replace(".xlsx", ".csv"))

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Transactions"
    headers = ["Date", "Customer", "Phone", "Wheat KG", "Flour KG", "Amount", "Payment", "Notes"]
    sheet.append(headers)

    for row in rows:
        sheet.append(
            [
                row["txn_date"],
                row["customer_name"],
                row["customer_phone"],
                row["wheat_weight"],
                row["flour_weight"],
                row["amount"],
                row["payment_status"],
                row["notes"],
            ]
        )

    for col in sheet.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        sheet.column_dimensions[col[0].column_letter].width = min(max_len + 2, 35)

    workbook.save(output_path)
    return output_path


def export_transactions_csv(rows: Iterable[Mapping], output_path: str) -> str:
    import csv

    headers = ["Date", "Customer", "Phone", "Wheat KG", "Flour KG", "Amount", "Payment", "Notes"]
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(
                [
                    row["txn_date"],
                    row["customer_name"],
                    row["customer_phone"],
                    row["wheat_weight"],
                    row["flour_weight"],
                    row["amount"],
                    row["payment_status"],
                    row["notes"],
                ]
            )
    return output_path


def generate_receipt_text(customer_name: str, txn_row: Mapping) -> str:
    lines = [
        "Yousaf Atta Chaki - Flodex Receipt",
        "=" * 36,
        f"Customer: {customer_name}",
        f"Date: {txn_row['txn_date']}",
        f"Wheat: {txn_row['wheat_weight']} KG",
        f"Flour: {txn_row['flour_weight']} KG",
        f"Amount: {txn_row['amount']}",
        f"Payment: {txn_row['payment_status']}",
        f"Notes: {txn_row['notes']}",
    ]
    return "\n".join(lines)


def save_receipt(customer_name: str, txn_row: Mapping, output_dir: str = "receipts") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    safe_name = customer_name.replace(" ", "_")
    out_path = Path(output_dir) / f"receipt_{safe_name}_{txn_row['id']}.txt"
    content = generate_receipt_text(customer_name, txn_row)
    out_path.write_text(content, encoding="utf-8")
    return str(out_path)


def save_receipt_pdf(customer_name: str, txn_row: Mapping, output_dir: str = "receipts") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    safe_name = customer_name.replace(" ", "_")
    out_path = Path(output_dir) / f"receipt_{safe_name}_{txn_row['id']}.pdf"

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return save_receipt(customer_name, txn_row, output_dir)

    c = canvas.Canvas(str(out_path), pagesize=A4)
    text = c.beginText(40, 800)
    for line in generate_receipt_text(customer_name, txn_row).split("\n"):
        text.textLine(line)
    c.drawText(text)
    c.save()
    return str(out_path)


def print_receipt_file(path: str) -> Tuple[bool, str]:
    file_path = Path(path)
    if not file_path.exists():
        return False, "Receipt file not found"

    system = platform.system().lower()
    try:
        if system.startswith("win"):
            import os

            os.startfile(str(file_path), "print")
        elif system == "darwin":
            subprocess.run(["lp", str(file_path)], check=True)
        else:
            subprocess.run(["lp", str(file_path)], check=True)
        return True, "Print job sent"
    except Exception as exc:
        return False, f"Print failed: {exc}"
