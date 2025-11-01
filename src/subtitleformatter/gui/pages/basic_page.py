from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from subtitleformatter.utils import (
    normalize_relative_path,
    to_absolute_path,
    to_relative_path,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class BasicPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.config_coordinator = None  # Will be set by MainWindowV2

        layout = QFormLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)  # Reduced top/bottom margins for better compression
        layout.setSpacing(4)  # Minimal spacing between rows, will be compressed first when window shrinks
        layout.setVerticalSpacing(4)  # Specifically control vertical spacing between rows

        # Input: label + mode combo + input controls + buttons (all in one row)
        self.combo_input_mode = QComboBox(self)
        self.combo_input_mode.addItems(["File", "Files", "Directory"])
        
        # Create stacked widget for input controls
        self.input_stack = QStackedWidget(self)
        
        # Page 0: single file - [file input] + [Browse]
        self.edit_input = QLineEdit(self)
        self.btn_input = QPushButton("Browse...", self)
        row_input = QHBoxLayout()
        row_input.addWidget(self.edit_input)
        row_input.addWidget(self.btn_input)
        page_input_file = QWidget(self)
        page_input_file.setLayout(row_input)
        self.input_stack.addWidget(page_input_file)

        # Page 1: multiple files - [file list] + [buttons vertically]
        self.list_inputs = QListWidget(self)
        self.list_inputs.setMinimumHeight(40)  # Minimum height for at least 2 rows
        # Set size policy to prevent excessive compression, prefer keeping height
        self.list_inputs.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Preferred
        )
        self.btn_add_inputs = QPushButton("Add files...", self)
        self.btn_remove_inputs = QPushButton("Remove selected", self)
        
        # Buttons in vertical layout
        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(4)  # Small spacing between buttons
        buttons_layout.addWidget(self.btn_add_inputs)
        buttons_layout.addWidget(self.btn_remove_inputs)
        buttons_widget = QWidget(self)
        buttons_widget.setLayout(buttons_layout)
        
        row_inputs_multi = QHBoxLayout()
        row_inputs_multi.addWidget(self.list_inputs, 1)  # Stretch factor for list
        row_inputs_multi.addWidget(buttons_widget)
        page_inputs_multi = QWidget(self)
        page_inputs_multi.setLayout(row_inputs_multi)
        self.input_stack.addWidget(page_inputs_multi)

        # Page 2: directory + glob - [directory input] + [Browse] + [glob input]
        self.edit_input_dir = QLineEdit(self)
        self.btn_input_dir = QPushButton("Browse...", self)
        self.edit_input_glob = QLineEdit(self)
        self.edit_input_glob.setText("*.*")
        self.edit_input_glob.setMaximumWidth(120)  # Limit glob input width
        row_input_dir = QHBoxLayout()
        row_input_dir.addWidget(self.edit_input_dir)
        row_input_dir.addWidget(self.btn_input_dir)
        row_input_dir.addWidget(QLabel("Glob:", self))
        row_input_dir.addWidget(self.edit_input_glob)
        page_input_dir = QWidget(self)
        page_input_dir.setLayout(row_input_dir)
        self.input_stack.addWidget(page_input_dir)

        # Input row: Label + Mode combo + Stacked widget
        # Create label with fixed width for alignment
        input_label = QLabel("Input:", self)
        input_label.setMinimumWidth(60)  # Fixed width to align with Output: label
        input_label.setMaximumWidth(60)
        input_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Right-align text to align colons
        row_input_container = QHBoxLayout()
        row_input_container.setContentsMargins(0, 0, 0, 0)  # Remove default margins
        row_input_container.setSpacing(8)  # Small spacing between elements in the row
        row_input_container.addWidget(input_label)
        row_input_container.addWidget(self.combo_input_mode)
        row_input_container.addWidget(self.input_stack, 1)  # Stretch factor for stacked widget
        input_widget = QWidget(self)
        input_widget.setLayout(row_input_container)
        # Set size policy to prevent row from being compressed, spacing should compress first
        input_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addRow(input_widget)

        # Output: label + mode combo + output controls + buttons (all in one row)
        self.combo_output_mode = QComboBox(self)
        self.combo_output_mode.addItems(["File", "Directory"])
        
        # Create stacked widget for output controls
        self.output_stack = QStackedWidget(self)

        # Page 0: output file - [file input] + [Browse]
        self.edit_output = QLineEdit(self)
        self.btn_output = QPushButton("Browse...", self)
        row_output = QHBoxLayout()
        row_output.addWidget(self.edit_output)
        row_output.addWidget(self.btn_output)
        page_output_file = QWidget(self)
        page_output_file.setLayout(row_output)
        self.output_stack.addWidget(page_output_file)

        # Page 1: output directory - [directory input] + [Browse]
        self.edit_output_dir = QLineEdit(self)
        self.btn_output_dir = QPushButton("Browse...", self)
        row_output_dir = QHBoxLayout()
        row_output_dir.addWidget(self.edit_output_dir)
        row_output_dir.addWidget(self.btn_output_dir)
        page_output_dir = QWidget(self)
        page_output_dir.setLayout(row_output_dir)
        self.output_stack.addWidget(page_output_dir)

        # Output row: Label + Mode combo + Stacked widget
        # Create label with fixed width for alignment (same width as Input: label)
        output_label = QLabel("Output:", self)
        output_label.setMinimumWidth(60)  # Same fixed width as Input: label for alignment
        output_label.setMaximumWidth(60)
        output_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Right-align text to align colons
        row_output_container = QHBoxLayout()
        row_output_container.setContentsMargins(0, 0, 0, 0)  # Remove default margins
        row_output_container.setSpacing(8)  # Small spacing between elements in the row
        row_output_container.addWidget(output_label)
        row_output_container.addWidget(self.combo_output_mode)
        row_output_container.addWidget(self.output_stack, 1)  # Stretch factor for stacked widget
        output_widget = QWidget(self)
        output_widget.setLayout(row_output_container)
        # Set size policy to prevent row from being compressed, spacing should compress first
        output_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addRow(output_widget)

        # Row 1: Checkbox (only Add timestamp)
        # Create label with same fixed width as Input/Output labels for alignment
        timestamp_label = QLabel("", self)
        timestamp_label.setMinimumWidth(60)  # Same fixed width as Input/Output labels
        timestamp_label.setMaximumWidth(60)
        timestamp_row_layout = QHBoxLayout()
        timestamp_row_layout.setContentsMargins(0, 0, 0, 0)  # Remove default margins
        timestamp_row_layout.setSpacing(8)  # Same spacing as other rows
        timestamp_row_layout.addWidget(timestamp_label)  # Empty label to match alignment
        self.check_timestamp = QCheckBox("Add timestamp to filename", self)
        self.check_timestamp.setChecked(True)
        timestamp_row_layout.addWidget(self.check_timestamp)
        timestamp_row_layout.addStretch()  # Push content to the left
        timestamp_widget = QWidget(self)
        timestamp_widget.setLayout(timestamp_row_layout)
        layout.addRow(timestamp_widget)

        # Switch stacked pages when mode changes
        self.combo_input_mode.currentIndexChanged.connect(self.input_stack.setCurrentIndex)
        self.combo_output_mode.currentIndexChanged.connect(self.output_stack.setCurrentIndex)

        # Connect button signals
        self.btn_input.clicked.connect(self._browse_input_file)
        self.btn_add_inputs.clicked.connect(self._add_input_files)
        self.btn_remove_inputs.clicked.connect(self._remove_selected_inputs)
        self.btn_input_dir.clicked.connect(self._browse_input_directory)
        self.btn_output.clicked.connect(self._browse_output_file)
        self.btn_output_dir.clicked.connect(self._browse_output_directory)
        
        # Connect input file change signal to auto-update output (real-time update)
        self.edit_input.textChanged.connect(self._auto_update_output_file)
        # Connect editingFinished to save config only when user finishes editing
        self.edit_input.editingFinished.connect(self.save_config_to_coordinator)
        self.edit_output.editingFinished.connect(self.save_config_to_coordinator)

    def set_config_coordinator(self, coordinator):
        """Set ConfigCoordinator for reading/writing configuration."""
        self.config_coordinator = coordinator

    def set_config(
        self,
        input_file: str,
        output_file: str,
        add_timestamp: bool = True,
    ) -> None:
        self.edit_input.setText(input_file)
        self.edit_output.setText(output_file)
        self.check_timestamp.setChecked(add_timestamp)

    def load_config_from_coordinator(self):
        """Load configuration from ConfigCoordinator and update UI."""
        if not self.config_coordinator:
            return

        file_config = self.config_coordinator.get_file_processing_config()

        # Backward-compatible defaults
        input_file = file_config.get("input_file", "")
        output_file = file_config.get("output_file", "")
        add_timestamp = file_config.get("add_timestamp", True)

        input_mode = file_config.get("input_mode") or "file"
        output_mode = file_config.get("output_mode") or "file"

        # Input: Always set all input-related controls, regardless of current mode
        # This ensures default values are available when user switches modes
        if input_mode == "file":
            self.combo_input_mode.setCurrentIndex(0)
            input_file_value = input_file or (file_config.get("input_paths", [""]) or [""])[0]
            # Convert to relative path for display (with forward slashes)
            if input_file_value and self.config_coordinator:
                input_file_value = to_relative_path(input_file_value, self.config_coordinator.project_root)
            self.edit_input.setText(input_file_value)
        elif input_mode == "files":
            self.combo_input_mode.setCurrentIndex(1)
            self.list_inputs.clear()
            for p in file_config.get("input_paths", []):
                if p:
                    # Convert to relative path for display (with forward slashes)
                    if self.config_coordinator:
                        relative_path = to_relative_path(p, self.config_coordinator.project_root)
                    else:
                        relative_path = p
                    self.list_inputs.addItem(relative_path)
        else:
            self.combo_input_mode.setCurrentIndex(2)
        
        # Always set input_dir and input_glob (for directory mode) with defaults
        input_dir = file_config.get("input_dir", "").strip()
        if input_dir and self.config_coordinator:
            # Convert to relative path for display (using platform-native separators)
            input_dir = to_relative_path(input_dir, self.config_coordinator.project_root)
        else:
            input_dir = normalize_relative_path(input_dir or "data/input/")
        self.edit_input_dir.setText(input_dir)
        input_glob = file_config.get("input_glob", "").strip()
        self.edit_input_glob.setText(input_glob if input_glob else "*.*")

        # Output: Always set all output-related controls, regardless of current mode
        if output_mode == "file":
            self.combo_output_mode.setCurrentIndex(0)
            # Convert to relative path for display (with forward slashes)
            if output_file and self.config_coordinator:
                output_file = to_relative_path(output_file, self.config_coordinator.project_root)
            self.edit_output.setText(output_file)
        else:
            self.combo_output_mode.setCurrentIndex(1)
        
        # Always set output_path (for directory mode) with default
        output_path = file_config.get("output_path", "").strip()
        if output_path and self.config_coordinator:
            # Convert to relative path for display (using platform-native separators)
            output_path = to_relative_path(output_path, self.config_coordinator.project_root)
        else:
            output_path = normalize_relative_path(output_path or "data/output/")
        self.edit_output_dir.setText(output_path)

        self.check_timestamp.setChecked(bool(add_timestamp))

    def save_config_to_coordinator(self):
        """Save current UI state to ConfigCoordinator."""
        if not self.config_coordinator:
            return

        # Compose new config including legacy fields for backward compatibility
        file_config: dict[str, object] = {
            "add_timestamp": self.check_timestamp.isChecked(),
        }

        # Input: Save current mode values and explicitly clear other modes
        input_mode_index = self.combo_input_mode.currentIndex()
        if input_mode_index == 0:
            # File mode: save only input_file, clear other modes
            file_config["input_mode"] = "file"
            file_config["input_file"] = self.edit_input.text().strip()
            # Clear other modes
            file_config["input_paths"] = []
            file_config["input_dir"] = ""
            file_config["input_glob"] = ""
        elif input_mode_index == 1:
            # Files mode: save only input_paths, clear other modes
            file_config["input_mode"] = "files"
            paths = [self.list_inputs.item(i).text().strip() for i in range(self.list_inputs.count())]
            file_config["input_paths"] = [p for p in paths if p]
            # Clear other modes
            file_config["input_file"] = ""
            file_config["input_dir"] = ""
            file_config["input_glob"] = ""
        else:
            # Directory mode: save only input_dir and input_glob, clear other modes
            file_config["input_mode"] = "directory"
            file_config["input_dir"] = self.edit_input_dir.text().strip()
            file_config["input_glob"] = self.edit_input_glob.text().strip()
            # Clear other modes
            file_config["input_file"] = ""
            file_config["input_paths"] = []

        # Output: Save current mode values and explicitly clear other modes
        output_mode_index = self.combo_output_mode.currentIndex()
        if output_mode_index == 0:
            # File mode: save only output_file, clear directory mode
            file_config["output_mode"] = "file"
            file_config["output_file"] = self.edit_output.text().strip()
            # Clear directory mode
            file_config["output_path"] = ""
        else:
            # Directory mode: save only output_path, clear file mode
            file_config["output_mode"] = "directory"
            file_config["output_path"] = self.edit_output_dir.text().strip()
            # Clear file mode
            file_config["output_file"] = ""

        self.config_coordinator.set_file_processing_config(file_config)

    def _auto_update_output_file(self) -> None:
        """Auto-update output file based on input file when in file/file mode."""
        # Only auto-update when both input and output modes are "file"
        if self.combo_input_mode.currentIndex() != 0:  # Not "File" mode
            return
        if self.combo_output_mode.currentIndex() != 0:  # Not "File" mode
            return
        
        input_path_str = self.edit_input.text().strip()
        if not input_path_str:
            return
        
        try:
            # Convert relative path to absolute for processing
            if not self.config_coordinator:
                return
            input_path = to_absolute_path(input_path_str, self.config_coordinator.project_root)
            
            # Get input stem (filename without extension)
            input_stem = input_path.stem
            input_suffix = input_path.suffix  # includes the dot, e.g., ".txt"
            
            # Get project root and output directory
            if not self.config_coordinator:
                return
            project_root = self.config_coordinator.project_root
            output_dir = (project_root / "data" / "output").resolve()
            
            # Get current output file to determine suffix
            current_output = self.edit_output.text().strip()
            if current_output:
                # If output has value, inherit its suffix
                current_output_path = to_absolute_path(current_output, project_root)
                output_suffix = current_output_path.suffix
                if not output_suffix:
                    # If current output has no suffix, use input suffix
                    output_suffix = input_suffix
                suggested_output_name = f"{input_stem}{output_suffix}"
            else:
                # If output is empty, use input filename as-is
                suggested_output_name = input_path.name
            
            # Generate relative path for display
            suggested_output = to_relative_path(str(output_dir / suggested_output_name), project_root)
            
            # Update output field (without triggering recursive updates)
            self.edit_output.blockSignals(True)
            self.edit_output.setText(suggested_output)
            self.edit_output.blockSignals(False)
            
            # Note: Config saving is handled by editingFinished signal
            # to avoid saving on every keystroke
        except Exception:
            # Silently ignore errors (e.g., invalid path format)
            pass

    def _browse_input_file(self) -> None:
        """Browse for a single input file."""
        start_dir = self.edit_input.text().strip()
        if start_dir:
            # Convert relative path to absolute for file dialog
            if not self.config_coordinator:
                start_dir = ""
            else:
                start_path = to_absolute_path(start_dir, self.config_coordinator.project_root)
                if start_path.exists():
                    if start_path.is_file():
                        start_dir = str(start_path.parent)
                    elif start_path.is_dir():
                        start_dir = str(start_path)
                else:
                    # Path doesn't exist, use parent if it's a file path, or path itself
                    start_dir = str(start_path.parent) if start_path.suffix else str(start_path)
        else:
            # Default to data/input directory
            if self.config_coordinator:
                project_root = self.config_coordinator.project_root
                start_dir = str((project_root / "data" / "input").resolve())
            else:
                start_dir = ""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input File",
            start_dir,
            "All Files (*.*)",
        )
        if file_path:
            # Convert to relative path for display (with forward slashes)
            if self.config_coordinator:
                relative_path = to_relative_path(file_path, self.config_coordinator.project_root)
            else:
                relative_path = file_path
            self.edit_input.setText(relative_path)
            # _auto_update_output_file will be called via textChanged signal
            self.save_config_to_coordinator()

    def _add_input_files(self) -> None:
        """Add multiple input files to the list."""
        start_dir = ""
        if self.list_inputs.count() > 0:
            last_item = self.list_inputs.item(self.list_inputs.count() - 1)
            if last_item:
                last_path = Path(last_item.text().strip())
                if last_path.is_file():
                    start_dir = str(last_path.parent)
                elif last_path.is_dir():
                    start_dir = str(last_path)
        
        if not start_dir:
            # Default to data/input directory
            if self.config_coordinator:
                project_root = self.config_coordinator.project_root
                start_dir = str((project_root / "data" / "input").resolve())
            else:
                start_dir = ""

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Input Files",
            start_dir,
            "All Files (*.*)",
        )
        for file_path in file_paths:
            # Convert to relative path for display (with forward slashes)
            if self.config_coordinator:
                relative_path = to_relative_path(file_path, self.config_coordinator.project_root)
            else:
                relative_path = file_path
            # Avoid duplicates
            existing_paths = [self.list_inputs.item(i).text().strip() for i in range(self.list_inputs.count())]
            if relative_path not in existing_paths:
                self.list_inputs.addItem(relative_path)
        if file_paths:
            self.save_config_to_coordinator()

    def _remove_selected_inputs(self) -> None:
        """Remove selected items from the input files list."""
        selected_items = self.list_inputs.selectedItems()
        for item in selected_items:
            row = self.list_inputs.row(item)
            self.list_inputs.takeItem(row)
        if selected_items:
            self.save_config_to_coordinator()

    def _browse_input_directory(self) -> None:
        """Browse for an input directory."""
        start_dir = self.edit_input_dir.text().strip()
        if start_dir:
            # Resolve relative path to absolute
            try:
                start_path = Path(start_dir)
                if not start_path.is_absolute() and self.config_coordinator:
                    start_path = self.config_coordinator.project_root / start_dir
                start_dir = str(start_path.resolve())
            except Exception:
                pass
        
        if not start_dir:
            # Default to data/input directory
            if self.config_coordinator:
                project_root = self.config_coordinator.project_root
                start_dir = str((project_root / "data" / "input").resolve())
            else:
                start_dir = ""

        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Input Directory",
            start_dir,
        )
        if dir_path:
            # Convert to relative path for display (with forward slashes)
            if self.config_coordinator:
                relative_path = to_relative_path(dir_path, self.config_coordinator.project_root)
            else:
                relative_path = dir_path
            self.edit_input_dir.setText(relative_path)
            self.save_config_to_coordinator()

    def _browse_output_file(self) -> None:
        """Browse for an output file."""
        start_dir = self.edit_output.text().strip()
        if start_dir:
            # Convert relative path to absolute for file dialog
            if not self.config_coordinator:
                start_dir = ""
            else:
                    start_path = to_absolute_path(start_dir, self.config_coordinator.project_root)
                    if start_path.exists():
                        if start_path.is_file():
                            start_dir = str(start_path.parent)
                        elif start_path.is_dir():
                            start_dir = str(start_path)
                    else:
                        # Path doesn't exist, use parent if it's a file path, or path itself
                        start_dir = str(start_path.parent) if start_path.suffix else str(start_path)
        else:
            # Default to data/output directory
            if self.config_coordinator:
                project_root = self.config_coordinator.project_root
                start_dir = str((project_root / "data" / "output").resolve())
            else:
                start_dir = ""

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            start_dir,
            "All Files (*.*)",
        )
        if file_path:
            # Convert to relative path for display (with forward slashes)
            if self.config_coordinator:
                relative_path = to_relative_path(file_path, self.config_coordinator.project_root)
            else:
                relative_path = file_path
            self.edit_output.setText(relative_path)
            self.save_config_to_coordinator()

    def _browse_output_directory(self) -> None:
        """Browse for an output directory."""
        start_dir = self.edit_output_dir.text().strip()
        if start_dir:
            # Resolve relative path to absolute
            try:
                start_path = Path(start_dir)
                if not start_path.is_absolute() and self.config_coordinator:
                    start_path = self.config_coordinator.project_root / start_dir
                start_dir = str(start_path.resolve())
            except Exception:
                pass
        
        if not start_dir:
            # Default to data/output directory
            if self.config_coordinator:
                project_root = self.config_coordinator.project_root
                start_dir = str((project_root / "data" / "output").resolve())
            else:
                start_dir = ""

        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            start_dir,
        )
        if dir_path:
            # Convert to relative path for display (with forward slashes)
            if self.config_coordinator:
                relative_path = to_relative_path(dir_path, self.config_coordinator.project_root)
            else:
                relative_path = dir_path
            self.edit_output_dir.setText(relative_path)
            self.save_config_to_coordinator()
