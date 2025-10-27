"""
配置管理面板组件

提供配置的导入、导出、恢复等功能
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from subtitleformatter.utils.unified_logger import logger


class ConfigurationManagementPanel(QWidget):
    """
    配置管理面板

    功能:
    - 导入配置文件
    - 导出配置文件
    - 恢复上次配置
    - 恢复默认配置
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config_coordinator = None
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 配置管理组
        config_group = QGroupBox("Configuration Management")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2196F3;
                border: 2px solid #2196F3;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        config_layout = QVBoxLayout(config_group)
        
        # 添加上方弹性空间，让按钮在QGroupBox中垂直居中
        config_layout.addStretch()

        # 配置按钮行 - 四个按钮在一行
        config_row = QHBoxLayout()
        
        # 按指定顺序添加按钮：Restore Last、Restore Default、Import Config、Export Config
        self.restore_last_btn = QPushButton("Restore Last")
        self.restore_last_btn.clicked.connect(self.restore_last_configuration)
        self.restore_last_btn.setMinimumHeight(40)
        self.restore_last_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
                background-color: #f5f5f5;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #bbb;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        self.restore_default_btn = QPushButton("Restore Default")
        self.restore_default_btn.clicked.connect(self.restore_default_configuration)
        self.restore_default_btn.setMinimumHeight(40)
        self.restore_default_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
                background-color: #f5f5f5;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #bbb;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        self.import_config_btn = QPushButton("Import Config")
        self.import_config_btn.clicked.connect(self.import_configuration)
        self.import_config_btn.setMinimumHeight(40)
        self.import_config_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
                background-color: #f5f5f5;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #bbb;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        self.export_config_btn = QPushButton("Export Config")
        self.export_config_btn.clicked.connect(self.export_configuration)
        self.export_config_btn.setMinimumHeight(40)
        self.export_config_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
                background-color: #f5f5f5;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #bbb;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        config_row.addWidget(self.restore_last_btn)
        config_row.addWidget(self.restore_default_btn)
        config_row.addWidget(self.import_config_btn)
        config_row.addWidget(self.export_config_btn)

        config_layout.addLayout(config_row)
        
        # 添加下方弹性空间，让按钮在QGroupBox中垂直居中
        config_layout.addStretch()
        
        layout.addWidget(config_group)

        self.setLayout(layout)

    def set_config_coordinator(self, coordinator):
        """设置配置协调器"""
        self.config_coordinator = coordinator

    def import_configuration(self):
        """导入配置文件"""
        if not self.config_coordinator:
            QMessageBox.warning(self, "Error", "Configuration coordinator not set")
            return
            
        # 设置默认目录为 data/configs
        default_dir = Path("data/configs")
        if not default_dir.exists():
            default_dir.mkdir(parents=True, exist_ok=True)
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Configuration", str(default_dir), "TOML Files (*.toml);;All Files (*)"
        )
        
        if file_path:
            try:
                config = self.config_coordinator.import_unified_config(Path(file_path))
                QMessageBox.information(self, "Success", "Configuration imported successfully!")
                logger.info(f"Imported configuration from {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import configuration: {e}")
                logger.error(f"Failed to import configuration: {e}")

    def export_configuration(self):
        """导出配置文件"""
        if not self.config_coordinator:
            QMessageBox.warning(self, "Error", "Configuration coordinator not set")
            return
            
        # 设置默认目录为 data/configs
        default_dir = Path("data/configs")
        if not default_dir.exists():
            default_dir.mkdir(parents=True, exist_ok=True)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Configuration", str(default_dir), "TOML Files (*.toml);;All Files (*)"
        )
        
        if file_path:
            try:
                self.config_coordinator.export_unified_config(Path(file_path))
                QMessageBox.information(self, "Success", "Configuration exported successfully!")
                logger.info(f"Exported configuration to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export configuration: {e}")
                logger.error(f"Failed to export configuration: {e}")

    def restore_last_configuration(self):
        """恢复到上次保存的配置"""
        if not self.config_coordinator:
            QMessageBox.warning(self, "Error", "Configuration coordinator not set")
            return
            
        try:
            config = self.config_coordinator.restore_last_config()
            QMessageBox.information(self, "Success", "Configuration restored to last saved state!")
            logger.info("Restored configuration to last saved state")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore configuration: {e}")
            logger.error(f"Failed to restore configuration: {e}")

    def restore_default_configuration(self):
        """恢复默认配置"""
        if not self.config_coordinator:
            QMessageBox.warning(self, "Error", "Configuration coordinator not set")
            return
            
        try:
            config = self.config_coordinator.restore_default_config()
            QMessageBox.information(self, "Success", "Configuration restored to default!")
            logger.info("Restored configuration to default")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore default configuration: {e}")
            logger.error(f"Failed to restore default configuration: {e}")
