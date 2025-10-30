from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
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
        self.config_coordinator = None  # Will be set by MainWindowV2

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        button_width = 90

        # User Data Path row (replicates MdxScraper style)
        data_row = QHBoxLayout()
        _lbl_data = QLabel("User Data Path:", self)
        _lbl_data.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        _lbl_data.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        data_row.addWidget(_lbl_data)
        data_row.addSpacing(8)

        self.edit_user_data = QLineEdit(self)
        self.edit_user_data.setReadOnly(True)
        self.edit_user_data.setProperty("class", "readonly-input")
        data_row.addWidget(self.edit_user_data, 1)

        self.btn_open_user_data = QPushButton("Open", self)
        self.btn_open_user_data.setFixedWidth(button_width)
        self.btn_open_user_data.setObjectName("open-data-button")
        data_row.addWidget(self.btn_open_user_data)
        layout.addLayout(data_row)

        # --- Debug mode + debug dir input + browse ---
        row_debug = QHBoxLayout()
        row_debug.setSpacing(8)
        self.check_debug = QCheckBox("Enable debug mode and save debug files:", self)
        self.check_debug.setChecked(False)
        row_debug.addWidget(self.check_debug)

        self.edit_debug_dir = QLineEdit(self)
        self.edit_debug_dir.setPlaceholderText("data/debug")
        row_debug.addWidget(self.edit_debug_dir, 1)

        self.btn_debug_dir = QPushButton("Browse...", self)
        self.btn_debug_dir.setFixedWidth(button_width)
        row_debug.addWidget(self.btn_debug_dir)

        layout.addLayout(row_debug)
        self.btn_debug_dir.clicked.connect(self.select_debug_dir)

        layout.addStretch(1)

        # Default hint text: show relative location until user clicks Open
        try:
            self.edit_user_data.setText("data/ (relative to project root)")
        except Exception:
            pass

    def set_config_coordinator(self, coordinator):
        """Set ConfigCoordinator for reading/writing configuration."""
        self.config_coordinator = coordinator

    def set_config(self, debug_enabled: bool = False, debug_dir: str = "data/debug"):
        self.check_debug.setChecked(debug_enabled)
        self.edit_debug_dir.setText(debug_dir)

    def load_config_from_coordinator(self):
        """Load configuration from ConfigCoordinator and update UI."""
        if not self.config_coordinator:
            return
        file_config = self.config_coordinator.get_file_processing_config()
        debug_enabled = file_config.get("debug", {}).get("enabled", False)
        debug_dir = file_config.get("debug", {}).get("debug_dir", "data/debug")
        self.set_config(debug_enabled, debug_dir)

    def save_config_to_coordinator(self):
        """Save current UI state to ConfigCoordinator."""
        if not self.config_coordinator:
            return
        file_config = self.config_coordinator.get_file_processing_config()
        file_config["debug"] = {
            "enabled": self.check_debug.isChecked(),
            "debug_dir": self.edit_debug_dir.text().strip() or "data/debug",
        }
        self.config_coordinator.set_file_processing_config(file_config)

    def select_debug_dir(self):
        """Select debug directory."""
        default_dir = self.edit_debug_dir.text().strip() or "data/debug"
        dir_path = QFileDialog.getExistingDirectory(self, "Select Debug Directory", default_dir)
        if dir_path:
            self.edit_debug_dir.setText(dir_path)
            self.save_config_to_coordinator()
