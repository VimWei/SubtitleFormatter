from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QCheckBox,
)


class BasicPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QFormLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Input selector
        self.edit_input = QLineEdit(self)
        self.btn_input = QPushButton("Browse...", self)
        row_input = QHBoxLayout()
        row_input.addWidget(self.edit_input)
        row_input.addWidget(self.btn_input)
        layout.addRow("Input file:", row_input)

        # Output selector
        self.edit_output = QLineEdit(self)
        self.btn_output = QPushButton("Browse...", self)
        row_output = QHBoxLayout()
        row_output.addWidget(self.edit_output)
        row_output.addWidget(self.btn_output)
        layout.addRow("Output file:", row_output)

        # Add timestamp option (mirrors MdxScraper placement)
        self.check_timestamp = QCheckBox("Add timestamp to filename", self)
        self.check_timestamp.setChecked(True)
        layout.addRow("", self.check_timestamp)

    def set_config(self, input_file: str, output_file: str) -> None:
        self.edit_input.setText(input_file)
        self.edit_output.setText(output_file)


