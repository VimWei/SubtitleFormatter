"""
Plugin configuration manager for SubtitleFormatter.

This module provides configuration management for plugins, including
loading, validation, and merging of plugin configurations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import tomli_w  # type: ignore

from ...utils.unified_logger import logger


class PluginConfigManager:
    """
    Plugin configuration manager for handling plugin configurations.

    This class manages plugin configurations including loading from files,
    validation, merging, and providing configuration to plugins.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the plugin configuration manager.

        Args:
            config_dir: Directory containing plugin configuration files
        """
        self.config_dir = config_dir or Path("data/configs")
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._default_configs: Dict[str, Dict[str, Any]] = {}
        self._plugin_order: List[str] = []

    def load_plugin_config(
        self, plugin_name: str, config_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Load configuration for a specific plugin.

        Args:
            plugin_name: Name of the plugin
            config_path: Optional path to plugin-specific config file

        Returns:
            Plugin configuration dictionary
        """
        if config_path and config_path.exists():
            return self._load_from_file(config_path)
        
        # Try to load from main config
        if plugin_name in self._configs:
            return self._configs[plugin_name]
        
        # Return default configuration
        return self._default_configs.get(plugin_name, {})

    def load_plugin_configs_from_main_config(self, main_config: Dict[str, Any]) -> None:
        """
        Load plugin configurations from the main configuration.

        Args:
            main_config: Main configuration dictionary
        """
        # Load plugin order
        self._plugin_order = main_config.get("plugins", {}).get("order", [])
        
        # Load individual plugin configurations
        plugins_config = main_config.get("plugins", {})
        for key, value in plugins_config.items():
            if key != "order" and isinstance(value, dict):
                self._configs[key] = value

    def get_plugin_order(self) -> List[str]:
        """
        Get the plugin execution order.

        Returns:
            List of plugin names in execution order
        """
        return self._plugin_order.copy()

    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin configuration dictionary
        """
        return self._configs.get(plugin_name, {})

    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> None:
        """
        Set configuration for a specific plugin.

        Args:
            plugin_name: Name of the plugin
            config: Plugin configuration dictionary
        """
        self._configs[plugin_name] = config

    def set_plugin_order(self, order: List[str]) -> None:
        """
        Set the plugin execution order.

        Args:
            order: List of plugin names in execution order
        """
        self._plugin_order = order

    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """
        Check if a plugin is enabled.

        Args:
            plugin_name: Name of the plugin

        Returns:
            True if plugin is enabled, False otherwise
        """
        config = self.get_plugin_config(plugin_name)
        return config.get("enabled", True)

    def get_enabled_plugins(self) -> List[str]:
        """
        Get list of enabled plugins in execution order.

        Returns:
            List of enabled plugin names
        """
        enabled_plugins = []
        for plugin_name in self._plugin_order:
            if self.is_plugin_enabled(plugin_name):
                enabled_plugins.append(plugin_name)
        return enabled_plugins

    def validate_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> List[str]:
        """
        Validate plugin configuration against its schema.

        Args:
            plugin_name: Name of the plugin
            config: Plugin configuration to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Basic validation
        if not isinstance(config, dict):
            errors.append(f"Plugin config must be a dictionary")
            return errors
        
        # Check for required fields
        if "enabled" not in config:
            errors.append(f"Plugin config missing 'enabled' field")
        
        # Type validation for common fields
        if "enabled" in config and not isinstance(config["enabled"], bool):
            errors.append(f"Plugin 'enabled' field must be boolean")
        
        # Plugin-specific validation can be added here
        # For now, we'll do basic validation
        
        return errors

    def save_plugin_configs_to_main_config(self, main_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save plugin configurations to main configuration.

        Args:
            main_config: Main configuration dictionary

        Returns:
            Updated main configuration dictionary
        """
        # Ensure plugins section exists
        if "plugins" not in main_config:
            main_config["plugins"] = {}
        
        # Set plugin order
        main_config["plugins"]["order"] = self._plugin_order
        
        # Set individual plugin configurations
        for plugin_name, config in self._configs.items():
            main_config["plugins"][plugin_name] = config
        
        return main_config

    def export_plugin_config(self, plugin_name: str, output_path: Path) -> None:
        """
        Export plugin configuration to a file.

        Args:
            plugin_name: Name of the plugin
            output_path: Path to output file
        """
        config = self.get_plugin_config(plugin_name)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write configuration file
        if output_path.suffix.lower() == ".json":
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        elif output_path.suffix.lower() == ".toml":
            with output_path.open("wb") as f:
                tomli_w.dump({plugin_name: config}, f)
        else:
            raise ValueError(f"Unsupported file format: {output_path.suffix}")

    def import_plugin_config(self, plugin_name: str, input_path: Path) -> Dict[str, Any]:
        """
        Import plugin configuration from a file.

        Args:
            plugin_name: Name of the plugin
            input_path: Path to input file

        Returns:
            Imported plugin configuration
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {input_path}")
        
        config = self._load_from_file(input_path)
        
        # Validate configuration
        errors = self.validate_plugin_config(plugin_name, config)
        if errors:
            raise ValueError(f"Invalid plugin configuration: {', '.join(errors)}")
        
        # Set configuration
        self.set_plugin_config(plugin_name, config)
        
        return config

    def _load_from_file(self, config_path: Path) -> Dict[str, Any]:
        """
        Load configuration from a file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with config_path.open("r", encoding="utf-8") as f:
            if config_path.suffix.lower() == ".json":
                return json.load(f)
            else:
                # For other formats, we could add support here
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")

    def get_plugin_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all plugin configurations.

        Returns:
            Summary dictionary containing plugin status and configuration
        """
        summary = {
            "plugin_order": self._plugin_order,
            "enabled_plugins": self.get_enabled_plugins(),
            "plugin_configs": {}
        }
        
        for plugin_name in self._plugin_order:
            config = self.get_plugin_config(plugin_name)
            summary["plugin_configs"][plugin_name] = {
                "enabled": self.is_plugin_enabled(plugin_name),
                "config_keys": list(config.keys())
            }
        
        return summary

    def reset_plugin_config(self, plugin_name: str) -> None:
        """
        Reset plugin configuration to defaults.

        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name in self._configs:
            del self._configs[plugin_name]
        
        logger.info(f"Reset configuration for plugin: {plugin_name}")

    def reset_all_plugin_configs(self) -> None:
        """Reset all plugin configurations to defaults."""
        self._configs.clear()
        self._plugin_order.clear()
        logger.info("Reset all plugin configurations to defaults")
