from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QCheckBox,
    QSpinBox,
    QComboBox,
    QLabel,
)

# Model size mapping constants
MODEL_SIZE_TO_DISPLAY = {"sm": "small", "md": "medium", "lg": "large"}
DISPLAY_TO_MODEL_SIZE = {"small": "sm", "medium": "md", "large": "lg"}


class BasicPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

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

        # Row 2: Language, Model size, and Max width
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(32)  # Add spacing between control groups
        
        # Language setting
        language_layout = QHBoxLayout()
        language_layout.setSpacing(8)  # Spacing between label and combo
        language_layout.addWidget(QLabel("Language:"))
        self.combo_language = QComboBox(self)
        self.combo_language.addItems(["auto", "en", "zh"])
        self.combo_language.setCurrentText("en")
        language_layout.addWidget(self.combo_language)
        row2_layout.addLayout(language_layout)
        
        # Model size setting
        model_layout = QHBoxLayout()
        model_layout.setSpacing(8)  # Spacing between label and combo
        model_layout.addWidget(QLabel("Model size:"))
        self.combo_model_size = QComboBox(self)
        # Add human-readable options with internal values
        self.combo_model_size.addItem("small", "sm")
        self.combo_model_size.addItem("medium", "md")
        self.combo_model_size.addItem("large", "lg")
        self.combo_model_size.setCurrentText("medium")  # Default to medium
        model_layout.addWidget(self.combo_model_size)
        row2_layout.addLayout(model_layout)
        
        # Max width setting
        max_width_layout = QHBoxLayout()
        max_width_layout.setSpacing(8)  # Spacing between label, spinbox, and unit
        max_width_layout.addWidget(QLabel("Max width:"))
        self.spin_max_width = QSpinBox(self)
        self.spin_max_width.setRange(20, 200)
        self.spin_max_width.setValue(78)
        max_width_layout.addWidget(self.spin_max_width)
        max_width_layout.addWidget(QLabel("characters"))
        row2_layout.addLayout(max_width_layout)
        
        row2_layout.addStretch()  # Push controls to the left
        layout.addRow("", row2_layout)

    def set_config(self, input_file: str, output_file: str, max_width: int = 78, 
                   language: str = "en", model_size: str = "md", 
                   add_timestamp: bool = True, debug_enabled: bool = False) -> None:
        self.edit_input.setText(input_file)
        self.edit_output.setText(output_file)
        self.spin_max_width.setValue(max_width)
        self.combo_language.setCurrentText(language)
        
        # Map internal model_size values to display text
        display_text = MODEL_SIZE_TO_DISPLAY.get(model_size, "medium")
        self.combo_model_size.setCurrentText(display_text)
        
        self.check_timestamp.setChecked(add_timestamp)
        self.check_debug.setChecked(debug_enabled)


