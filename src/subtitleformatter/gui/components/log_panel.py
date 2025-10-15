from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QTextEdit, QVBoxLayout, QWidget


class LogPanel(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        self.editor = QTextEdit(self)
        self.editor.setReadOnly(True)
        self.editor.setPlaceholderText("Logs will appear here...")

        controls = QHBoxLayout()
        self.btn_clear = QPushButton("Clear log", self)
        self.btn_copy = QPushButton("Copy log", self)
        controls.addWidget(self.btn_clear)
        controls.addWidget(self.btn_copy)
        controls.addStretch(1)

        # editor on top, buttons at bottom
        root.addWidget(self.editor)
        root.addLayout(controls)

        self.btn_clear.clicked.connect(self.editor.clear)
        self.btn_copy.clicked.connect(self._copy)

    def append_log(self, text: str) -> None:
        self.editor.append(text)

    def _copy(self) -> None:
        self.editor.selectAll()
        self.editor.copy()
        self.editor.moveCursor(self.editor.textCursor().End)
