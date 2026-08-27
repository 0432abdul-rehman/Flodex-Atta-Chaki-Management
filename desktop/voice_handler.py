import re
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class VoiceIntent:
    action: str
    customer_query: Optional[str] = None
    weight: Optional[float] = None
    period: Optional[str] = None


class VoiceCommandParser:
    WAKE_WORD = "flodex"

    def parse(self, text: str) -> VoiceIntent:
        raw = text.strip().lower()
        normalized = raw.replace("٫", ".")

        if self.WAKE_WORD in normalized:
            normalized = normalized.split(self.WAKE_WORD, 1)[1].strip(" ,:")

        if "aaj ka data" in normalized or "today" in normalized:
            return VoiceIntent(action="summary", period="daily")

        if "hafta" in normalized or "week" in normalized:
            return VoiceIntent(action="summary", period="weekly")

        if "mahina" in normalized or "month" in normalized:
            return VoiceIntent(action="summary", period="monthly")

        if "kitni wheat" in normalized:
            return VoiceIntent(action="summary", period="daily")

        if "data nikalo" in normalized or "show" in normalized:
            name = normalized.split("ka data nikalo")[0].strip() if "ka data nikalo" in normalized else normalized
            return VoiceIntent(action="find_customer", customer_query=name.title())

        if "add" in normalized or "kg" in normalized:
            weight = self._extract_weight(normalized)
            customer_name = self._extract_name(normalized)
            return VoiceIntent(action="add_transaction", customer_query=customer_name, weight=weight)

        return VoiceIntent(action="unknown")

    def _extract_weight(self, text: str) -> Optional[float]:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kilo)?", text)
        return float(match.group(1)) if match else None

    def _extract_name(self, text: str) -> Optional[str]:
        match = re.search(r"flodex[, ]*(.*?)\s*(?:ka data nikalo|add|kg)", text)
        if match and match.group(1).strip():
            return match.group(1).strip().title()
        words = text.split()
        if words and words[0] != self.WAKE_WORD:
            return words[0].title()
        return None


class VoiceResponder:
    @staticmethod
    def customer_not_found(name: str) -> str:
        return f"{name} ka record nahin mila. Manual entry se add kar dein."

    @staticmethod
    def customer_found(name: str) -> str:
        return f"{name} ka data mil gaya."

    @staticmethod
    def summary_response(period: str, total_wheat: float, total_amount: float) -> str:
        today = date.today().isoformat()
        return f"{period} summary ({today}): wheat {total_wheat:.2f} KG, amount {total_amount:.2f}"
