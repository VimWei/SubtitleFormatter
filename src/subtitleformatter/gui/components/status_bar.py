from __future__ import annotations

from PySide6.QtWidgets import QLabel, QStatusBar


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_label = QLabel("Ready", self)
        self.addPermanentWidget(self.status_label)

    def set_message(self, text: str) -> None:
        self.status_label.setText(text)
