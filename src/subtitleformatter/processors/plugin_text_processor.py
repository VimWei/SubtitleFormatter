"""
Plugin-based text processing coordinator for SubtitleFormatter.

This module provides a new text processor that uses the plugin system
instead of the old hardcoded processing stages.
"""

from pathlib import Path
from typing import Any, Dict, List, Union

from ..plugins import PluginLifecycleManager, PluginRegistry, TextProcessorPlugin
from ..plugins.manager import NewPluginConfigManager
from ..utils.debug_output import DebugOutput
from ..utils.unified_logger import log_debug_info, log_info, log_stats, log_step, logger


class PluginTextProcessor:
    """
    Plugin-based text processing coordinator.

    This class coordinates the text processing workflow using plugins
    instead of hardcoded processing stages.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the plugin-based text processor.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.plugin_registry = None
        self.plugin_lifecycle = None
        self.plugin_config_manager = None
        self.loaded_plugins: List[TextProcessorPlugin] = []

    def process(self) -> None:
        """Execute the complete text processing workflow using plugins."""
        # Initialize processing environment
        log_step("正在初始化插件处理环境")

        # 1. Create debug output and set unified logger debug mode
        debug_config = self.config.get("debug", {})
        output_config = self.config.get("output", {})
        debug_enabled = debug_config.get("enabled", False)

        # Set unified logger debug mode
        logger.set_debug_mode(debug_enabled)

        self.config["debug_output"] = DebugOutput(
            debug=debug_enabled,
            temp_dir=debug_config.get("temp_dir", "temp"),
            add_timestamp=output_config.get("add_timestamp", True),
        )
        debug_output = self.config["debug_output"]

        # 2. Initialize plugin system
        log_step("正在初始化插件系统")
        self._initialize_plugin_system()

        # 3. Load and initialize plugins
        log_step("正在加载插件")
        self._load_plugins()

        # Start file processing workflow
        log_step("开始处理文件")

        # Read input file
        input_file = self.config.get("paths", {}).get("input_file")
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()

        # Log file information using unified logger
        import os

        filename = os.path.basename(input_file)
        log_info(f"已读入文件 {filename}")
        log_debug_info(f"文本长度: {len(text)} 字符")

        # Pass filename information to debug output
        debug_output.show_step("读入文件", text, {"input_file": input_file})

        # Process text through plugin chain
        processed_text = self._process_text_through_plugins(text, debug_output)

        # Save result
        output_file = self.config.get("paths", {}).get("output_file")
        log_step("正在保存结果到文件", output_file)
        with open(output_file, "w", encoding="utf-8") as f:
            # Some plugins may return a list of lines/sentences; normalize to string
            if isinstance(processed_text, list):
                processed_text = "\n".join(map(str, processed_text))
            elif not isinstance(processed_text, str):
                processed_text = str(processed_text)
            f.write(processed_text)

        # Save debug log
        debug_output.save_log()

        log_info(f"处理完成！输出文件：{output_file}")

    def _initialize_plugin_system(self) -> None:
        """Initialize the plugin system components."""
        # Initialize plugin registry
        self.plugin_registry = PluginRegistry()

        # Add plugin directory - automatically scan all subdirectories
        plugin_dir = Path("plugins")
        if plugin_dir.exists():
            self.plugin_registry.add_plugin_dir(plugin_dir)

        # Scan for plugins
        self.plugin_registry.scan_plugins()

        # Initialize plugin lifecycle manager
        self.plugin_lifecycle = PluginLifecycleManager(self.plugin_registry)

        # Initialize plugin configuration manager
        self.plugin_config_manager = NewPluginConfigManager()

        # Load plugin configurations from main config
        self.plugin_config_manager.load_plugin_configs_from_main_config(self.config)

    def _load_plugins(self) -> None:
        """Load and initialize plugins based on configuration."""
        # Get enabled plugins in order
        enabled_plugins = self.plugin_config_manager.get_enabled_plugins()

        if not enabled_plugins:
            log_info("没有启用的插件，使用原始文本")
            return

        log_info(f"启用的插件: {', '.join(enabled_plugins)}")

        # Load each plugin
        for plugin_name in enabled_plugins:
            try:
                # Get plugin configuration
                plugin_config = self.plugin_config_manager.get_plugin_config(plugin_name)

                # Load plugin instance
                plugin_instance = self.plugin_lifecycle.load_plugin(plugin_name, plugin_config)

                if plugin_instance:
                    self.loaded_plugins.append(plugin_instance)
                    log_info(f"已加载插件: {plugin_name}")
                else:
                    log_info(f"插件加载失败: {plugin_name}")

            except Exception as e:
                logger.error(f"加载插件 {plugin_name} 时出错: {e}")
                log_info(f"跳过插件: {plugin_name}")

    def _process_text_through_plugins(self, text: str, debug_output: DebugOutput) -> str:
        """
        Process text through the plugin chain.

        Args:
            text: Input text
            debug_output: Debug output instance

        Returns:
            Processed text
        """
        current_text = text

        for i, plugin in enumerate(self.loaded_plugins):
            plugin_name = plugin.name
            log_step(f"正在执行插件: {plugin_name}")

            try:
                # Process text with plugin
                processed_text = plugin.process(current_text)

                # Log processing statistics
                if isinstance(processed_text, str):
                    log_debug_info(f"插件 {plugin_name} 处理结果:")
                    log_debug_info(f"  - 输入长度: {len(current_text)} 字符")
                    log_debug_info(f"  - 输出长度: {len(processed_text)} 字符")
                    log_debug_info(f"  - 长度变化: {len(processed_text) - len(current_text)} 字符")

                # Show debug output
                debug_output.show_step(f"插件处理: {plugin_name}", processed_text)

                # Update current text
                current_text = processed_text

                log_info(f"插件 {plugin_name} 处理完成")

            except Exception as e:
                logger.error(f"插件 {plugin_name} 处理时出错: {e}")
                log_info(f"插件 {plugin_name} 处理失败，跳过")
                # Continue with previous text if plugin fails
                continue

        return current_text

    def get_plugin_status(self) -> Dict[str, Any]:
        """
        Get status information about loaded plugins.

        Returns:
            Dictionary containing plugin status information
        """
        return {
            "total_plugins": len(self.loaded_plugins),
            "loaded_plugins": [plugin.name for plugin in self.loaded_plugins],
            "plugin_config_summary": self.plugin_config_manager.get_plugin_config_summary(),
        }

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        if self.plugin_lifecycle:
            self.plugin_lifecycle.cleanup_all_plugins()

        self.loaded_plugins.clear()
        log_info("插件资源清理完成")
