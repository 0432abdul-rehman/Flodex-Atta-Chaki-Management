import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Customer:
    id: int
    name: str
    phone: str
    address: str
    photo_path: Optional[str]
    created_at: str


@dataclass
class Transaction:
    id: int
    customer_id: int
    txn_date: str
    wheat_weight: float
    flour_weight: float
    amount: float
    payment_status: str
    notes: str


class FlodexDatabase:
    def __init__(self, db_path: str = "flodex.db") -> None:
        self.db_path = str(Path(db_path))
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    address TEXT,
                    photo_path TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    txn_date TEXT NOT NULL,
                    wheat_weight REAL NOT NULL,
                    flour_weight REAL NOT NULL,
                    amount REAL NOT NULL,
                    payment_status TEXT NOT NULL CHECK(payment_status IN ('PAID', 'UNPAID')),
                    notes TEXT DEFAULT '',
                    FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(txn_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id)")

    def add_or_get_customer(self, name: str, phone: str, address: str = "", photo_path: Optional[str] = None) -> Customer:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM customers WHERE phone = ?", (phone,)).fetchone()
            if row:
                return Customer(**row)
            cursor = conn.execute(
                "INSERT INTO customers(name, phone, address, photo_path, created_at) VALUES(?,?,?,?,?)",
                (name.strip(), phone.strip(), address.strip(), photo_path, now),
            )
            customer_id = cursor.lastrowid
            created = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
            return Customer(**created)

    def update_customer(self, customer_id: int, name: str, phone: str, address: str, photo_path: Optional[str]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE customers SET name = ?, phone = ?, address = ?, photo_path = ?
                WHERE id = ?
                """,
                (name.strip(), phone.strip(), address.strip(), photo_path, customer_id),
            )

    def find_customer(self, query: str) -> Optional[Customer]:
        pattern = f"%{query.strip()}%"
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY id LIMIT 1",
                (pattern, pattern),
            ).fetchone()
        return Customer(**row) if row else None

    def list_customers(self) -> List[Customer]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM customers ORDER BY name COLLATE NOCASE").fetchall()
        return [Customer(**row) for row in rows]

    def add_transaction(
        self,
        customer_id: int,
        wheat_weight: float,
        flour_weight: float,
        amount: float,
        payment_status: str,
        txn_date: Optional[str] = None,
        notes: str = "",
    ) -> Transaction:
        date_value = txn_date or date.today().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO transactions(customer_id, txn_date, wheat_weight, flour_weight, amount, payment_status, notes)
                VALUES(?,?,?,?,?,?,?)
                """,
                (customer_id, date_value, wheat_weight, flour_weight, amount, payment_status, notes.strip()),
            )
            row = conn.execute("SELECT * FROM transactions WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return Transaction(**row)

    def list_customer_transactions(self, customer_id: int) -> List[Transaction]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM transactions WHERE customer_id = ? ORDER BY txn_date DESC, id DESC",
                (customer_id,),
            ).fetchall()
        return [Transaction(**row) for row in rows]

    def list_transactions_by_range(self, start_date: str, end_date: str) -> List[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute(
                """
                SELECT t.*, c.name as customer_name, c.phone as customer_phone
                FROM transactions t
                JOIN customers c ON c.id = t.customer_id
                WHERE t.txn_date BETWEEN ? AND ?
                ORDER BY t.txn_date DESC, t.id DESC
                """,
                (start_date, end_date),
            ).fetchall()

    def _aggregate(self, start_date: str, end_date: str) -> Dict[str, float]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    COALESCE(SUM(wheat_weight), 0) AS total_wheat,
                    COALESCE(SUM(flour_weight), 0) AS total_flour,
                    COALESCE(SUM(amount), 0) AS total_amount,
                    COALESCE(SUM(CASE WHEN payment_status='UNPAID' THEN amount ELSE 0 END), 0) AS unpaid_amount,
                    COUNT(*) as total_transactions
                FROM transactions
                WHERE txn_date BETWEEN ? AND ?
                """,
                (start_date, end_date),
            ).fetchone()
        return dict(row)

    def daily_summary(self, day: Optional[str] = None) -> Dict[str, float]:
        day = day or date.today().isoformat()
        summary = self._aggregate(day, day)
        summary["label"] = f"Summary for {day}"
        return summary

    def weekly_summary(self, reference_day: Optional[date] = None) -> Dict[str, float]:
        reference = reference_day or date.today()
        start = reference - timedelta(days=reference.weekday())
        summary = self._aggregate(start.isoformat(), reference.isoformat())
        summary["label"] = f"Summary ({start.isoformat()} to {reference.isoformat()})"
        return summary

    def monthly_summary(self, year: int, month: int) -> Dict[str, float]:
        start = date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        end = next_month - timedelta(days=1)
        summary = self._aggregate(start.isoformat(), end.isoformat())
        summary["label"] = f"Monthly Summary ({start.strftime('%B %Y')})"
        return summary

    def loan_report(self) -> List[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute(
                """
                SELECT c.id, c.name, c.phone,
                       COALESCE(SUM(CASE WHEN t.payment_status = 'UNPAID' THEN t.amount ELSE 0 END), 0) as unpaid_total,
                       COUNT(CASE WHEN t.payment_status = 'UNPAID' THEN 1 END) as unpaid_transactions
                FROM customers c
                LEFT JOIN transactions t ON c.id = t.customer_id
                GROUP BY c.id, c.name, c.phone
                HAVING unpaid_total > 0
                ORDER BY unpaid_total DESC
                """
            ).fetchall()
