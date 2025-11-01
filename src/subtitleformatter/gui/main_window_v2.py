"""
SubtitleFormatter 插件化架构主窗口 - 完全重构版本

这个新的主窗口设计充分发挥插件化架构的优势，采用最大化窗口布局，
提供直观的插件管理和处理流程可视化。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from subtitleformatter.config import ConfigCoordinator
from subtitleformatter.plugins import PluginLifecycleManager, PluginRegistry
from subtitleformatter.runtime.config_materializer import materialize_runtime_config
from subtitleformatter.runtime.plugin_runtime import (
    initialize_plugin_system as runtime_init_plugins,
)
from subtitleformatter.utils.unified_logger import logger
from subtitleformatter.version import get_app_title

from .components.command_panel import CommandPanel
from .components.configuration_management_panel import ConfigurationManagementPanel
from .components.log_panel import LogPanel
from .components.plugin_chain_visualizer import PluginChainVisualizer
from .components.plugin_config_panel import PluginConfigPanel
from .components.plugin_management_panel import PluginManagementPanel
from .components.processing_flow_panel import ProcessingFlowPanel
from .components.tabs_panel import TabsPanel
from .pages.about_page import AboutPage
from .pages.advanced_page import AdvancedPage
from .pages.basic_page import BasicPage
from .styles.theme_loader import ThemeLoader
from .threads.processing_thread import ProcessingThread


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

        # 准备插件系统字段（仅创建对象，不扫描/加载）
        self.plugin_registry = PluginRegistry()
        self.plugin_lifecycle = None
        self.loaded_plugins: Dict[str, any] = {}

        # 设置最大化窗口
        self.setWindowState(Qt.WindowMaximized)
        self.setMinimumSize(1200, 600)

        # 创建主界面
        self.setup_ui()

        # 在初始化和加载配置之前绑定GUI日志回调，确保启动日志显示到Log panel
        # 注意：后台线程运行时会改为通过线程信号转发，避免跨线程直接操作GUI
        if hasattr(self, "log_panel"):
            logger.set_gui_callback(self.log_panel.append_log)
        else:
            logger.warning("log_panel not initialized, GUI logging callback not set")

        # 应用主题样式
        self.apply_modern_styling()

        # 扫描并加载插件（需要 UI/日志面板已就绪）
        self.initialize_plugin_system()

        # 初始化可用插件到插件管理面板，确保后续链渲染有元数据
        try:
            self.update_plugin_management_ui()
        except Exception as e:
            logger.warning(f"Failed to prepare plugin management UI: {e}")

        # 设置配置协调器到各个面板（必须在加载配置之前）
        self.plugin_management.set_config_coordinator(self.config_coordinator)
        self.config_management.set_config_coordinator(self.config_coordinator)
        self.plugin_config.set_config_coordinator(self.config_coordinator)
        # Set config coordinator for both tabs (via TabsPanel's method)
        self.tabs_panel.set_config_coordinator(self.config_coordinator)

        # 设置信号连接（必须在配置加载之前）
        self.setup_signals()

        # 加载配置
        self.load_configuration()

    def setup_ui(self):
        """设置主界面布局"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 水平分割
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(8)

        # 创建主水平分割器
        main_splitter = QSplitter(Qt.Horizontal)

        # 左侧：配置管理和插件管理区域
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # 右侧：处理面板和日志区域
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        # 设置主分割器比例
        main_splitter.setSizes([700, 500])
        main_splitter.setStretchFactor(0, 0)  # 左侧固定
        main_splitter.setStretchFactor(1, 1)  # 右侧可伸缩

        main_layout.addWidget(main_splitter)

    def create_left_panel(self) -> QWidget:
        """创建左侧配置管理和插件管理面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # 创建左侧垂直分割器
        left_splitter = QSplitter(Qt.Vertical)

        # 顶部：配置管理面板
        self.config_management = ConfigurationManagementPanel(self)
        left_splitter.addWidget(self.config_management)

        # 底部：插件管理和插件配置的水平分割
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

        # 设置左侧分割器比例
        left_splitter.setSizes([100, 1000])  # 配置管理占较小空间，插件区域占更多空间
        left_splitter.setStretchFactor(0, 0)  # 顶部固定（配置管理区域）
        left_splitter.setStretchFactor(1, 1)  # 底部可伸缩（插件区域）

        layout.addWidget(left_splitter)

        return panel

    def create_right_panel(self) -> QWidget:
        """创建右侧四段布局：Tabs、Processing Flow、Command Panel、Log Panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # 创建垂直分割器
        right_splitter = QSplitter(Qt.Vertical)

        # 面板1：TabsPanel（含 margin, QTabWidget/Basic/Advanced/About）
        self.tabs_panel = TabsPanel(self)
        right_splitter.addWidget(self.tabs_panel)

        # 面板2：ProcessingFlowPanel（含 margin, PluginChainVisualizer）
        self.processing_flow_panel = ProcessingFlowPanel(self)
        self.plugin_chain_visualizer = self.processing_flow_panel.visualizer
        right_splitter.addWidget(self.processing_flow_panel)

        # 面板3：命令面板（仅 Format + 进度）
        self.command_panel = CommandPanel(self)
        right_splitter.addWidget(self.command_panel)

        # 面板4：日志面板
        self.log_panel = LogPanel()
        right_splitter.addWidget(self.log_panel)

        # 设置分割器比例（调整初始高度：Tabs/Flow 各自最小高度，底部填充）
        right_splitter.setSizes([220, 120, 160, 999])  # log panel 占据剩余空间
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 1)
        right_splitter.setStretchFactor(2, 1)
        right_splitter.setStretchFactor(3, 1)

        layout.addWidget(right_splitter)

        return panel

    def initialize_plugin_system(self):
        """初始化插件系统（委托 runtime 层）"""
        try:
            self.plugin_lifecycle = runtime_init_plugins(
                self.project_root, self.plugin_registry, self.plugin_config, self.plugin_management
            )
        except Exception as e:
            logger.error(f"Failed to initialize plugin system: {e}")

    def update_plugin_management_ui(self):
        """更新插件管理界面"""
        if not self.plugin_registry:
            logger.warning("Plugin registry not available")
            return

        # 获取可用插件
        plugin_names = self.plugin_registry.list_plugins()
        logger.debug(f"Preparing plugin management UI with {len(plugin_names)} plugins")

        available_plugins = {}
        for name in plugin_names:
            try:
                available_plugins[name] = self.plugin_registry.get_plugin_metadata(name)
            except Exception as e:
                logger.warning(f"Failed to get metadata for plugin {name}: {e}")

        logger.info(f"Plugin management UI updated ({len(available_plugins)} plugins)")

        # 更新插件管理面板
        self.plugin_management.update_available_plugins(available_plugins)

        # 插件链可视化应该只显示用户配置的插件链，而不是所有可用插件
        # 初始时插件链为空，用户需要手动添加插件到链中

    def setup_signals(self):
        """设置信号连接"""
        # 插件管理信号
        if hasattr(self.plugin_management, "pluginSelected"):
            self.plugin_management.pluginSelected.connect(self.on_plugin_selected)

        if hasattr(self.plugin_management, "pluginChainSelected"):
            self.plugin_management.pluginChainSelected.connect(self.on_plugin_chain_selected)

        if hasattr(self.plugin_management, "pluginChainChanged"):
            self.plugin_management.pluginChainChanged.connect(self.on_plugin_chain_changed)

        # 命令面板信号
        if hasattr(self, "command_panel") and hasattr(self.command_panel, "formatRequested"):
            self.command_panel.formatRequested.connect(self.on_format_requested)

        # 插件配置信号
        if hasattr(self.plugin_config, "configChanged"):
            self.plugin_config.configChanged.connect(self.on_plugin_config_changed)
            logger.debug("Plugin config signal connected successfully")
        else:
            logger.warning("Plugin config panel does not have configChanged signal")

        # 日志级别选择变化
        if hasattr(self.log_panel, "levelChanged"):
            self.log_panel.levelChanged.connect(self.on_logging_level_changed)

        # Basic 页面信号连接：保存配置变更到 ConfigCoordinator
        # Note: Browse buttons are already connected in BasicPage.__init__, no need to connect again here
        if hasattr(self, "tabs_panel"):
            self.tabs_panel.tab_basic.edit_input.editingFinished.connect(
                lambda: self.tabs_panel.tab_basic.save_config_to_coordinator()
            )
            self.tabs_panel.tab_basic.edit_output.editingFinished.connect(
                lambda: self.tabs_panel.tab_basic.save_config_to_coordinator()
            )
            self.tabs_panel.tab_basic.check_timestamp.stateChanged.connect(
                lambda: self.tabs_panel.tab_basic.save_config_to_coordinator()
            )

        # Advanced 页面信号连接
        if hasattr(self, "tabs_panel"):
            self.tabs_panel.tab_advanced.btn_open_user_data.clicked.connect(
                self._open_user_data_dir
            )
            self.tabs_panel.tab_advanced.check_debug.stateChanged.connect(
                lambda: self.tabs_panel.tab_advanced.save_config_to_coordinator()
            )

    def on_plugin_selected(self, plugin_name: str):
        """处理插件选择事件"""
        try:
            # 更新插件配置面板，标记为来自可用插件列表（非插件链）
            self.plugin_config.load_plugin_config(plugin_name, is_from_chain=False)

        except Exception as e:
            logger.error(f"Failed to select plugin {plugin_name}: {e}")

    def on_plugin_chain_selected(self, plugin_name: str):
        """处理插件链中的插件选择事件"""
        try:
            # 更新插件配置面板，标记为来自插件链选择
            self.plugin_config.load_plugin_config(plugin_name, is_from_chain=True)

        except Exception as e:
            logger.error(f"Failed to select plugin from chain {plugin_name}: {e}")

    def on_configuration_restored(
        self, unified_config: Dict[str, Any], chain_config: Dict[str, Any]
    ):
        """配置恢复后刷新所有涉及UI"""
        try:
            # 确保可用插件清单已准备好（用于链展示的元数据）
            try:
                self.update_plugin_management_ui()
            except Exception as e:
                logger.warning(f"update_plugin_management_ui failed during restore: {e}")

            # 1. 刷新插件链可视化、管理面板
            plugin_order = chain_config.get("plugins", {}).get("order", [])
            plugin_metadata = chain_config.get("plugin_configs", {})
            # PluginChainVisualizer
            if hasattr(self, "plugin_chain_visualizer"):
                try:
                    self.plugin_chain_visualizer.update_plugin_chain(plugin_order)
                except Exception as e:
                    logger.error(f"UI: plugin_chain_visualizer update failed: {e}")
            # PluginManagementPanel
            if hasattr(self, "plugin_management"):
                try:
                    # 使用面板现有API载入完整链配置
                    self.plugin_management.load_plugin_chain_config(chain_config)
                except Exception as e:
                    logger.error(f"UI: plugin_management load_plugin_chain_config failed: {e}")

            # 2. 插件参数配置面板（需补实现reload_all_plugin_configs）
            if hasattr(self, "plugin_config"):
                try:
                    self.plugin_config.reload_all_plugin_configs(chain_config)
                except Exception as e:
                    logger.error(f"UI: plugin_config reload_all_plugin_configs failed: {e}")

            # 3. 流程面板（需补实现update_processing_flow）
            if hasattr(self, "processing_flow_panel"):
                try:
                    self.processing_flow_panel.update_processing_flow(plugin_order)
                except Exception as e:
                    logger.error(f"UI: processing_flow_panel update_processing_flow failed: {e}")

            # 4. TabsPanel: basic/advanced
            if hasattr(self, "tabs_panel"):
                try:
                    if hasattr(self.tabs_panel, "tab_basic"):
                        self.tabs_panel.tab_basic.load_config_from_coordinator()
                    if hasattr(self.tabs_panel, "tab_advanced"):
                        self.tabs_panel.tab_advanced.load_config_from_coordinator()
                except Exception as e:
                    logger.error(f"UI: tabs_panel reload failed: {e}")

            # 5. LogPanel: logging level
            if hasattr(self, "log_panel"):
                try:
                    logging_level = (unified_config.get("logging") or {}).get("level", "INFO")
                    self.log_panel.set_logging_level(logging_level)
                except Exception as e:
                    logger.error(f"UI: log_panel set_logging_level failed: {e}")

            logger.info("Configuration restored and FULL UI updated")
        except Exception as e:
            logger.error(f"Failed to update UI after configuration restore: {e}")

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

        except Exception as e:
            logger.error(f"Failed to update plugin chain: {e}")

    def on_format_requested(self):
        """处理格式化请求（委托 runtime 组装 full_config）"""
        try:
            from subtitleformatter.runtime.config_materializer import (
                materialize_runtime_config,
            )

            full_config = materialize_runtime_config(
                self.project_root, self.config_coordinator, self.plugin_management
            )

            # GUI 负责最小校验与提示
            paths = full_config.get("paths", {})
            if not paths.get("input_file"):
                QMessageBox.warning(self, "Processing Error", "Please select an input file first.")
                return

            # 根据输出模式进行不同的验证
            output_mode = paths.get("output_mode", "file")
            if output_mode == "directory":
                # 目录输出模式：检查 output_dir
                if not paths.get("output_dir"):
                    QMessageBox.warning(
                        self, "Processing Error", "Please select an output directory."
                    )
                    return
            else:
                # 文件输出模式：检查 output_file
                if not paths.get("output_file"):
                    QMessageBox.warning(self, "Processing Error", "Please select an output file.")
                    return

            self.start_processing_thread(full_config)

        except Exception as e:
            try:
                from subtitleformatter.utils.unified_logger import logger as _ul

                if getattr(_ul, "log_level", "INFO") == "DEBUG":
                    import traceback

                    logger.error(f"Failed to start processing: {e}\n{traceback.format_exc()}")
                else:
                    logger.error(f"Failed to start processing: {e}")
            except Exception:
                logger.error(f"Failed to start processing: {e}")
            QMessageBox.critical(self, "Processing Error", f"Failed to start processing:\n{e}")

    def on_plugin_config_changed(self, plugin_name: str, config: Dict):
        """处理插件配置变更事件"""
        try:
            logger.debug(f"Plugin config changed signal received: {plugin_name}")

            # 更新插件配置
            if plugin_name in self.loaded_plugins:
                self.loaded_plugins[plugin_name].config.update(config)

            logger.info(f"Plugin {plugin_name} configuration updated")

        except Exception as e:
            logger.error(f"Failed to update plugin config: {e}")

    def start_processing_thread(self, config: Dict):
        """启动处理线程"""
        try:
            # 验证必需的组件已初始化
            if not hasattr(self, "command_panel") or self.command_panel is None:
                raise RuntimeError("command_panel not initialized")
            if not hasattr(self, "log_panel") or self.log_panel is None:
                raise RuntimeError("log_panel not initialized")
            if self.plugin_lifecycle is None:
                raise RuntimeError("plugin_lifecycle not initialized")

            self.processing_thread = ProcessingThread(config)

            # 连接信号
            self.processing_thread.progress.connect(
                lambda v, _m: self.command_panel.set_progress(v)
            )
            self.processing_thread.log.connect(self.log_panel.append_log)
            self.processing_thread.finished.connect(self.on_processing_finished)

            # 将统一日志系统的GUI回调重定向到线程信号，避免后台线程直接触碰GUI
            try:
                logger.set_gui_callback(lambda msg: self.processing_thread.log.emit(msg))
                logger.enable_gui(True)
            except Exception:
                pass

            # 启动线程（这是异步操作，不会阻塞UI）
            self.processing_thread.start()

        except Exception as e:
            # 仅在 DEBUG 日志级别下附带 traceback
            try:
                from subtitleformatter.utils.unified_logger import logger as _ul

                if getattr(_ul, "log_level", "INFO") == "DEBUG":
                    import traceback

                    logger.error(
                        f"Failed to start processing thread: {e}\n{traceback.format_exc()}"
                    )
                else:
                    logger.error(f"Failed to start processing thread: {e}")
            except Exception:
                logger.error(f"Failed to start processing thread: {e}")
            QMessageBox.critical(
                self, "Processing Error", f"Failed to start processing thread:\n{e}"
            )

    def on_processing_finished(self, success: bool, message: str):
        """处理完成回调"""
        if success:
            logger.info(" " + message)
        else:
            logger.error(" " + message)
            QMessageBox.critical(self, "Processing Error", message)

        # 处理结束后恢复GUI日志回调到直接写入日志面板（主线程）
        try:
            if hasattr(self, "log_panel"):
                logger.set_gui_callback(self.log_panel.append_log)
        except Exception:
            pass

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

            # 设置日志级别
            log_level = config.get("unified", {}).get("logging", {}).get("level", "INFO")
            logger.set_log_level(log_level)
            # 同步到日志面板下拉框
            try:
                self.log_panel.set_logging_level(log_level)
            except Exception:
                pass

            # 加载配置到 Tabs
            self.tabs_panel.tab_basic.load_config_from_coordinator()
            self.tabs_panel.tab_advanced.load_config_from_coordinator()

            # 创建插件链配置快照用于 Restore Last 功能
            self.config_coordinator.create_chain_snapshot()

            # 确保可用插件已经设置
            if (
                not hasattr(self.plugin_management, "available_plugins")
                or not self.plugin_management.available_plugins
            ):
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

            logger.info(
                "Configuration successfully applied: all systems initialized with loaded settings"
            )

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")

    # ---- Path normalization helpers ----
    def _normalize_path_for_display(self, path_text: str) -> str:
        """Normalize path for display."""
        try:
            import os

            if not path_text:
                return ""
            return os.path.normpath(path_text)
        except Exception:
            return path_text

    def _to_relative(self, p: str | Path) -> str:
        """Convert path to relative path from project root."""
        try:
            import os

            abs_path = Path(p).resolve()
            root = self.project_root.resolve()
            rel = abs_path.relative_to(root)
            return os.path.normpath(str(rel))
        except Exception:
            # If on different drive or outside root, keep absolute normalized
            return self._normalize_path_for_display(str(p))

    def _choose_input(self) -> None:
        """Choose input file and update configuration."""
        start_dir = str((self.project_root / "data" / "input").resolve())
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select input file",
            start_dir,
            "Text/Markdown files (*.txt *.md);;All files (*.*)",
        )
        if not file:
            return

        # Display relative for portability
        self.tabs_panel.tab_basic.edit_input.setText(
            self._normalize_path_for_display(self._to_relative(file))
        )

        # Save to ConfigCoordinator
        file_config = self.config_coordinator.get_file_processing_config()
        file_config["input_file"] = file
        self.config_coordinator.set_file_processing_config(file_config)

        # Auto-suggest output file if empty
        if not self.tabs_panel.tab_basic.edit_output.text().strip():
            in_path = Path(file)
            base = in_path.stem
            out_dir = (self.project_root / "data" / "output").resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            new_out = str(out_dir / f"{base}.txt")
            self.tabs_panel.tab_basic.edit_output.setText(
                self._normalize_path_for_display(self._to_relative(new_out))
            )
            file_config["output_file"] = new_out
            self.config_coordinator.set_file_processing_config(file_config)

    def _choose_output(self) -> None:
        """Choose output file and update configuration."""
        out_dir = (self.project_root / "data" / "output").resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        # Suggest a name based on input if present
        suggested = ""
        in_text = self.tabs_panel.tab_basic.edit_input.text().strip()
        if in_text:
            try:
                in_base = Path(in_text).stem
                suggested = str(out_dir / f"{in_base}.txt")
            except Exception:
                pass

        file, _ = QFileDialog.getSaveFileName(
            self,
            "Select output file",
            suggested or str(out_dir),
            "Text files (*.txt);;All files (*.*)",
        )
        if not file:
            return

        # Display relative for portability
        self.tabs_panel.tab_basic.edit_output.setText(
            self._normalize_path_for_display(self._to_relative(file))
        )

        # Save to ConfigCoordinator
        file_config = self.config_coordinator.get_file_processing_config()
        file_config["output_file"] = file
        self.config_coordinator.set_file_processing_config(file_config)

    def _open_user_data_dir(self) -> None:
        """Open user data directory."""
        try:
            import os

            path = (self.project_root / "data").resolve()
            path.mkdir(parents=True, exist_ok=True)
            os.startfile(str(path))
            # After opening, update instructional with absolute path
            self.tabs_panel.tab_advanced.edit_user_data.setText(str(path))
        except Exception:
            pass

    def on_logging_level_changed(self, level: str):
        """当用户在日志面板中切换日志级别时触发"""
        try:
            # 更新运行时日志级别
            logger.set_log_level(level)

            # 更新并持久化统一配置
            unified_cfg = self.config_coordinator.unified_manager.get_config()
            if "logging" not in unified_cfg:
                unified_cfg["logging"] = {}
            unified_cfg["logging"]["level"] = (level or "INFO").upper()
            self.config_coordinator.unified_manager.set_config(unified_cfg)
            self.config_coordinator.save_all_config()

            # 反馈到日志
            self.log_panel.append_log(f"Logging level set to {unified_cfg['logging']['level']}")
        except Exception as e:
            # 不打断用户操作，仅记录错误
            try:
                logger.error(f"Failed to update logging level: {e}")
            except Exception:
                pass

    def save_configuration(self):
        """保存配置"""
        try:
            # 保存 Basic 页面的配置变更
            if hasattr(self, "tabs_panel"):
                self.tabs_panel.tab_basic.save_config_to_coordinator()

            # 持久化当前工作插件链配置到当前链文件（避免用独立插件配置重建并覆盖）
            try:
                self.config_coordinator.save_working_chain_config()
            except Exception as e:
                logger.error(f"Failed to persist working chain configuration: {e}")

            # 保存所有配置
            self.config_coordinator.save_all_config()

            logger.info("Configuration saved successfully")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 保存配置
        self.save_configuration()

        # 如果有未保存的插件链配置变更，自动保存
        if (
            hasattr(self, "config_coordinator")
            and self.config_coordinator.has_unsaved_chain_changes()
        ):
            try:
                self.config_coordinator.save_working_chain_config()
                logger.info("Auto-saved plugin chain configuration on exit")
            except Exception as e:
                logger.error(f"Failed to auto-save plugin chain configuration: {e}")

        # 停止插件生命周期
        if self.plugin_lifecycle:
            self.plugin_lifecycle.cleanup_all()

        event.accept()


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
