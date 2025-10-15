from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QProgressBar,
)


class CommandPanel(QWidget):
    restoreRequested = Signal()
    importRequested = Signal()
    exportRequested = Signal()
    formatRequested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        row1 = QHBoxLayout()
        self.btn_restore = QPushButton("Restore last config", self)
        self.btn_import = QPushButton("Import config", self)
        self.btn_export = QPushButton("Export config", self)
        # center
        row1.addStretch(1)
        row1.addWidget(self.btn_restore)
        row1.addWidget(self.btn_import)
        row1.addWidget(self.btn_export)
        row1.addStretch(1)

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
        root.addLayout(row1)
        root.addLayout(row2)
        root.addLayout(row3)

        # fix panel height similar to MdxScraper (approx)
        self.setFixedHeight(120)

        self.btn_restore.clicked.connect(lambda: self.restoreRequested.emit())
        self.btn_import.clicked.connect(lambda: self.importRequested.emit())
        self.btn_export.clicked.connect(lambda: self.exportRequested.emit())
        self.btn_format.clicked.connect(lambda: self.formatRequested.emit())

    def set_progress(self, value: int) -> None:
        self.progress.setValue(max(0, min(100, value)))


