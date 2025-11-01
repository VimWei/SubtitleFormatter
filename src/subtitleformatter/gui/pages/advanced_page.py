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

from subtitleformatter.utils import (
    normalize_relative_path,
    to_absolute_path,
    to_relative_path,
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
        self.edit_debug_dir.setPlaceholderText(normalize_relative_path("data/debug"))
        row_debug.addWidget(self.edit_debug_dir, 1)

        self.btn_debug_dir = QPushButton("Browse...", self)
        self.btn_debug_dir.setFixedWidth(button_width)
        row_debug.addWidget(self.btn_debug_dir)

        layout.addLayout(row_debug)
        self.btn_debug_dir.clicked.connect(self.select_debug_dir)
        # Connect editing finished signal to auto-convert to relative path
        # This will trigger when user finishes editing (focus out or Enter)
        self.edit_debug_dir.editingFinished.connect(self._on_debug_dir_edited)

        layout.addStretch(1)

        # Default hint text: show relative location until user clicks Open
        try:
            self.edit_user_data.setText("data/ (relative to project root)")
        except Exception:
            pass

    def set_config_coordinator(self, coordinator):
        """Set ConfigCoordinator for reading/writing configuration."""
        self.config_coordinator = coordinator

    def _on_debug_dir_edited(self):
        """Convert debug directory path to relative path when user finishes editing."""
        debug_dir = self.edit_debug_dir.text().strip()
        if not debug_dir:
            return

        # Convert absolute path to relative if needed (using platform-native separators)
        # Same logic as BasicPage for consistency
        if self.config_coordinator:
            try:
                relative_path = to_relative_path(debug_dir, self.config_coordinator.project_root)
                # Update UI if path changed
                if relative_path != debug_dir:
                    self.edit_debug_dir.blockSignals(True)
                    self.edit_debug_dir.setText(relative_path)
                    self.edit_debug_dir.blockSignals(False)
                    # Auto-save the converted path
                    self.save_config_to_coordinator()
            except Exception:
                # Fallback: at least normalize the path
                normalized = normalize_relative_path(debug_dir)
                if normalized != debug_dir:
                    self.edit_debug_dir.blockSignals(True)
                    self.edit_debug_dir.setText(normalized)
                    self.edit_debug_dir.blockSignals(False)
        else:
            # If no config_coordinator, at least normalize the path
            normalized = normalize_relative_path(debug_dir)
            if normalized != debug_dir:
                self.edit_debug_dir.blockSignals(True)
                self.edit_debug_dir.setText(normalized)
                self.edit_debug_dir.blockSignals(False)

    def set_config(self, debug_enabled: bool = False, debug_dir: str = "data/debug"):
        self.check_debug.setChecked(debug_enabled)
        # Convert to relative path if needed (should already be normalized from load_config_from_coordinator)
        # But ensure it's correct in case set_config is called directly
        if debug_dir and self.config_coordinator:
            try:
                debug_dir = to_relative_path(debug_dir, self.config_coordinator.project_root)
            except Exception:
                debug_dir = normalize_relative_path(debug_dir)
        else:
            debug_dir = normalize_relative_path(debug_dir or "data/debug")
        # Block signals to avoid triggering editingFinished
        self.edit_debug_dir.blockSignals(True)
        self.edit_debug_dir.setText(debug_dir)
        self.edit_debug_dir.blockSignals(False)

    def load_config_from_coordinator(self):
        """Load configuration from ConfigCoordinator and update UI."""
        if not self.config_coordinator:
            return

        # Force reload from file to ensure we get the latest config
        # This is important because _config might be stale if restore_default was called
        self.config_coordinator.unified_manager.load()

        file_config = self.config_coordinator.get_file_processing_config()
        debug_config = file_config.get("debug", {})
        debug_enabled = debug_config.get("enabled", False)
        debug_dir = debug_config.get("debug_dir", "data/debug")

        # Convert to relative path for display (using platform-native separators)
        # If debug_dir is already a relative path (e.g., from TOML), just normalize it
        # If it's absolute, convert it to relative
        if debug_dir:
            try:
                # Check if it's already relative (doesn't start with drive letter or /)
                debug_path = Path(debug_dir)
                if debug_path.is_absolute():
                    # Convert absolute to relative
                    debug_dir = to_relative_path(debug_dir, self.config_coordinator.project_root)
                else:
                    # Already relative, just normalize separators
                    debug_dir = normalize_relative_path(debug_dir)
            except Exception:
                # Fallback: at least normalize the path
                debug_dir = normalize_relative_path(debug_dir)
        else:
            debug_dir = normalize_relative_path("data/debug")

        # Directly set to ensure UI is updated immediately
        # Block signals to avoid triggering editingFinished
        self.edit_debug_dir.blockSignals(True)
        self.check_debug.setChecked(debug_enabled)
        self.edit_debug_dir.setText(debug_dir)
        self.edit_debug_dir.blockSignals(False)

    def save_config_to_coordinator(self):
        """Save current UI state to ConfigCoordinator."""
        if not self.config_coordinator:
            return

        # Get current UI values directly (not from file_config)
        debug_dir = self.edit_debug_dir.text().strip() or "data/debug"
        debug_enabled = self.check_debug.isChecked()

        # Convert absolute path to relative if needed (using platform-native separators)
        if debug_dir:
            try:
                debug_dir = to_relative_path(debug_dir, self.config_coordinator.project_root)
            except Exception:
                debug_dir = normalize_relative_path(debug_dir)
        else:
            debug_dir = normalize_relative_path("data/debug")

        # Build config dict with debug settings
        file_config = {
            "debug": {
                "enabled": debug_enabled,
                "debug_dir": debug_dir,
            }
        }

        # Save to coordinator
        self.config_coordinator.set_file_processing_config(file_config)

        # Update UI to ensure display shows normalized relative path
        # Block signals to avoid triggering editingFinished recursively
        self.edit_debug_dir.blockSignals(True)
        if self.edit_debug_dir.text().strip() != debug_dir:
            self.edit_debug_dir.setText(debug_dir)
        self.edit_debug_dir.blockSignals(False)

    def select_debug_dir(self):
        """Select debug directory."""
        default_dir = self.edit_debug_dir.text().strip() or "data/debug"
        # Convert relative path to absolute for file dialog
        if self.config_coordinator:
            try:
                default_dir_abs = to_absolute_path(
                    default_dir, self.config_coordinator.project_root
                )
                if default_dir_abs.exists() and default_dir_abs.is_dir():
                    default_dir = str(default_dir_abs)
                elif default_dir_abs.parent.exists():
                    default_dir = str(default_dir_abs.parent)
                else:
                    default_dir = str(self.config_coordinator.project_root / "data" / "debug")
            except Exception:
                default_dir = str(self.config_coordinator.project_root / "data" / "debug")

        dir_path = QFileDialog.getExistingDirectory(self, "Select Debug Directory", default_dir)
        if dir_path:
            # Convert to relative path for display (using platform-native separators)
            if self.config_coordinator:
                try:
                    relative_path = to_relative_path(dir_path, self.config_coordinator.project_root)
                except Exception:
                    # Fallback: use normalize if conversion fails
                    relative_path = normalize_relative_path(dir_path)
            else:
                relative_path = dir_path
            self.edit_debug_dir.blockSignals(True)
            self.edit_debug_dir.setText(relative_path)
            self.edit_debug_dir.blockSignals(False)
            self.save_config_to_coordinator()
