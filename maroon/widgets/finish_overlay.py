from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ..config import Config


class FinishOverlay(QFrame):
    lbl_finish_score: QLabel
    lbl_finish_sub: QLabel
    """Final score overlay that appears on top of the text frame."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_finish_score = QLabel("", self)
        self.lbl_finish_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_finish_score.setFont(QFont(Config.FONT_FAMILY, 46, QFont.Weight.Black))

        self.lbl_finish_sub = QLabel("", self)
        self.lbl_finish_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_finish_sub.setWordWrap(True)
        self.lbl_finish_sub.setFont(QFont(Config.FONT_FAMILY, 16, QFont.Weight.DemiBold))

        layout.addWidget(self.lbl_finish_score)
        layout.addWidget(self.lbl_finish_sub)

        self.hide()
        self.apply_theme()

    def apply_theme(self):
        c = Config.COLORS
        self.setStyleSheet(
            f"background-color: rgba(0, 0, 0, 150); border: 2px solid {c['border']}; "
            f"border-radius: 16px; padding: 28px;"
        )
        self.lbl_finish_score.setStyleSheet(f"color: {c['accent']};")
        self.lbl_finish_sub.setStyleSheet(f"color: {c['text_main']}; letter-spacing: 0.3px;")

    def set_result(self, success: bool, wpm: int, acc: int):
        c = Config.COLORS
        accent = c['correct'] if success else c['death']
        status = "Tamamlandı" if success else "Hata!"
        self.lbl_finish_score.setText(f"{wpm} WPM")
        self.lbl_finish_sub.setText(f"{status} • Doğruluk: {acc}%\nTAB ile yeniden başlat.")
        self.lbl_finish_score.setStyleSheet(f"color: {accent};")
        self.show()
        self.raise_()

    def update_geometry(self, rect):
        self.setGeometry(rect)
