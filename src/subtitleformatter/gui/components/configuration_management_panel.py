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
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from subtitleformatter.utils.path_utils import normalize_path
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
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # 配置管理组
        config_group = QGroupBox("Configuration Management")
        config_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
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
        """
        )
        config_layout = QVBoxLayout(config_group)

        # 添加上方弹性空间，让按钮在QGroupBox中垂直居中
        config_layout.addStretch()

        # 配置按钮行 - 四个按钮在一行
        config_row = QHBoxLayout()

        # 按指定顺序添加按钮：Restore Last、Restore Default、Import Config、Export Config
        self.restore_last_btn = QPushButton("Restore Last")
        self.restore_last_btn.clicked.connect(self.restore_last_configuration)
        self.restore_last_btn.setMinimumHeight(40)
        self.restore_last_btn.setStyleSheet("font-size: 14px; font-weight: 500; padding: 8px 16px;")

        self.restore_default_btn = QPushButton("Restore Default")
        self.restore_default_btn.clicked.connect(self.restore_default_configuration)
        self.restore_default_btn.setMinimumHeight(40)
        self.restore_default_btn.setStyleSheet(
            "font-size: 14px; font-weight: 500; padding: 8px 16px;"
        )

        self.import_config_btn = QPushButton("Import Config")
        self.import_config_btn.clicked.connect(self.import_configuration)
        self.import_config_btn.setMinimumHeight(40)
        self.import_config_btn.setStyleSheet(
            "font-size: 14px; font-weight: 500; padding: 8px 16px;"
        )

        self.export_config_btn = QPushButton("Export Config")
        self.export_config_btn.clicked.connect(self.export_configuration)
        self.export_config_btn.setMinimumHeight(40)
        self.export_config_btn.setStyleSheet(
            "font-size: 14px; font-weight: 500; padding: 8px 16px;"
        )

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
            logger.error("Configuration coordinator not set")
            return

        default_dir = Path("data/configs")
        if not default_dir.exists():
            default_dir.mkdir(parents=True, exist_ok=True)

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Configuration", str(default_dir), "TOML Files (*.toml);;All Files (*)"
        )

        if file_path:
            try:
                unified_config = self.config_coordinator.import_unified_config(Path(file_path))
                chain_ref = None
                if unified_config and "plugins" in unified_config:
                    chain_ref = unified_config["plugins"].get("current_plugin_chain")
                chain_config = None
                if chain_ref:
                    ref_path = Path(chain_ref)
                    if ref_path.is_absolute():
                        chain_path = ref_path
                    else:
                        # 统一从 data/configs/plugin_chains 解析
                        base_dir = self.config_coordinator.chain_manager.plugin_chains_dir
                        # 若引用里自带 plugin_chains/ 前缀，也统一归一到 base_dir 下
                        if str(ref_path).startswith("plugin_chains/"):
                            chain_path = base_dir / str(ref_path).split("plugin_chains/", 1)[1]
                        else:
                            chain_path = base_dir / ref_path
                    if chain_path.exists():
                        chain_config = self.config_coordinator.chain_manager.load_chain(chain_path)
                        logger.info(f"Imported plugin chain from {chain_path}")
                    else:
                        logger.warning(
                            f"Plugin chain file missing: {chain_path}, fallback to default chain."
                        )
                if chain_config is None:
                    # fallback: 确保用户 plugin_chains 目录有 default_plugin_chain.toml
                    self.config_coordinator.chain_manager._ensure_default_chain_exists()
                    user_chain = self.config_coordinator.chain_manager.plugin_chains_dir / "default_plugin_chain.toml"
                    chain_config = self.config_coordinator.chain_manager.load_chain(user_chain)
                    logger.info("Fell back to user default plugin chain config on import.")

                main_window = self.window()
                logger.info("Dispatching on_configuration_restored after import configuration")
                if hasattr(main_window, "on_configuration_restored"):
                    main_window.on_configuration_restored(unified_config, chain_config)

            except Exception as e:
                logger.error(f"Failed to import configuration: {e}")

    def export_configuration(self):
        """导出配置文件"""
        if not self.config_coordinator:
            logger.error("Configuration coordinator not set")
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
                logger.debug(f"Exported configuration to {normalize_path(file_path)}")

            except Exception as e:
                logger.error(f"Failed to export configuration: {e}")

    def restore_last_configuration(self):
        """恢复到上次保存的配置"""
        if not self.config_coordinator:
            logger.error("Configuration coordinator not set")
            return

        try:
            # 恢复插件链配置从快照
            chain_config = self.config_coordinator.restore_chain_from_snapshot()

            # 恢复统一配置
            unified_config = self.config_coordinator.restore_last_config()

            logger.info("Restored configuration to last saved state")

            # 通知主窗口更新界面
            main_window = self.window()
            logger.info("Dispatching on_configuration_restored after restore last")
            if hasattr(main_window, "on_configuration_restored"):
                main_window.on_configuration_restored(unified_config, chain_config)

        except Exception as e:
            logger.error(f"Failed to restore configuration: {e}")

    def restore_default_configuration(self):
        """恢复默认配置"""
        if not self.config_coordinator:
            logger.error("Configuration coordinator not set")
            return

        try:
            # Use restore_default which loads default_config.toml and saves to config_latest.toml
            unified_config = self.config_coordinator.restore_default_config()
            # 保证用户 plugin_chains 目录下有 default_plugin_chain.toml
            self.config_coordinator.chain_manager._ensure_default_chain_exists()
            user_chain = self.config_coordinator.chain_manager.plugin_chains_dir / "default_plugin_chain.toml"
            chain_config = self.config_coordinator.chain_manager.load_chain(user_chain)
            logger.info("Restored configuration to default (user default chain in plugin_chains dir)")

            main_window = self.window()
            logger.info("Dispatching on_configuration_restored after restore default")
            if hasattr(main_window, "on_configuration_restored"):
                main_window.on_configuration_restored(unified_config, chain_config)

        except Exception as e:
            logger.error(f"Failed to restore default configuration: {e}")
