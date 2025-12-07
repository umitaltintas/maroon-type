from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QFrame, QGraphicsDropShadowEffect, QGraphicsBlurEffect,
                             QDialog, QComboBox, QCheckBox, QPushButton, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, QEasingCurve, QPropertyAnimation, QAbstractAnimation
from PyQt6.QtGui import QFont, QCursor, QColor

from .config import Config
from .engine import GameEngine
from .modes import WordMode, QuoteMode, TimeMode, SuddenDeathMode, IGameMode


class ModeButton(QLabel):
    clicked = pyqtSignal(object)

    def __init__(self, text: str, mode_instance):
        super().__init__(text)
        self.mode_instance = mode_instance
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet(self._style(default=True))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._active = False

    def mousePressEvent(self, e):
        self.clicked.emit(self.mode_instance)

    def set_active(self, active: bool):
        self._active = active
        self.setStyleSheet(self._style(active=active))

    def enterEvent(self, event):
        self.setStyleSheet(self._style(active=self._active, hover=True))
        return super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._style(active=self._active))
        return super().leaveEvent(event)

    def _style(self, default=False, active=False, hover=False) -> str:
        c = Config.COLORS
        base = c['text_sub'] if not active else c['active_mode']
        bg = "transparent"
        if hover:
            bg = c['surface_alt']
        return (
            f"color: {base}; padding: 7px 10px; border-radius: 6px;"
            f"letter-spacing: 0.4px; background-color: {bg};"
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maroon Type - Modular Pro")
        self.resize(1100, 750)
        self.engine = GameEngine()
        self.pulse_anim = None
        self.focus_mode = False
        self.theme_names = list(Config.THEMES.keys())
        self.theme_index = self.theme_names.index(Config.ACTIVE_THEME)
        self.running_blur_radius = 5
        self.start_in_focus = False

        self.setup_ui()
        self.connect_signals()

        self.engine.reset_game()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(60, 60, 60, 60)
        self.main_layout.setSpacing(20)
        self.central_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {Config.COLORS['bg']};
            }}
        """)

        self.header_container = QWidget()
        self.header_layout = QVBoxLayout(self.header_container)

        self.lbl_title = QLabel("MAROON TYPE")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet(
            f"color: {Config.COLORS['accent']}; font-size: 32px; font-weight: bold; letter-spacing: 2px;"
        )
        self.header_layout.addWidget(self.lbl_title)

        self.toolbar = QFrame()
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Config.COLORS['surface']}, stop:1 {Config.COLORS['surface_alt']});
                border-radius: 10px;
                border: 1px solid {Config.COLORS['border']};
                padding: 6px;
            }}
        """
        )

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

        self.toolbar_layout.addStretch(1)
        self.btn_settings = QPushButton("⚙ Settings")
        self.btn_settings.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_settings.setStyleSheet(
            f"color: {Config.COLORS['text_main']}; background: transparent; border: none; "
            f"padding: 6px 10px; border-radius: 6px;"
        )
        self.btn_settings.clicked.connect(self.open_settings)
        self.toolbar_layout.addWidget(self.btn_settings)

        self.header_layout.addWidget(self.toolbar)
        self.header_layout.addWidget(QLabel())

        self.lbl_stats = QLabel("Ready")
        self.lbl_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_stats.setStyleSheet(
            f"color: {Config.COLORS['text_main']}; font-size: 18px; font-family: {Config.FONT_FALLBACK};"
        )
        self.header_layout.addWidget(self.lbl_stats)

        self.main_layout.addWidget(self.header_container)

        self.text_frame = QFrame()
        self.text_layout = QVBoxLayout(self.text_frame)
        self.lbl_text = QLabel()
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.lbl_text.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE))
        self.lbl_text.setStyleSheet(
            f"letter-spacing: 0.5px; line-height: 1.55; font-family: {Config.FONT_FALLBACK};"
        )
        self.text_layout.addWidget(self.lbl_text)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.text_frame.setGraphicsEffect(shadow)

        self.update_style(Config.COLORS['border'])
        self.main_layout.addWidget(self.text_frame, stretch=1)

        self.lbl_info = QLabel("TAB to restart | Blur Focus Active")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_info.setStyleSheet(f"color: {Config.COLORS['text_sub']}; letter-spacing: 0.3px;")
        self.main_layout.addWidget(self.lbl_info)

        self.blur = QGraphicsBlurEffect()
        self.blur.setBlurRadius(0)
        self.header_container.setGraphicsEffect(self.blur)
        self.apply_theme()

    def connect_signals(self):
        self.engine.stats_updated.connect(self.update_ui)
        self.engine.game_finished.connect(self.on_game_finish)
        self.engine.game_started.connect(lambda: self.set_blur(0))

    def change_mode(self, mode: IGameMode):
        assert mode is not None
        self.engine.set_mode(mode)
        for btn in self.mode_buttons:
            btn.set_active(btn.mode_instance == mode)
        style_color = mode.style_color if mode else Config.COLORS["border"]
        self.update_style(style_color)
        self._pulse_text_frame()

    def update_ui(self, stats_text, html):
        self.lbl_stats.setText(stats_text)
        self.lbl_text.setText(html)
        if self.engine.is_running:
            self.set_blur(5)

    def on_game_finish(self, success):
        self.set_blur(0)
        color = Config.COLORS['correct'] if success else Config.COLORS['death']
        self.update_style(color)
        self._pulse_text_frame()

    def set_blur(self, radius):
        self.blur.setBlurRadius(radius)

    def update_style(self, border_color):
        self.text_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Config.COLORS['surface']}, stop:1 {Config.COLORS['surface_alt']});
                border-radius: 18px;
                padding: 28px;
                border: 2px solid {border_color};
            }}
        """)
        self.central_widget.setStyleSheet(
            f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {Config.COLORS['bg']}, stop:1 {Config.COLORS['bg_alt']});
        """
        )

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()

        if key == Qt.Key.Key_Tab:
            self.engine.reset_game()
            style_color = self.engine.mode.style_color if self.engine.mode else Config.COLORS['border']
            self.update_style(style_color)
            return
        if key == Qt.Key.Key_F and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.toggle_focus_mode()
            return
        if key == Qt.Key.Key_T and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.toggle_theme()
            return
        if key == Qt.Key.Key_Comma and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.open_settings()
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

    def _pulse_text_frame(self):
        # Small opacity pulse to emphasize state change.
        effect = self.text_frame.graphicsEffect()
        if not effect or not isinstance(effect, QGraphicsDropShadowEffect):
            return
        if self.pulse_anim and self.pulse_anim.state() == QAbstractAnimation.State.Running:
            self.pulse_anim.stop()
        self.pulse_anim = QPropertyAnimation(effect, b"blurRadius", self)
        self.pulse_anim.setDuration(220)
        self.pulse_anim.setStartValue(18)
        self.pulse_anim.setEndValue(34)
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.pulse_anim.setLoopCount(2)
        self.pulse_anim.start()

    def toggle_focus_mode(self):
        self.focus_mode = not self.focus_mode
        visible = not self.focus_mode
        self.header_container.setVisible(visible)
        self.update_info_text()

    def toggle_theme(self):
        self.theme_index = (self.theme_index + 1) % len(self.theme_names)
        next_theme = self.theme_names[self.theme_index]
        Config.set_theme(next_theme)
        self.apply_theme()
        # Re-render text with new colors.
        self.engine._emit_update(final=self.engine.finished)
        self.update_info_text()

    def apply_theme(self, border_color=None):
        c = Config.COLORS
        self.central_widget.setStyleSheet(
            f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {c['bg']}, stop:1 {c['bg_alt']});
        """
        )
        self.toolbar.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {c['surface']}, stop:1 {c['surface_alt']});
                border-radius: 10px;
                border: 1px solid {c['border']};
                padding: 6px;
            }}
        """
        )
        self.lbl_title.setStyleSheet(
            f"color: {c['accent']}; font-size: 32px; font-weight: bold; letter-spacing: 2px;"
        )
        self.lbl_stats.setStyleSheet(
            f"color: {c['text_main']}; font-size: 18px; font-family: {Config.FONT_FALLBACK};"
        )
        self.lbl_info.setStyleSheet(f"color: {c['text_sub']}; letter-spacing: 0.3px;")
        for btn in self.mode_buttons:
            btn.setStyleSheet(btn._style(active=btn._active))
        style_color = border_color
        if not style_color and self.engine.mode:
            style_color = self.engine.mode.style_color
        self.update_style(style_color or Config.COLORS["border"])

    def update_info_text(self):
        theme = Config.ACTIVE_THEME.capitalize()
        if self.focus_mode:
            text = f"Focus Mode ON | Theme: {theme} | Ctrl+F to exit"
        else:
            text = f"TAB restart | Ctrl+F focus | Ctrl+T theme ({theme}) | Ctrl+, settings"
        self.lbl_info.setText(text)

    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        layout = QVBoxLayout(dialog)

        theme_combo = QComboBox(dialog)
        theme_combo.addItems(self.theme_names)
        theme_combo.setCurrentIndex(self.theme_index)
        layout.addWidget(QLabel("Theme"))
        layout.addWidget(theme_combo)

        blur_spin = QSpinBox(dialog)
        blur_spin.setRange(0, 20)
        blur_spin.setValue(self.running_blur_radius)
        layout.addWidget(QLabel("Blur while typing"))
        layout.addWidget(blur_spin)

        focus_check = QCheckBox("Start in focus mode (hide header)", dialog)
        focus_check.setChecked(self.start_in_focus)
        layout.addWidget(focus_check)

        btns = QHBoxLayout()
        btn_save = QPushButton("Save", dialog)
        btn_cancel = QPushButton("Cancel", dialog)
        btns.addWidget(btn_save)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        btn_save.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)

        if dialog.exec():
            self.theme_index = theme_combo.currentIndex()
            Config.set_theme(self.theme_names[self.theme_index])
            self.running_blur_radius = blur_spin.value()
            self.start_in_focus = focus_check.isChecked()
            if self.start_in_focus and not self.focus_mode:
                self.toggle_focus_mode()
            if not self.start_in_focus and self.focus_mode:
                self.toggle_focus_mode()
            self.apply_theme()
            self.engine._emit_update(final=self.engine.finished)
            self.update_info_text()
