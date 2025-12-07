from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class SettingsDialog(QDialog):
    def __init__(self, parent, theme_names, theme_index, blur_radius, start_in_focus):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QVBoxLayout(self)

        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(theme_names)
        self.theme_combo.setCurrentIndex(theme_index)
        layout.addWidget(QLabel("Theme", self))
        layout.addWidget(self.theme_combo)

        self.blur_spin = QSpinBox(self)
        self.blur_spin.setRange(0, 20)
        self.blur_spin.setValue(blur_radius)
        layout.addWidget(QLabel("Blur while typing", self))
        layout.addWidget(self.blur_spin)

        self.focus_check = QCheckBox("Start in focus mode (hide header)", self)
        self.focus_check.setChecked(start_in_focus)
        layout.addWidget(self.focus_check)

        btns = QHBoxLayout()
        btn_save = QPushButton("Save", self)
        btn_cancel = QPushButton("Cancel", self)
        btns.addWidget(btn_save)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

    def values(self):
        return (
            self.theme_combo.currentIndex(),
            self.blur_spin.value(),
            self.focus_check.isChecked(),
        )
