"""
Plugin Config Manager for SubtitleFormatter.

Manages individual plugin configurations including:
- Loading plugin configurations on-demand
- Saving plugin configurations immediately
- Supporting per-plugin configuration files
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import tomli_w  # type: ignore
import tomllib  # type: ignore

from ..utils.unified_logger import logger


class PluginConfigManager:
    """Manages individual plugin configurations."""

    def __init__(self, project_root: Path, configs_dir: Path, plugin_registry=None):
        """
        Initialize plugin config manager.

        Args:
            project_root: Project root directory
            configs_dir: Configurations directory (data/configs)
            plugin_registry: Optional plugin registry instance
        """
        self.project_root = project_root
        self.configs_dir = configs_dir
        self.plugins_dir = configs_dir / "plugins"
        self.plugin_registry = plugin_registry

        # Ensure directory exists
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

        # Cache loaded configs to avoid repeated file I/O
        self._config_cache: Dict[str, Dict[str, Any]] = {}

    def load_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Load configuration for a specific plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin configuration dictionary (default config if not found)
        """
        if plugin_name in self._config_cache:
            return self._config_cache[plugin_name].copy()

        config_file = self.plugins_dir / f"{plugin_name}.toml"

        if not config_file.exists():
            logger.debug(f"Plugin config not found for {plugin_name}, using default config")
            # Get default config from plugin metadata
            default_config = self._get_plugin_default_config(plugin_name)
            self._config_cache[plugin_name] = default_config
            return default_config

        try:
            with config_file.open("rb") as f:
                config = tomllib.load(f)

            self._config_cache[plugin_name] = config
            logger.debug(f"Loaded config for plugin {plugin_name}")
            return config

        except Exception as e:
            logger.error(f"Failed to load config for plugin {plugin_name}: {e}")
            # Fallback to default config
            default_config = self._get_plugin_default_config(plugin_name)
            self._config_cache[plugin_name] = default_config
            return default_config

    def _get_plugin_default_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get default configuration for a plugin from its metadata.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Default configuration dictionary
        """
        try:
            if not self.plugin_registry:
                # Import here to avoid circular imports
                from ..plugins.base.plugin_registry import PluginRegistry
                
                # Create and initialize plugin registry
                self.plugin_registry = PluginRegistry()
                self.plugin_registry.add_plugin_dir(self.project_root / "plugins")
                self.plugin_registry.scan_plugins()
            
            # Get plugin metadata
            metadata = self.plugin_registry.get_plugin_metadata(plugin_name)
            if not metadata:
                logger.error(f"Plugin metadata not found for {plugin_name} - this should not happen!")
                raise ValueError(f"Plugin metadata not found for {plugin_name}")
            
            # Extract default values from config_schema
            config_schema = metadata.get("config_schema")
            if not config_schema:
                logger.info(f"Plugin {plugin_name} has no config_schema - no configuration needed")
                return {}
            
            properties = config_schema.get("properties", {})
            default_config = {}
            
            for prop_name, prop_config in properties.items():
                if "default" in prop_config:
                    default_config[prop_name] = prop_config["default"]
            
            if not default_config:
                logger.info(f"Plugin {plugin_name} has no default configuration parameters")
            else:
                logger.debug(f"Extracted default config for {plugin_name}: {default_config}")
            return default_config
            
        except Exception as e:
            logger.error(f"Failed to get default config for plugin {plugin_name}: {e}")
            return {}

    def save_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> Path:
        """
        Save plugin configuration immediately.

        Args:
            plugin_name: Name of the plugin
            config: Configuration dictionary

        Returns:
            Path to saved configuration file
        """
        config_file = self.plugins_dir / f"{plugin_name}.toml"

        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)

            # Only save if config is not empty
            if config:
                with config_file.open("wb") as f:
                    tomli_w.dump(config, f)

                self._config_cache[plugin_name] = config
                logger.debug(f"Saved config for plugin {plugin_name} to {config_file}")

            return config_file

        except Exception as e:
            logger.error(f"Failed to save config for plugin {plugin_name}: {e}")
            raise

    def get_all_plugin_configs(self, plugin_names: list[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get configurations for multiple plugins.

        Args:
            plugin_names: List of plugin names

        Returns:
            Dictionary mapping plugin names to their configurations
        """
        configs = {}
        for plugin_name in plugin_names:
            configs[plugin_name] = self.load_plugin_config(plugin_name)
        return configs

    def clear_cache(self, plugin_name: Optional[str] = None):
        """
        Clear configuration cache.

        Args:
            plugin_name: If provided, clear only this plugin's cache
        """
        if plugin_name is None:
            self._config_cache.clear()
            logger.debug("Cleared all plugin config cache")
        else:
            self._config_cache.pop(plugin_name, None)
            logger.debug(f"Cleared cache for plugin {plugin_name}")

    def config_exists(self, plugin_name: str) -> bool:
        """Check if configuration file exists for a plugin."""
        config_file = self.plugins_dir / f"{plugin_name}.toml"
        return config_file.exists()

    def delete_plugin_config(self, plugin_name: str):
        """Delete plugin configuration file."""
        config_file = self.plugins_dir / f"{plugin_name}.toml"

        if config_file.exists():
            try:
                config_file.unlink()
                self._config_cache.pop(plugin_name, None)
                logger.info(f"Deleted config for plugin {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to delete config for plugin {plugin_name}: {e}")
        else:
            logger.warning(f"Config file not found for plugin {plugin_name}")

