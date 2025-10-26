"""
文件处理面板组件

提供文件选择、处理控制和进度显示功能
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QProgressBar,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QFormLayout,
    QFileDialog,
    QMessageBox,
    QFrame,
)

from subtitleformatter.utils.unified_logger import logger


class FileProcessingPanel(QWidget):
    """
    文件处理面板
    
    功能:
    - 文件输入/输出选择
    - 处理参数配置
    - 处理进度显示
    - 处理控制
    """
    
    formatRequested = Signal()
    progressUpdated = Signal(int, str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 文件选择组
        file_group = QGroupBox("File Selection")
        file_layout = QFormLayout(file_group)
        
        # 输入文件
        input_layout = QHBoxLayout()
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("Select input file...")
        self.input_file_btn = QPushButton("Browse...")
        self.input_file_btn.clicked.connect(self.choose_input_file)
        input_layout.addWidget(self.input_file_edit)
        input_layout.addWidget(self.input_file_btn)
        file_layout.addRow("Input file:", input_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setPlaceholderText("Select output file...")
        self.output_file_btn = QPushButton("Browse...")
        self.output_file_btn.clicked.connect(self.choose_output_file)
        output_layout.addWidget(self.output_file_edit)
        output_layout.addWidget(self.output_file_btn)
        file_layout.addRow("Output file:", output_layout)
        
        layout.addWidget(file_group)
        
        # 处理选项组
        options_group = QGroupBox("Processing Options")
        options_layout = QFormLayout(options_group)
        
        # 添加时间戳
        self.add_timestamp_check = QCheckBox("Add timestamp to filename")
        self.add_timestamp_check.setChecked(True)
        options_layout.addRow("", self.add_timestamp_check)
        
        # 调试模式
        self.debug_mode_check = QCheckBox("Enable debug mode")
        self.debug_mode_check.setChecked(False)
        options_layout.addRow("", self.debug_mode_check)
        
        # 语言设置
        self.language_combo = QComboBox()
        self.language_combo.addItems(["auto", "en", "zh"])
        self.language_combo.setCurrentText("en")
        options_layout.addRow("Language:", self.language_combo)
        
        # 模型大小
        self.model_size_combo = QComboBox()
        self.model_size_combo.addItem("small", "sm")
        self.model_size_combo.addItem("medium", "md")
        self.model_size_combo.addItem("large", "lg")
        self.model_size_combo.setCurrentText("medium")
        options_layout.addRow("Model size:", self.model_size_combo)
        
        # 最大宽度
        self.max_width_spin = QSpinBox()
        self.max_width_spin.setRange(20, 200)
        self.max_width_spin.setValue(78)
        options_layout.addRow("Max width:", self.max_width_spin)
        
        layout.addWidget(options_group)
        
        # 处理控制组
        control_group = QGroupBox("Processing Control")
        control_layout = QVBoxLayout(control_group)
        
        # 处理按钮
        self.format_btn = QPushButton("Start Processing")
        self.format_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 12px 24px;
                font-weight: 700;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.format_btn.setMinimumHeight(50)
        self.format_btn.clicked.connect(self.start_processing)
        
        control_layout.addWidget(self.format_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #BDBDBD;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        control_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("Ready to process")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.status_label)
        
        layout.addWidget(control_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.setLayout(layout)
    
    def choose_input_file(self):
        """选择输入文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.input_file_edit.setText(file_path)
            logger.info(f"Selected input file: {file_path}")
    
    def choose_output_file(self):
        """选择输出文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.output_file_edit.setText(file_path)
            logger.info(f"Selected output file: {file_path}")
    
    def start_processing(self):
        """开始处理"""
        # 验证输入
        if not self.input_file_edit.text().strip():
            QMessageBox.warning(self, "Input Required", "Please select an input file.")
            return
        
        if not self.output_file_edit.text().strip():
            QMessageBox.warning(self, "Output Required", "Please select an output file.")
            return
        
        # 检查输入文件是否存在
        input_path = Path(self.input_file_edit.text().strip())
        if not input_path.exists():
            QMessageBox.warning(self, "File Not Found", f"Input file does not exist: {input_path}")
            return
        
        # 更新UI状态
        self.format_btn.setEnabled(False)
        self.format_btn.setText("Processing...")
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting processing...")
        
        # 发送处理请求信号
        self.formatRequested.emit()
        
        logger.info("Processing started")
    
    def update_progress(self, value: int, message: str = ""):
        """更新进度"""
        self.progress_bar.setValue(value)
        if message:
            self.status_label.setText(message)
    
    def processing_finished(self, success: bool, message: str = ""):
        """处理完成"""
        # 恢复UI状态
        self.format_btn.setEnabled(True)
        self.format_btn.setText("Start Processing")
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("Processing completed successfully")
            logger.info("Processing completed successfully")
        else:
            self.status_label.setText("Processing failed")
            logger.error(f"Processing failed: {message}")
    
    def get_processing_config(self) -> Dict[str, Any]:
        """获取处理配置"""
        return {
            "input_file": self.input_file_edit.text().strip(),
            "output_file": self.output_file_edit.text().strip(),
            "add_timestamp": self.add_timestamp_check.isChecked(),
            "debug_enabled": self.debug_mode_check.isChecked(),
            "language": self.language_combo.currentText(),
            "model_size": self.model_size_combo.currentData(),
            "max_width": self.max_width_spin.value(),
        }
    
    def set_processing_config(self, config: Dict[str, Any]):
        """设置处理配置"""
        if "input_file" in config:
            self.input_file_edit.setText(config["input_file"])
        
        if "output_file" in config:
            self.output_file_edit.setText(config["output_file"])
        
        if "add_timestamp" in config:
            self.add_timestamp_check.setChecked(config["add_timestamp"])
        
        if "debug_enabled" in config:
            self.debug_mode_check.setChecked(config["debug_enabled"])
        
        if "language" in config:
            self.language_combo.setCurrentText(config["language"])
        
        if "model_size" in config:
            index = self.model_size_combo.findData(config["model_size"])
            if index >= 0:
                self.model_size_combo.setCurrentIndex(index)
        
        if "max_width" in config:
            self.max_width_spin.setValue(config["max_width"])
