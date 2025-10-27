"""
SubtitleFormatter 插件化架构主窗口 - 完全重构版本

这个新的主窗口设计充分发挥插件化架构的优势，采用最大化窗口布局，
提供直观的插件管理和处理流程可视化。
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from subtitleformatter.config import ConfigCoordinator
from subtitleformatter.plugins import PluginLifecycleManager, PluginRegistry
from subtitleformatter.utils.unified_logger import logger
from subtitleformatter.version import get_app_title

from .components.configuration_management_panel import ConfigurationManagementPanel
from .components.file_processing_panel import FileProcessingPanel
from .components.log_panel import LogPanel
from .components.plugin_chain_visualizer import PluginChainVisualizer
from .components.plugin_config_panel import PluginConfigPanel
from .components.plugin_management_panel import PluginManagementPanel
from .components.status_bar import StatusBar
from .styles.theme_loader import ThemeLoader


class MainWindowV2(QMainWindow):
    """
    插件化架构主窗口 - 完全重构版本

    设计特点:
    - 最大化窗口布局，充分利用屏幕空间
    - 插件管理为核心，直观的插件链配置
    - 动态UI更新，根据插件状态实时调整界面
    - 保留优秀的LogPanel等组件
    """

    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.setWindowTitle(get_app_title())

        # 设置窗口图标
        icon_path = project_root / "src" / "subtitleformatter" / "gui" / "assets" / "app_icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # 初始化配置管理系统
        self.config_coordinator = ConfigCoordinator(project_root)

        # 初始化插件系统
        self.plugin_registry = PluginRegistry()
        self.plugin_lifecycle = None
        self.loaded_plugins: Dict[str, any] = {}

        # 设置最大化窗口
        self.setWindowState(Qt.WindowMaximized)
        self.setMinimumSize(1200, 800)

        # 创建主界面
        self.setup_ui()

        # 应用主题样式
        self.apply_modern_styling()

        # 初始化插件系统
        self.initialize_plugin_system()

        # 设置信号连接（必须在配置加载之前）
        self.setup_signals()

        # 加载配置
        self.load_configuration()

        # 设置配置协调器到各个面板
        self.file_processing.set_config_coordinator(self.config_coordinator)
        self.plugin_management.set_config_coordinator(self.config_coordinator)
        self.config_management.set_config_coordinator(self.config_coordinator)

        # 设置统一日志系统的GUI回调
        logger.set_gui_callback(self.log_panel.append_log)

    def setup_ui(self):
        """设置主界面布局"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 水平分割
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # 创建主水平分割器
        main_splitter = QSplitter(Qt.Horizontal)

        # 左侧：插件管理和流程区域
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # 右侧：处理面板和日志区域
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        # 设置主分割器比例
        main_splitter.setSizes([750, 600])
        main_splitter.setStretchFactor(0, 0)  # 左侧固定
        main_splitter.setStretchFactor(1, 1)  # 右侧可伸缩

        main_layout.addWidget(main_splitter)

        # 创建状态栏
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

    def create_left_panel(self) -> QWidget:
        """创建左侧插件管理和流程面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 创建左侧垂直分割器
        left_splitter = QSplitter(Qt.Vertical)

        # 顶部：配置管理面板
        self.config_management = ConfigurationManagementPanel(self)
        left_splitter.addWidget(self.config_management)

        # 底部：插件管理和配置的水平分割
        bottom_splitter = QSplitter(Qt.Horizontal)

        # 插件管理面板
        self.plugin_management = PluginManagementPanel(self)
        bottom_splitter.addWidget(self.plugin_management)

        # 插件配置面板
        self.plugin_config = PluginConfigPanel(self)
        bottom_splitter.addWidget(self.plugin_config)

        # 设置底部分割器比例
        bottom_splitter.setSizes([300, 400])  # 增加插件配置面板的初始宽度
        bottom_splitter.setStretchFactor(0, 0)  # 左侧固定
        bottom_splitter.setStretchFactor(1, 0)  # 右侧固定

        left_splitter.addWidget(bottom_splitter)

        # 设置左侧分割器比例 - 让配置管理面板能够充分利用空间
        left_splitter.setSizes([150, 1000])  # 配置管理占较小空间，插件区域占更多空间
        left_splitter.setStretchFactor(0, 1)  # 顶部可伸缩（配置管理区域）- 关键修改！
        left_splitter.setStretchFactor(1, 1)  # 底部可伸缩（插件区域）

        layout.addWidget(left_splitter)

        return panel

    def create_right_panel(self) -> QWidget:
        """创建右侧处理面板和日志面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 创建垂直分割器
        right_splitter = QSplitter(Qt.Vertical)

        # 文件处理面板
        self.file_processing = FileProcessingPanel(self)
        
        # 创建插件链可视化组件
        self.plugin_chain_visualizer = PluginChainVisualizer(self)
        
        # 将可视化组件设置到文件处理面板
        self.file_processing.set_plugin_chain_visualizer(self.plugin_chain_visualizer)
        
        right_splitter.addWidget(self.file_processing)

        # 日志面板
        self.log_panel = LogPanel()
        right_splitter.addWidget(self.log_panel)

        # 设置分割器比例
        right_splitter.setSizes([400, 200])
        right_splitter.setStretchFactor(0, 1)  # 处理面板可伸缩
        right_splitter.setStretchFactor(1, 0)  # 日志面板固定

        layout.addWidget(right_splitter)

        return panel

    def initialize_plugin_system(self):
        """初始化插件系统"""
        try:
            logger.info(f"Initializing plugin system in {self.project_root}")

            # 添加插件目录 - 自动扫描所有子目录
            plugin_dir = self.project_root / "plugins"
            if plugin_dir.exists():
                self.plugin_registry.add_plugin_dir(plugin_dir)
                logger.info(f"Added plugin directory: {plugin_dir}")

            # 扫描插件
            logger.info("Scanning plugins...")
            self.plugin_registry.scan_plugins()

            # 检查扫描结果
            plugin_names = self.plugin_registry.list_plugins()
            logger.info(f"After scanning, found {len(plugin_names)} plugins: {plugin_names}")

            # 创建生命周期管理器
            self.plugin_lifecycle = PluginLifecycleManager(self.plugin_registry)

            # 设置插件配置面板的注册表
            self.plugin_config.set_plugin_registry(self.plugin_registry)

            # 更新插件管理界面
            self.update_plugin_management_ui()

            logger.info("Plugin system initialized successfully")
            self.status_bar.set_message("Plugin system ready")

        except Exception as e:
            logger.error(f"Failed to initialize plugin system: {e}")
            self.status_bar.set_message(f"Plugin system error: {e}")

    def update_plugin_management_ui(self):
        """更新插件管理界面"""
        if not self.plugin_registry:
            logger.warning("Plugin registry not available")
            return

        # 获取可用插件
        plugin_names = self.plugin_registry.list_plugins()
        logger.info(f"Found {len(plugin_names)} plugins: {plugin_names}")

        available_plugins = {}
        for name in plugin_names:
            try:
                available_plugins[name] = self.plugin_registry.get_plugin_metadata(name)
            except Exception as e:
                logger.warning(f"Failed to get metadata for plugin {name}: {e}")

        logger.info(f"Updating plugin management UI with {len(available_plugins)} plugins")

        # 更新插件管理面板
        self.plugin_management.update_available_plugins(available_plugins)

        # 插件链可视化应该只显示用户配置的插件链，而不是所有可用插件
        # 初始时插件链为空，用户需要手动添加插件到链中

    def setup_signals(self):
        """设置信号连接"""
        # 插件管理信号
        if hasattr(self.plugin_management, "pluginSelected"):
            self.plugin_management.pluginSelected.connect(self.on_plugin_selected)

        if hasattr(self.plugin_management, "pluginChainChanged"):
            self.plugin_management.pluginChainChanged.connect(self.on_plugin_chain_changed)

        # 文件处理信号
        if hasattr(self.file_processing, "formatRequested"):
            self.file_processing.formatRequested.connect(self.on_format_requested)

        # 插件配置信号
        if hasattr(self.plugin_config, "configChanged"):
            self.plugin_config.configChanged.connect(self.on_plugin_config_changed)
            logger.debug("Plugin config signal connected successfully")
        else:
            logger.warning("Plugin config panel does not have configChanged signal")

    def on_plugin_selected(self, plugin_name: str):
        """处理插件选择事件"""
        try:
            # 更新插件配置面板
            self.plugin_config.load_plugin_config(plugin_name)

            # 更新状态栏
            self.status_bar.set_message(f"Selected plugin: {plugin_name}")

        except Exception as e:
            logger.error(f"Failed to select plugin {plugin_name}: {e}")

    def on_plugin_chain_changed(self, plugin_chain: List[str]):
        """处理插件链变更事件"""
        try:
            # 获取插件元数据
            plugin_metadata = {}
            if self.plugin_registry:
                for plugin_name in plugin_chain:
                    try:
                        plugin_metadata[plugin_name] = self.plugin_registry.get_plugin_metadata(
                            plugin_name
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get metadata for plugin {plugin_name}: {e}")

            # 更新插件链可视化
            self.plugin_chain_visualizer.update_plugin_chain(plugin_chain, plugin_metadata)

            # 更新状态栏
            self.status_bar.set_message(f"Plugin chain updated: {len(plugin_chain)} plugins")

        except Exception as e:
            logger.error(f"Failed to update plugin chain: {e}")

    def on_format_requested(self):
        """处理格式化请求"""
        try:
            # 获取文件处理配置
            config = self.file_processing.get_processing_config()

            # 获取插件链配置
            plugin_config = self.plugin_management.get_plugin_chain_config()

            # 合并配置
            full_config = {**config, **plugin_config}

            # 启动处理线程
            self.start_processing_thread(full_config)

        except Exception as e:
            logger.error(f"Failed to start processing: {e}")
            QMessageBox.critical(self, "Processing Error", f"Failed to start processing: {e}")

    def on_plugin_config_changed(self, plugin_name: str, config: Dict):
        """处理插件配置变更事件"""
        try:
            logger.debug(f"Plugin config changed signal received: {plugin_name}")
            
            # 更新插件配置
            if plugin_name in self.loaded_plugins:
                self.loaded_plugins[plugin_name].config.update(config)

            # 立即保存插件配置到文件
            if hasattr(self, 'config_coordinator'):
                saved_path = self.config_coordinator.save_plugin_config(plugin_name, config)
                logger.info(f"Plugin {plugin_name} configuration saved to {saved_path}")
            else:
                logger.warning("Config coordinator not available for saving plugin config")

            logger.info(f"Plugin {plugin_name} configuration updated")
            self.status_bar.set_message(f"Plugin {plugin_name} config updated")

        except Exception as e:
            logger.error(f"Failed to update plugin config: {e}")

    def start_processing_thread(self, config: Dict):
        """启动处理线程"""
        self.processing_thread = ProcessingThread(config, self.plugin_lifecycle)

        # 连接信号
        self.processing_thread.progress.connect(self.file_processing.update_progress)
        self.processing_thread.log.connect(self.log_panel.append_log)
        self.processing_thread.finished.connect(self.on_processing_finished)

        # 启动线程
        self.processing_thread.start()

        # 更新状态
        self.status_bar.set_message("Processing started...")

    def on_processing_finished(self, success: bool, message: str):
        """处理完成回调"""
        if success:
            self.status_bar.set_message("Processing completed successfully")
            logger.info(" " + message)
        else:
            self.status_bar.set_message("Processing failed")
            logger.error(" " + message)
            QMessageBox.critical(self, "Processing Error", message)

    def apply_modern_styling(self):
        """应用现代化样式"""
        try:
            app = QApplication.instance()
            theme_loader = ThemeLoader(self.project_root)
            theme_name = "default"
            theme_loader.apply_base_style(app, theme_name)
            self.setStyleSheet(theme_loader.load_theme(theme_name))
        except Exception as e:
            logger.warning(f"Failed to apply theme: {e}")

    def load_configuration(self):
        """加载配置"""
        try:
            config = self.config_coordinator.load_all_config()
            
            # 更新文件处理配置
            file_config = config.get("unified", {}).get("file_processing", {})
            self.file_processing.set_processing_config(file_config)
            
            # 确保可用插件已经设置
            if not hasattr(self.plugin_management, 'available_plugins') or not self.plugin_management.available_plugins:
                # 重新获取可用插件
                available_plugins = {}
                for name in self.plugin_registry.list_plugins():
                    try:
                        available_plugins[name] = self.plugin_registry.get_plugin_metadata(name)
                    except Exception as e:
                        logger.warning(f"Failed to get metadata for plugin {name}: {e}")
                
                self.plugin_management.update_available_plugins(available_plugins)
            
            # 更新插件链配置
            chain_config = config.get("plugin_chain", {})
            logger.debug(f"Chain config: {chain_config}")
            if "plugins" in chain_config and "order" in chain_config["plugins"]:
                logger.debug(f"Loading plugin chain with order: {chain_config['plugins']['order']}")
                self.plugin_management.load_plugin_chain_config(chain_config)
            else:
                logger.warning("No valid plugin chain configuration found")
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")

    def save_configuration(self):
        """保存配置"""
        try:
            # 保存文件处理配置
            file_config = self.file_processing.get_processing_config()
            self.config_coordinator.set_file_processing_config(file_config)
            
            # 保存插件链配置到 latest 文件
            chain_config = self.plugin_management.get_plugin_chain_config()
            if chain_config.get("plugins", {}).get("order"):
                plugin_configs = self.config_coordinator.get_all_plugin_configs(
                    chain_config["plugins"]["order"]
                )
                # 保存到 chain_latest.toml，不生成新文件
                self.config_coordinator.save_plugin_chain(
                    chain_config["plugins"]["order"],
                    plugin_configs,
                    "chain_latest.toml"
                )
            
            # 保存所有配置
            self.config_coordinator.save_all_config()
            
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 保存配置
        self.save_configuration()
        
        # 停止插件生命周期
        if self.plugin_lifecycle:
            self.plugin_lifecycle.cleanup_all()
        
        event.accept()


class ProcessingThread(QThread):
    """处理线程"""

    progress = Signal(int, str)
    log = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, config: Dict, plugin_lifecycle: PluginLifecycleManager):
        super().__init__()
        self.config = config
        self.plugin_lifecycle = plugin_lifecycle

    def run(self):
        """运行处理逻辑"""
        try:
            self.log.emit("Starting text processing...")

            # 检查是否使用插件系统
            if self.config.get("plugins") and self.config.get("plugins", {}).get("order"):
                # 使用插件系统
                from subtitleformatter.processors.plugin_text_processor import (
                    PluginTextProcessor,
                )

                processor = PluginTextProcessor(self.config)
                self.log.emit("Using plugin-based processing system")
            else:
                # 使用传统处理器
                from subtitleformatter.processors.text_processor import TextProcessor

                processor = TextProcessor(self.config)
                self.log.emit("Using legacy processing system")

            # 执行处理
            processor.process()

            self.finished.emit(True, "Processing completed successfully")

        except Exception as e:
            self.finished.emit(False, f"Processing failed: {e}")


def run_gui_v2() -> None:
    """运行新的GUI"""
    import sys

    app = QApplication(sys.argv)

    root = Path(__file__).resolve().parents[3]
    icon_path = root / "src" / "subtitleformatter" / "gui" / "assets" / "app_icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    w = MainWindowV2(root)
    w.show()
    sys.exit(app.exec())
