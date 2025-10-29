from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class CommandPanel(QWidget):
    formatRequested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # row for legacy config buttons removed per V2 design

        row2 = QHBoxLayout()
        self.btn_format = QPushButton("Format", self)
        self.btn_format.setStyleSheet("font-size: 16px; padding: 12px 24px; font-weight: 700;")
        self.btn_format.setMinimumWidth(240)
        self.btn_format.setMinimumHeight(40)
        row2.addStretch(1)
        row2.addWidget(self.btn_format)
        row2.addStretch(1)

        row3 = QHBoxLayout()
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        # progress bar should span full width
        self.progress.setMinimumWidth(0)
        self.progress.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row3.addWidget(self.progress)

        # add rows centered
        # legacy row1 removed
        root.addLayout(row2)
        root.addLayout(row3)

        # fix panel height similar to MdxScraper (approx)
        self.setFixedHeight(120)

        self.btn_format.clicked.connect(lambda: self.formatRequested.emit())

    def set_progress(self, value: int) -> None:
        self.progress.setValue(max(0, min(100, value)))
