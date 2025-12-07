import time
from typing import Optional

from PyQt6.QtCore import QTimer, QObject, pyqtSignal

from .config import Config
from .modes import IGameMode, SuddenDeathMode, TimeMode, WordMode
from .services import WordService


class GameEngine(QObject):
    """UI'dan bağımsız oyun mantığı."""
    stats_updated = pyqtSignal(str, str)
    game_finished = pyqtSignal(bool)
    game_started = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.service = WordService()
        self.mode: Optional[IGameMode] = None
        self.target_text = ""
        self.user_input = ""
        self.start_time = None
        self.is_running = False
        self.finished = False
        self.last_wpm = 0
        self.last_acc = 100
        self.last_elapsed = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_tick)
        self.set_mode(WordMode(25))

    def set_mode(self, mode: IGameMode):
        self.mode = mode
        self.reset_game()

    def reset_game(self):
        assert self.mode is not None
        self.target_text = self.mode.generate_target(self.service)
        self.user_input = ""
        self.start_time = None
        self.is_running = False
        self.finished = False
        self.last_wpm = 0
        self.last_acc = 100
        self.last_elapsed = 0.0
        self.timer.stop()
        self._emit_update()
        self.game_started.emit()

    def process_input(self, text_input: str):
        if self.finished:
            return

        if self.is_running and not self.timer.isActive() and isinstance(self.mode, TimeMode):
            self.timer.start(100)

        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            if isinstance(self.mode, TimeMode):
                self.timer.start(100)

        assert self.mode is not None
        if not self.mode.validate_input(text_input, self.target_text):
            self.user_input = text_input
            self._finish_game(success=False)
            return

        self.user_input = text_input
        self._emit_update()

        elapsed = time.time() - self.start_time if self.start_time else 0
        if self.mode.is_finished(self.user_input, self.target_text, elapsed):
            self._finish_game(success=True)

    def _on_tick(self):
        assert self.mode is not None
        elapsed = time.time() - self.start_time if self.start_time else 0
        self._emit_update()
        if self.mode.is_finished(self.user_input, self.target_text, elapsed):
            self._finish_game(success=True)

    def _finish_game(self, success: bool):
        self.is_running = False
        self.finished = True
        self.timer.stop()
        self._emit_update(final=True)
        self.game_finished.emit(success)

    def _emit_update(self, final=False):
        elapsed = time.time() - self.start_time if self.start_time else 0.1
        if elapsed < 0.1:
            elapsed = 0.1

        correct_chars = sum(
            1 for i, c in enumerate(self.user_input)
            if i < len(self.target_text) and c == self.target_text[i]
        )
        wpm = int((correct_chars / 5) / (elapsed / 60))
        acc = int((correct_chars / len(self.user_input) * 100)) if self.user_input else 100
        self.last_wpm = wpm
        self.last_acc = acc
        self.last_elapsed = elapsed

        if self.mode:
            stats_text = self.mode.get_stats_text(wpm, acc, elapsed)
        else:
            stats_text = f"WPM: {wpm} | ACC: {acc}%"
        if final:
            stats_text = f"FINISH | {stats_text}"

        html = self._generate_html()
        self.stats_updated.emit(stats_text, html)

    def _generate_html(self):
        c = Config.COLORS
        html = "<html><head/><body><p style='line-height: 140%;'>"
        inp_len = len(self.user_input)

        for i, char in enumerate(self.target_text):
            if i < inp_len:
                if self.user_input[i] == char:
                    html += f'<span style="color:{c["correct"]};">{char}</span>'
                else:
                    html += (
                        f'<span style="background-color:{c["error"]}; color:#222; '
                        f'border-radius:3px;">{char}</span>'
                    )
            elif i == inp_len:
                display = "&nbsp;" if char == " " else char
                cursor_color = c["death"] if isinstance(self.mode, SuddenDeathMode) else c["cursor"]
                html += (
                    f'<span style="background-color:{cursor_color}; color:{c["bg"]};">{display}</span>'
                )
            else:
                html += f'<span style="color:{c["text_sub"]};">{char}</span>'
        html += "</p></body></html>"
        return html
