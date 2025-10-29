from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class AdvancedPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # User Data Path row (replicates MdxScraper style)
        data_row = QHBoxLayout()
        _lbl_data = QLabel("User Data Path:", self)
        _lbl_data.setProperty("class", "field-label")
        _lbl_data.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        _lbl_data.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        data_row.addWidget(_lbl_data)
        data_row.addSpacing(8)

        self.edit_user_data = QLineEdit(self)
        self.edit_user_data.setReadOnly(True)
        self.edit_user_data.setProperty("class", "readonly-input")
        data_row.addWidget(self.edit_user_data, 1)

        self.btn_open_user_data = QPushButton("Open", self)
        self.btn_open_user_data.setFixedWidth(90)
        self.btn_open_user_data.setObjectName("open-data-button")
        data_row.addWidget(self.btn_open_user_data)
        layout.addLayout(data_row)

        # Top-align the whole page like MdxScraper
        layout.addStretch(1)

        # Default hint text: show relative location until user clicks Open
        try:
            self.edit_user_data.setText("data/ (relative to project root)")
        except Exception:
            pass
