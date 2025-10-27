"""
插件管理面板组件

提供插件发现、选择、配置和链管理功能
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from subtitleformatter.plugins import PluginRegistry
from subtitleformatter.utils.unified_logger import logger


class PluginManagementPanel(QWidget):
    """
    插件管理面板

    功能:
    - 显示可用插件列表
    - 管理插件链配置
    - 提供插件启用/禁用控制
    """

    pluginSelected = Signal(str)
    pluginChainChanged = Signal(list)
    pluginEnabled = Signal(str, bool)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.available_plugins: Dict[str, Dict] = {}
        self.plugin_chain: List[str] = []
        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 创建垂直分割器
        splitter = QSplitter(Qt.Vertical)

        # 可用插件组 - 改为普通 Widget，去除组框
        available_group = QWidget()
        available_layout = QVBoxLayout(available_group)
        available_layout.setContentsMargins(4, 6, 4, 6)

        # 添加标题到框内
        available_title = QLabel("Available Plugins")
        available_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #2196F3;")
        available_layout.addWidget(available_title)

        self.available_list = QListWidget()
        self.available_list.setStyleSheet("QListWidget { padding: 5px; } QListWidget::item { padding: 3px; }")
        self.available_list.itemClicked.connect(self.on_plugin_selected)
        self.available_list.currentRowChanged.connect(self.on_available_current_changed)
        available_layout.addWidget(self.available_list)

        # 插件操作按钮
        plugin_buttons = QHBoxLayout()
        self.add_plugin_btn = QPushButton("Add to Chain")
        self.add_plugin_btn.clicked.connect(self.add_plugin_to_chain)
        self.add_plugin_btn.setEnabled(False)

        plugin_buttons.addWidget(self.add_plugin_btn)
        available_layout.addLayout(plugin_buttons)

        splitter.addWidget(available_group)

        # 插件链组 - 改为普通 Widget，去除组框
        chain_group = QWidget()
        chain_layout = QVBoxLayout(chain_group)
        chain_layout.setContentsMargins(4, 4, 4, 4)

        # 添加标题到框内
        chain_title = QLabel("Plugin Chain")
        chain_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #2196F3;")
        chain_layout.addWidget(chain_title)

        self.chain_list = QListWidget()
        self.chain_list.setStyleSheet("QListWidget { padding: 5px; } QListWidget::item { padding: 3px; }")
        self.chain_list.itemClicked.connect(self.on_chain_item_selected)
        self.chain_list.currentRowChanged.connect(self.on_chain_current_changed)
        self.chain_list.setDragDropMode(QListWidget.InternalMove)
        self.chain_list.model().rowsMoved.connect(self.on_chain_reordered)
        chain_layout.addWidget(self.chain_list)

        # 链操作按钮
        chain_buttons = QHBoxLayout()
        self.move_up_btn = QPushButton("Up")
        self.move_up_btn.clicked.connect(self.move_plugin_up)
        self.move_up_btn.setEnabled(False)

        self.move_down_btn = QPushButton("Down")
        self.move_down_btn.clicked.connect(self.move_plugin_down)
        self.move_down_btn.setEnabled(False)

        self.remove_plugin_btn = QPushButton("Remove")
        self.remove_plugin_btn.clicked.connect(self.remove_plugin_from_chain)
        self.remove_plugin_btn.setEnabled(False)

        self.clear_chain_btn = QPushButton("Clear All")
        self.clear_chain_btn.clicked.connect(self.clear_plugin_chain)

        # 设置按钮的 padding 上下 3px，左右 5px
        chain_button_style = "QPushButton { padding: 3px 5px; }"
        self.move_up_btn.setStyleSheet(chain_button_style)
        self.move_down_btn.setStyleSheet(chain_button_style)
        self.remove_plugin_btn.setStyleSheet(chain_button_style)
        self.clear_chain_btn.setStyleSheet(chain_button_style)

        chain_buttons.addWidget(self.move_up_btn)
        chain_buttons.addWidget(self.move_down_btn)
        chain_buttons.addWidget(self.remove_plugin_btn)
        chain_buttons.addWidget(self.clear_chain_btn)
        chain_layout.addLayout(chain_buttons)

        # 插件链配置按钮
        chain_config_buttons = QHBoxLayout()
        self.import_chain_btn = QPushButton("Import Chain")
        self.import_chain_btn.clicked.connect(self.import_plugin_chain)
        
        self.export_chain_btn = QPushButton("Export Chain")
        self.export_chain_btn.clicked.connect(self.export_plugin_chain)
        
        # 设置配置按钮的左右 padding
        self.import_chain_btn.setStyleSheet(chain_button_style)
        self.export_chain_btn.setStyleSheet(chain_button_style)
        
        chain_config_buttons.addWidget(self.import_chain_btn)
        chain_config_buttons.addWidget(self.export_chain_btn)
        chain_layout.addLayout(chain_config_buttons)

        splitter.addWidget(chain_group)

        # 设置分割器比例
        splitter.setSizes([300, 300])
        splitter.setStretchFactor(0, 1)  # 可用插件可伸缩
        splitter.setStretchFactor(1, 1)  # 插件链可伸缩

        layout.addWidget(splitter)

        # 设置布局
        self.setLayout(layout)

    def update_available_plugins(self, plugins: Dict[str, Dict]):
        """更新可用插件列表"""
        print(f"PluginManagementPanel: Updating with {len(plugins)} plugins")
        self.available_plugins = plugins
        self.available_list.clear()

        for plugin_name, metadata in plugins.items():
            print(f"PluginManagementPanel: Adding plugin {plugin_name}")
            item = QListWidgetItem()
            item.setText(metadata.get("name", plugin_name))
            item.setData(Qt.UserRole, plugin_name)
            item.setToolTip(metadata.get("description", ""))

            self.available_list.addItem(item)

        print(f"PluginManagementPanel: Added {self.available_list.count()} items to list")

    def on_plugin_selected(self, item: QListWidgetItem):
        """处理插件选择"""
        plugin_name = item.data(Qt.UserRole)
        if plugin_name in self.available_plugins:
            # 更新按钮状态 - 总是启用添加按钮
            self.add_plugin_btn.setEnabled(True)

            # 发送信号
            self.pluginSelected.emit(plugin_name)

    def on_available_current_changed(self, current_row: int):
        """处理可用插件列表当前行变化（键盘导航）"""
        if current_row >= 0 and current_row < self.available_list.count():
            item = self.available_list.item(current_row)
            if item:
                plugin_name = item.data(Qt.UserRole)
                if plugin_name in self.available_plugins:
                    # 更新按钮状态 - 总是启用添加按钮
                    self.add_plugin_btn.setEnabled(True)
                    
                    # 发送信号
                    self.pluginSelected.emit(plugin_name)

    def add_plugin_to_chain(self):
        """添加插件到链中"""
        current_item = self.available_list.currentItem()
        if not current_item:
            return

        plugin_name = current_item.data(Qt.UserRole)
        # 直接添加插件，不检查是否已存在
        self.plugin_chain.append(plugin_name)
        self.update_chain_display()
        self.pluginChainChanged.emit(self.plugin_chain)

        logger.info(f"Added plugin '{plugin_name}' to chain")

    def remove_plugin_from_chain(self):
        """从链中移除插件"""
        current_item = self.chain_list.currentItem()
        if not current_item:
            return

        current_row = self.chain_list.currentRow()
        if 0 <= current_row < len(self.plugin_chain):
            # 根据行索引移除插件，而不是根据名称
            removed_plugin = self.plugin_chain.pop(current_row)
            self.update_chain_display()
            self.pluginChainChanged.emit(self.plugin_chain)

            # 更新按钮状态
            self.remove_plugin_btn.setEnabled(False)

            logger.info(f"Removed plugin '{removed_plugin}' from chain")

    def on_chain_item_selected(self, item: QListWidgetItem):
        """处理链项目选择"""
        plugin_name = item.data(Qt.UserRole)

        # 更新按钮状态
        current_index = self.chain_list.currentRow()
        self.move_up_btn.setEnabled(current_index > 0)
        self.move_down_btn.setEnabled(current_index < len(self.plugin_chain) - 1)
        self.remove_plugin_btn.setEnabled(True)

        # 发送信号
        self.pluginSelected.emit(plugin_name)

    def on_chain_current_changed(self, current_row: int):
        """处理插件链列表当前行变化（键盘导航）"""
        if current_row >= 0 and current_row < self.chain_list.count():
            item = self.chain_list.item(current_row)
            if item:
                plugin_name = item.data(Qt.UserRole)
                
                # 更新按钮状态
                self.move_up_btn.setEnabled(current_row > 0)
                self.move_down_btn.setEnabled(current_row < len(self.plugin_chain) - 1)
                self.remove_plugin_btn.setEnabled(True)
                
                # 发送信号
                self.pluginSelected.emit(plugin_name)

    def on_chain_reordered(self):
        """处理链重排序"""
        # 更新插件链顺序
        self.plugin_chain.clear()
        for i in range(self.chain_list.count()):
            item = self.chain_list.item(i)
            plugin_name = item.data(Qt.UserRole)
            self.plugin_chain.append(plugin_name)

        self.pluginChainChanged.emit(self.plugin_chain)
        logger.info("Plugin chain reordered")

    def move_plugin_up(self):
        """向上移动插件"""
        current_row = self.chain_list.currentRow()
        if current_row > 0:
            item = self.chain_list.takeItem(current_row)
            self.chain_list.insertItem(current_row - 1, item)
            self.chain_list.setCurrentRow(current_row - 1)
            self.on_chain_reordered()

            # 更新按钮状态
            new_row = current_row - 1
            self.move_up_btn.setEnabled(new_row > 0)
            self.move_down_btn.setEnabled(new_row < self.chain_list.count() - 1)

    def move_plugin_down(self):
        """向下移动插件"""
        current_row = self.chain_list.currentRow()
        if current_row < self.chain_list.count() - 1:
            item = self.chain_list.takeItem(current_row)
            self.chain_list.insertItem(current_row + 1, item)
            self.chain_list.setCurrentRow(current_row + 1)
            self.on_chain_reordered()

            # 更新按钮状态
            new_row = current_row + 1
            self.move_up_btn.setEnabled(new_row > 0)
            self.move_down_btn.setEnabled(new_row < self.chain_list.count() - 1)

    def clear_plugin_chain(self):
        """清空插件链"""
        self.plugin_chain.clear()
        self.update_chain_display()
        self.update_available_plugins(self.available_plugins)
        self.pluginChainChanged.emit(self.plugin_chain)

        # 禁用所有链操作按钮
        self.move_up_btn.setEnabled(False)
        self.move_down_btn.setEnabled(False)
        self.remove_plugin_btn.setEnabled(False)

        logger.info("Plugin chain cleared")

    def update_chain_display(self):
        """更新链显示"""
        self.chain_list.clear()

        for plugin_name in self.plugin_chain:
            if plugin_name in self.available_plugins:
                metadata = self.available_plugins[plugin_name]
                item = QListWidgetItem()
                item.setText(metadata.get("name", plugin_name))
                item.setData(Qt.UserRole, plugin_name)
                item.setToolTip(metadata.get("description", ""))
                self.chain_list.addItem(item)

    def get_plugin_chain_config(self) -> Dict[str, Any]:
        """获取插件链配置"""
        return {"plugins": {"order": self.plugin_chain}}

    def load_plugin_chain_config(self, config: Dict[str, Any]):
        """加载插件链配置"""
        if "plugins" in config and "order" in config["plugins"]:
            self.plugin_chain = config["plugins"]["order"].copy()
            self.update_chain_display()
            # 不需要重新更新可用插件，因为available_plugins已经设置过了
            self.pluginChainChanged.emit(self.plugin_chain)

    def set_config_coordinator(self, coordinator):
        """设置配置协调器"""
        self.config_coordinator = coordinator

    def import_plugin_chain(self):
        """导入插件链配置"""
        from PySide6.QtWidgets import QFileDialog
        from pathlib import Path
        
        # 设置默认目录为 data/configs/plugin_chains
        default_dir = Path("data/configs/plugin_chains")
        if not default_dir.exists():
            default_dir.mkdir(parents=True, exist_ok=True)
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Plugin Chain", str(default_dir), "TOML Files (*.toml);;All Files (*)"
        )
        
        if file_path:
            try:
                from pathlib import Path
                chain_config = self.config_coordinator.import_plugin_chain(Path(file_path))
                
                # 更新插件链
                if "plugins" in chain_config and "order" in chain_config["plugins"]:
                    self.plugin_chain = chain_config["plugins"]["order"].copy()
                    self.update_chain_display()
                    self.update_available_plugins(self.available_plugins)
                    self.pluginChainChanged.emit(self.plugin_chain)
                    logger.info(f"Imported plugin chain from {file_path}")
                else:
                    logger.error("Invalid plugin chain file format")
                    
            except Exception as e:
                logger.error(f"Failed to import plugin chain: {e}")

    def export_plugin_chain(self):
        """导出插件链配置"""
        from PySide6.QtWidgets import QFileDialog
        from pathlib import Path
        
        if not self.plugin_chain:
            logger.warning("Plugin chain is empty")
            return
        
        # 设置默认目录为 data/configs/plugin_chains
        default_dir = Path("data/configs/plugin_chains")
        if not default_dir.exists():
            default_dir.mkdir(parents=True, exist_ok=True)
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Plugin Chain", str(default_dir), "TOML Files (*.toml);;All Files (*)"
        )
        
        if file_path:
            try:
                from pathlib import Path
                
                # 获取当前插件链中所有插件的配置
                plugin_configs = self.config_coordinator.get_all_plugin_configs(self.plugin_chain)
                
                self.config_coordinator.export_plugin_chain(
                    self.plugin_chain, plugin_configs, Path(file_path)
                )
                
            except Exception as e:
                logger.error(f"Failed to export plugin chain: {e}")
