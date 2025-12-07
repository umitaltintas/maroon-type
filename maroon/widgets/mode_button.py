from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QFont
from PyQt6.QtWidgets import QLabel

from ..config import Config


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
