import unittest

from desktop.voice_handler import VoiceCommandParser


class TestVoiceParser(unittest.TestCase):
    def setUp(self):
        self.parser = VoiceCommandParser()

    def test_find_customer_command(self):
        intent = self.parser.parse("Flodex, Ali Hassan ka data nikalo")
        self.assertEqual(intent.action, "find_customer")
        self.assertIn("Ali", intent.customer_query)

    def test_add_weight_command(self):
        intent = self.parser.parse("Flodex Ali ko 40 KG add karo")
        self.assertEqual(intent.action, "add_transaction")
        self.assertEqual(intent.weight, 40.0)

    def test_daily_summary_command(self):
        intent = self.parser.parse("Flodex aaj ka data de")
        self.assertEqual(intent.action, "summary")
        self.assertEqual(intent.period, "daily")

    def test_wake_word_required(self):
        intent = self.parser.parse("Ali Hassan ko add karo")
        self.assertEqual(intent.action, "wake_word_required")

    def test_unpaid_command(self):
        intent = self.parser.parse("Flodex unpaid report de")
        self.assertEqual(intent.action, "unpaid_report")


if __name__ == "__main__":
    unittest.main()
