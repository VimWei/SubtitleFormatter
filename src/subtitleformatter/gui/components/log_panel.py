from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class LogPanel(QWidget):
    levelChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(8)

        self.editor = QTextEdit(self)
        self.editor.setReadOnly(True)
        self.editor.setPlaceholderText("Logs will appear here...")

        controls = QHBoxLayout()
        self.btn_clear = QPushButton("Clear log", self)
        self.btn_copy = QPushButton("Copy log", self)
        controls.addWidget(self.btn_clear)
        controls.addWidget(self.btn_copy)

        # Logging level selector
        self.label_level = QLabel("Logging Level", self)
        self.combo_level = QComboBox(self)
        self.combo_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.combo_level.setCurrentText("INFO")
        controls.addSpacing(12)
        controls.addWidget(self.label_level)
        controls.addWidget(self.combo_level)
        controls.addStretch(1)

        # editor on top, buttons at bottom
        root.addWidget(self.editor)
        root.addLayout(controls)

        self.btn_clear.clicked.connect(self.editor.clear)
        self.btn_copy.clicked.connect(self._copy)
        self.combo_level.currentTextChanged.connect(self.levelChanged.emit)

    def append_log(self, text: str) -> None:
        self.editor.append(text)

    def _copy(self) -> None:
        self.editor.selectAll()
        self.editor.copy()
        self.editor.moveCursor(self.editor.textCursor().MoveOperation.End)

    def set_logging_level(self, level: str) -> None:
        level = (level or "").upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
            level = "INFO"
        if self.combo_level.currentText() != level:
            self.combo_level.setCurrentText(level)

    def get_logging_level(self) -> str:
        return self.combo_level.currentText()
