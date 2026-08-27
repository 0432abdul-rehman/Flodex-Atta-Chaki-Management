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
    raw_query: Optional[str] = None


class VoiceCommandParser:
    WAKE_WORD = "flodex"

    def parse(self, text: str) -> VoiceIntent:
        raw = text.strip().lower().replace("٫", ".")
        activated = self.WAKE_WORD in raw
        normalized = raw
        if activated:
            normalized = raw.split(self.WAKE_WORD, 1)[1].strip(" ,:")

        if not activated and not self._looks_like_known_command(normalized):
            return VoiceIntent(action="wake_word_required")

        if any(k in normalized for k in ["aaj ka data", "today", "aaj ka summary", "kitni wheat aayi aaj"]):
            return VoiceIntent(action="summary", period="daily")

        if any(k in normalized for k in ["hafta", "week", "is hafta"]):
            return VoiceIntent(action="summary", period="weekly")

        if any(k in normalized for k in ["mahina", "month", "is mahina"]):
            return VoiceIntent(action="summary", period="monthly")

        if any(k in normalized for k in ["total", "all data", "poora data", "whole data"]):
            return VoiceIntent(action="summary", period="all")

        if any(k in normalized for k in ["unpaid", "qarz", "loan", "udhaar"]):
            return VoiceIntent(action="unpaid_report")

        if "data nikalo" in normalized or "show" in normalized:
            name = normalized.split("ka data nikalo")[0].strip() if "ka data nikalo" in normalized else normalized
            return VoiceIntent(action="find_customer", customer_query=name.title())

        if "history" in normalized or "record" in normalized:
            return VoiceIntent(action="customer_history", customer_query=self._extract_name(normalized))

        if any(k in normalized for k in ["add", "kg", "kilo", "wazan"]):
            weight = self._extract_weight(normalized)
            customer_name = self._extract_name(normalized)
            return VoiceIntent(action="add_transaction", customer_query=customer_name, weight=weight)

        return VoiceIntent(action="custom_query", raw_query=normalized)

    def _extract_weight(self, text: str) -> Optional[float]:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kilo)?", text)
        return float(match.group(1)) if match else None

    def _extract_name(self, text: str) -> Optional[str]:
        match = re.search(r"flodex[, ]*(.*?)\s*(?:ka data nikalo|add|kg|kilo|history|record)", text)
        if match and match.group(1).strip():
            return match.group(1).strip().title()

        cleaned = re.sub(r"\b(add|kg|kilo|show|data|nikalo|history|record|ka|ko|de)\b", "", text).strip()
        if cleaned:
            return " ".join(cleaned.split()[:2]).title()
        return None

    def _looks_like_known_command(self, text: str) -> bool:
        known = ["data", "summary", "aaj", "hafta", "mahina", "kg", "loan", "unpaid", "history"]
        return any(token in text for token in known)


class VoiceEngine:
    def __init__(self, language: str = "ur-PK") -> None:
        self.language = language
        self._recognizer = None
        self._mic = None
        self._tts = None

        try:
            import speech_recognition as sr

            self._recognizer = sr.Recognizer()
            self._mic = sr.Microphone()
        except Exception:
            self._recognizer = None
            self._mic = None

        try:
            import pyttsx3

            self._tts = pyttsx3.init()
            for voice in self._tts.getProperty("voices"):
                voice_name = (getattr(voice, "name", "") or "").lower()
                if "urdu" in voice_name or "hindi" in voice_name:
                    self._tts.setProperty("voice", voice.id)
                    break
        except Exception:
            self._tts = None

    @property
    def supported(self) -> bool:
        return self._recognizer is not None and self._mic is not None

    def listen_once(self, timeout: int = 5, phrase_time_limit: int = 8) -> Optional[str]:
        if not self.supported:
            return None

        try:
            import speech_recognition as sr

            with self._mic as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self._recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            try:
                return self._recognizer.recognize_google(audio, language=self.language)
            except sr.UnknownValueError:
                return None
        except Exception:
            return None

    def speak(self, text: str) -> None:
        if not self._tts:
            return
        try:
            self._tts.say(text)
            self._tts.runAndWait()
        except Exception:
            return


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

    @staticmethod
    def wake_word_required() -> str:
        return "Please start command with wake word 'Flodex'."
