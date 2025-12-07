from abc import ABC, abstractmethod

from .config import Config
from .services import WordService


class IGameMode(ABC):
    """Tüm oyun modları bu arayüzü uygulamalıdır."""

    @abstractmethod
    def generate_target(self, service: WordService) -> str:
        pass

    @abstractmethod
    def is_finished(self, input_text: str, target_text: str, time_elapsed: float) -> bool:
        pass

    @abstractmethod
    def get_stats_text(self, wpm: int, acc: int, time_left: int) -> str:
        pass

    @abstractmethod
    def validate_input(self, input_text: str, target_text: str) -> bool:
        """Karakter girildiğinde özel bir kural (örn: Sudden Death) var mı?"""
        return True

    @property
    def style_color(self) -> str:
        return Config.COLORS['border']


class WordMode(IGameMode):
    def __init__(self, count: int = 25):
        self.count = count

    def generate_target(self, service: WordService) -> str:
        return " ".join(service.get_words(self.count))

    def is_finished(self, inp: str, tgt: str, _: float) -> bool:
        return len(inp) >= len(tgt)

    def get_stats_text(self, wpm: int, acc: int, _: int) -> str:
        return f"WPM: {wpm} | ACC: {acc}%"

    def validate_input(self, inp: str, tgt: str) -> bool:
        return True


class TimeMode(IGameMode):
    def __init__(self, seconds: int = 30):
        self.seconds = seconds

    def generate_target(self, service: WordService) -> str:
        return " ".join(service.get_words(100))

    def is_finished(self, _: str, __: str, t: float) -> bool:
        return t >= self.seconds

    def get_stats_text(self, wpm: int, _: int, t: int) -> str:
        return f"Time: {int(self.seconds - t)}s | WPM: {wpm}"

    def validate_input(self, inp: str, tgt: str) -> bool:
        return True


class QuoteMode(IGameMode):
    def generate_target(self, service: WordService) -> str:
        return service.get_quote()

    def is_finished(self, inp: str, tgt: str, _: float) -> bool:
        return len(inp) >= len(tgt)

    def get_stats_text(self, _: int, __: int, ___: int) -> str:
        return "Quote Mode"

    def validate_input(self, inp: str, tgt: str) -> bool:
        return True


class SuddenDeathMode(IGameMode):
    def generate_target(self, service: WordService) -> str:
        return " ".join(service.get_words(30))

    def is_finished(self, inp: str, tgt: str, _: float) -> bool:
        return len(inp) >= len(tgt)

    def get_stats_text(self, wpm: int, _: int, __: int) -> str:
        return f"💀 WPM: {wpm}"

    @property
    def style_color(self) -> str:
        return Config.COLORS['death']

    def validate_input(self, input_text: str, target_text: str) -> bool:
        if not input_text:
            return True
        idx = len(input_text) - 1
        if idx < len(target_text) and input_text[idx] != target_text[idx]:
            return False
        return True
