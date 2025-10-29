from __future__ import annotations

from pathlib import Path
from typing import Dict

from subtitleformatter.plugins import PluginLifecycleManager, PluginRegistry
from subtitleformatter.utils.unified_logger import logger


def initialize_plugin_system(
    project_root: Path,
    plugin_registry: PluginRegistry,
    plugin_config_panel,
    plugin_management_panel,
) -> PluginLifecycleManager:
    """Initialize plugin system and update related panels."""
    logger.info(f"Initializing plugin system in {project_root}")

    plugin_dir = project_root / "plugins"
    if plugin_dir.exists():
        plugin_registry.add_plugin_dir(plugin_dir)
        logger.info(f"Added plugin directory: {plugin_dir}")

    logger.info("Scanning plugins...")
    plugin_registry.scan_plugins()

    lifecycle = PluginLifecycleManager(plugin_registry)

    if plugin_config_panel is not None and hasattr(plugin_config_panel, "set_plugin_registry"):
        plugin_config_panel.set_plugin_registry(plugin_registry)

    # Build metadata for management panel
    available: Dict[str, Dict] = {}
    for name in plugin_registry.list_plugins():
        try:
            available[name] = plugin_registry.get_plugin_metadata(name)
        except Exception as e:
            logger.warning(f"Failed to get metadata for plugin {name}: {e}")

    if plugin_management_panel is not None and hasattr(
        plugin_management_panel, "update_available_plugins"
    ):
        plugin_management_panel.update_available_plugins(available)

    logger.info("Plugin system initialized successfully")
    return lifecycle
