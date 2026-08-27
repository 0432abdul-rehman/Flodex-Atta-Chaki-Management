import os
import tempfile
import unittest

from desktop.database import FlodexDatabase


class TestFlodexDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_flodex.db")
        self.db = FlodexDatabase(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_reuse_customer_and_transaction(self):
        customer = self.db.add_or_get_customer("Ali Hassan", "03001234567", "Lahore")
        reused = self.db.add_or_get_customer("Ali Hassan", "03001234567", "Lahore")
        self.assertEqual(customer.id, reused.id)

        txn = self.db.add_transaction(customer.id, 40.0, 35.0, 500.0, "UNPAID")
        self.assertEqual(txn.wheat_weight, 40.0)

        summary = self.db.daily_summary(txn.txn_date)
        self.assertEqual(summary["total_transactions"], 1)
        self.assertEqual(summary["unpaid_amount"], 500.0)

    def test_loan_report(self):
        c1 = self.db.add_or_get_customer("A", "1", "")
        c2 = self.db.add_or_get_customer("B", "2", "")
        self.db.add_transaction(c1.id, 10, 8, 100, "UNPAID")
        self.db.add_transaction(c2.id, 10, 8, 100, "PAID")

        loans = self.db.loan_report()
        self.assertEqual(len(loans), 1)
        self.assertEqual(loans[0]["name"], "A")


if __name__ == "__main__":
    unittest.main()
