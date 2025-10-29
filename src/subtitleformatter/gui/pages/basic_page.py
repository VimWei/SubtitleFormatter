from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class BasicPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.config_coordinator = None  # Will be set by MainWindowV2

        layout = QFormLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

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

        # Row 1: Checkboxes (Add timestamp and Debug mode)
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(24)  # Add spacing between checkboxes
        self.check_timestamp = QCheckBox("Add timestamp to filename", self)
        self.check_timestamp.setChecked(True)
        self.check_debug = QCheckBox("Enable debug mode", self)
        self.check_debug.setChecked(False)
        row1_layout.addWidget(self.check_timestamp)
        row1_layout.addWidget(self.check_debug)
        row1_layout.addStretch()  # Push checkboxes to the left
        layout.addRow("", row1_layout)

    def set_config_coordinator(self, coordinator):
        """Set ConfigCoordinator for reading/writing configuration."""
        self.config_coordinator = coordinator

    def set_config(
        self,
        input_file: str,
        output_file: str,
        add_timestamp: bool = True,
        debug_enabled: bool = False,
    ) -> None:
        self.edit_input.setText(input_file)
        self.edit_output.setText(output_file)
        self.check_timestamp.setChecked(add_timestamp)
        self.check_debug.setChecked(debug_enabled)

    def load_config_from_coordinator(self):
        """Load configuration from ConfigCoordinator and update UI."""
        if not self.config_coordinator:
            return

        file_config = self.config_coordinator.get_file_processing_config()
        input_file = file_config.get("input_file", "")
        output_file = file_config.get("output_file", "")
        add_timestamp = file_config.get("add_timestamp", True)
        debug_enabled = file_config.get("debug", {}).get("enabled", False)

        self.set_config(input_file, output_file, add_timestamp, debug_enabled)

    def save_config_to_coordinator(self):
        """Save current UI state to ConfigCoordinator."""
        if not self.config_coordinator:
            return

        file_config = {
            "input_file": self.edit_input.text().strip(),
            "output_file": self.edit_output.text().strip(),
            "add_timestamp": self.check_timestamp.isChecked(),
            "debug": {"enabled": self.check_debug.isChecked()},
        }

        self.config_coordinator.set_file_processing_config(file_config)
