from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QFrame, QGraphicsDropShadowEffect, QGraphicsBlurEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QColor

from .config import Config
from .engine import GameEngine
from .modes import WordMode, QuoteMode, TimeMode, SuddenDeathMode


class ModeButton(QLabel):
    clicked = pyqtSignal(object)

    def __init__(self, text: str, mode_instance):
        super().__init__(text)
        self.mode_instance = mode_instance
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet(f"color: {Config.COLORS['text_sub']}; padding: 5px;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, e):
        self.clicked.emit(self.mode_instance)

    def set_active(self, active: bool):
        color = Config.COLORS['active_mode'] if active else Config.COLORS['text_sub']
        decoration = "underline" if active else "none"
        self.setStyleSheet(f"color: {color}; text-decoration: {decoration}; padding: 5px;")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maroon Type - Modular Pro")
        self.resize(1100, 750)
        self.engine = GameEngine()

        self.setup_ui()
        self.connect_signals()

        self.engine.reset_game()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(60, 60, 60, 60)
        self.layout.setSpacing(20)

        self.header_container = QWidget()
        self.header_layout = QVBoxLayout(self.header_container)

        self.lbl_title = QLabel("MAROON TYPE")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet(f"color: {Config.COLORS['accent']}; font-size: 32px; font-weight: bold;")
        self.header_layout.addWidget(self.lbl_title)

        self.toolbar = QFrame()
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar.setStyleSheet(f"background-color: {Config.COLORS['surface']}; border-radius: 8px;")

        self.mode_buttons = []
        modes = [
            ("25 Words", WordMode(25)),
            ("Quotes", QuoteMode()),
            ("30s Time", TimeMode(30)),
            ("15s Sprint", TimeMode(15)),
            ("💀 Death", SuddenDeathMode())
        ]

        for name, mode_obj in modes:
            btn = ModeButton(name, mode_obj)
            btn.clicked.connect(self.change_mode)
            self.toolbar_layout.addWidget(btn)
            self.mode_buttons.append(btn)

        self.header_layout.addWidget(self.toolbar)
        self.header_layout.addWidget(QLabel())

        self.lbl_stats = QLabel("Ready")
        self.lbl_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_stats.setStyleSheet(f"color: {Config.COLORS['text_main']}; font-size: 20px; font-family: Consolas;")
        self.header_layout.addWidget(self.lbl_stats)

        self.layout.addWidget(self.header_container)

        self.text_frame = QFrame()
        self.text_layout = QVBoxLayout(self.text_frame)
        self.lbl_text = QLabel()
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.lbl_text.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE))
        self.text_layout.addWidget(self.lbl_text)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.text_frame.setGraphicsEffect(shadow)

        self.update_style(Config.COLORS['border'])
        self.layout.addWidget(self.text_frame, stretch=1)

        self.lbl_info = QLabel("TAB to restart | Blur Focus Active")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_info.setStyleSheet(f"color: {Config.COLORS['text_sub']};")
        self.layout.addWidget(self.lbl_info)

        self.blur = QGraphicsBlurEffect()
        self.blur.setBlurRadius(0)
        self.header_container.setGraphicsEffect(self.blur)

    def connect_signals(self):
        self.engine.stats_updated.connect(self.update_ui)
        self.engine.game_finished.connect(self.on_game_finish)
        self.engine.game_started.connect(lambda: self.set_blur(0))

    def change_mode(self, mode):
        self.engine.set_mode(mode)
        for btn in self.mode_buttons:
            btn.set_active(btn.mode_instance == mode)
        self.update_style(mode.style_color)

    def update_ui(self, stats_text, html):
        self.lbl_stats.setText(stats_text)
        self.lbl_text.setText(html)
        if self.engine.is_running:
            self.set_blur(5)

    def on_game_finish(self, success):
        self.set_blur(0)
        color = Config.COLORS['correct'] if success else Config.COLORS['death']
        self.update_style(color)

    def set_blur(self, radius):
        self.blur.setBlurRadius(radius)

    def update_style(self, border_color):
        self.text_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Config.COLORS['surface']};
                border-radius: 15px;
                padding: 25px;
                border: 2px solid {border_color};
            }}
        """)
        self.central_widget.setStyleSheet(f"background-color: {Config.COLORS['bg']};")

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()

        if key == Qt.Key.Key_Tab:
            self.engine.reset_game()
            self.update_style(self.engine.mode.style_color)
            return

        if key == Qt.Key.Key_Backspace:
            current = self.engine.user_input
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                space_idx = current.rstrip().rfind(' ')
                new_input = current[:space_idx+1] if space_idx != -1 else ""
            else:
                new_input = current[:-1]
            self.engine.process_input(new_input)

        elif key == Qt.Key.Key_Space:
            current = self.engine.user_input
            target = self.engine.target_text

            if not current.endswith(" "):
                idx = len(current)
                if idx < len(target) and target[idx] != " ":
                    nxt = target.find(" ", idx)
                    nxt = len(target) if nxt == -1 else nxt
                    missing = nxt - idx
                    self.engine.process_input(current + "_" * missing + " ")
                else:
                    self.engine.process_input(current + " ")

        elif text and text.isprintable():
            if len(self.engine.user_input) < len(self.engine.target_text):
                self.engine.process_input(self.engine.user_input + text)
