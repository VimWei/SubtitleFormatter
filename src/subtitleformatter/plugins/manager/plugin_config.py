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
        self._config_schema: Optional[Dict[str, Any]] = None

    def load_plugin_config(
        self, plugin_name: str, config_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Load configuration for a specific plugin.

        Args:
            plugin_name: Name of the plugin
            config_path: Optional path to configuration file

        Returns:
            Plugin configuration dictionary
        """
        if config_path is None:
            config_path = self.config_dir / f"{plugin_name}.toml"

        if config_path.exists():
            try:
                with config_path.open("rb") as f:
                    import tomllib

                    config = tomllib.load(f)

                self._configs[plugin_name] = config
                logger.debug(f"Loaded configuration for plugin '{plugin_name}'")
                return config

            except Exception as e:
                logger.error(f"Failed to load configuration for plugin '{plugin_name}': {e}")
                return {}
        else:
            logger.warning(
                f"Configuration file not found for plugin '{plugin_name}': {config_path}"
            )
            return {}

    def load_all_plugin_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Load configurations for all plugins in the config directory.

        Returns:
            Dictionary mapping plugin names to their configurations
        """
        self._configs.clear()

        if not self.config_dir.exists():
            logger.warning(f"Configuration directory does not exist: {self.config_dir}")
            return {}

        for config_file in self.config_dir.glob("*.toml"):
            plugin_name = config_file.stem
            self.load_plugin_config(plugin_name, config_file)

        logger.info(f"Loaded configurations for {len(self._configs)} plugins")
        return self._configs

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
            config: Configuration dictionary
        """
        self._configs[plugin_name] = config
        logger.debug(f"Set configuration for plugin '{plugin_name}'")

    def save_plugin_config(self, plugin_name: str, config_path: Optional[Path] = None) -> None:
        """
        Save configuration for a specific plugin to file.

        Args:
            plugin_name: Name of the plugin
            config_path: Optional path to save configuration file
        """
        if plugin_name not in self._configs:
            logger.warning(f"No configuration found for plugin '{plugin_name}'")
            return

        if config_path is None:
            config_path = self.config_dir / f"{plugin_name}.toml"

        # Ensure config directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            config = self._configs[plugin_name]
            with config_path.open("wb") as f:
                tomli_w.dump(config, f)

            logger.info(f"Saved configuration for plugin '{plugin_name}' to {config_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration for plugin '{plugin_name}': {e}")

    def save_all_configs(self) -> None:
        """Save all plugin configurations to files."""
        for plugin_name in self._configs:
            self.save_plugin_config(plugin_name)

    def merge_configs(
        self, base_config: Dict[str, Any], override_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries.

        Args:
            base_config: Base configuration
            override_config: Configuration to merge in

        Returns:
            Merged configuration dictionary
        """
        merged = base_config.copy()

        for key, value in override_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value

        return merged

    def validate_plugin_config(
        self, plugin_name: str, config: Dict[str, Any], schema: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Validate plugin configuration against schema.

        Args:
            plugin_name: Name of the plugin
            config: Configuration to validate
            schema: Optional schema to validate against

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if schema is None:
            schema = self._config_schema

        if schema is None:
            logger.warning(f"No schema available for validation of plugin '{plugin_name}'")
            return errors

        # Basic validation - can be extended with jsonschema library
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in config:
                errors.append(f"Required field '{field}' missing")

        # Type validation
        properties = schema.get("properties", {})
        for field, field_schema in properties.items():
            if field in config:
                expected_type = field_schema.get("type")
                if expected_type and not self._validate_type(config[field], expected_type):
                    errors.append(f"Field '{field}' has wrong type (expected {expected_type})")

        return errors

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """
        Validate that a value matches the expected type.

        Args:
            value: Value to validate
            expected_type: Expected type string

        Returns:
            True if type matches, False otherwise
        """
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        if expected_type not in type_mapping:
            return True  # Unknown type, assume valid

        expected_python_type = type_mapping[expected_type]
        return isinstance(value, expected_python_type)

    def set_default_config(self, plugin_name: str, default_config: Dict[str, Any]) -> None:
        """
        Set default configuration for a plugin.

        Args:
            plugin_name: Name of the plugin
            default_config: Default configuration dictionary
        """
        self._default_configs[plugin_name] = default_config
        logger.debug(f"Set default configuration for plugin '{plugin_name}'")

    def get_default_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get default configuration for a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Default configuration dictionary
        """
        return self._default_configs.get(plugin_name, {})

    def normalize_config(self, plugin_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize configuration by merging with defaults.

        Args:
            plugin_name: Name of the plugin
            config: Configuration to normalize

        Returns:
            Normalized configuration dictionary
        """
        default_config = self.get_default_config(plugin_name)
        return self.merge_configs(default_config, config)

    def load_plugin_order_config(self) -> List[str]:
        """
        Load plugin execution order from configuration.

        Returns:
            List of plugin names in execution order
        """
        main_config_path = self.config_dir / "config_latest.toml"

        if not main_config_path.exists():
            logger.warning(f"Main configuration file not found: {main_config_path}")
            return []

        try:
            with main_config_path.open("rb") as f:
                import tomllib

                config = tomllib.load(f)

            plugins_config = config.get("plugins", {})
            plugin_order = plugins_config.get("order", [])

            logger.info(f"Loaded plugin execution order: {plugin_order}")
            return plugin_order

        except Exception as e:
            logger.error(f"Failed to load plugin order configuration: {e}")
            return []

    def save_plugin_order_config(self, plugin_order: List[str]) -> None:
        """
        Save plugin execution order to configuration.

        Args:
            plugin_order: List of plugin names in execution order
        """
        main_config_path = self.config_dir / "config_latest.toml"

        # Load existing config or create new one
        config = {}
        if main_config_path.exists():
            try:
                with main_config_path.open("rb") as f:
                    import tomllib

                    config = tomllib.load(f)
            except Exception as e:
                logger.error(f"Failed to load existing configuration: {e}")
                config = {}

        # Update plugins section
        if "plugins" not in config:
            config["plugins"] = {}

        config["plugins"]["order"] = plugin_order

        # Save updated config
        try:
            main_config_path.parent.mkdir(parents=True, exist_ok=True)
            with main_config_path.open("wb") as f:
                tomli_w.dump(config, f)

            logger.info(f"Saved plugin execution order: {plugin_order}")

        except Exception as e:
            logger.error(f"Failed to save plugin order configuration: {e}")

    def get_enabled_plugins(self) -> Dict[str, Dict[str, Any]]:
        """
        Get configurations for all enabled plugins.

        Returns:
            Dictionary mapping plugin names to their configurations
        """
        enabled_plugins = {}

        for plugin_name, config in self._configs.items():
            if config.get("enabled", True):
                enabled_plugins[plugin_name] = config

        return enabled_plugins

    def list_plugin_configs(self) -> List[str]:
        """
        List all plugin names with configurations.

        Returns:
            List of plugin names
        """
        return list(self._configs.keys())

    def remove_plugin_config(self, plugin_name: str) -> None:
        """
        Remove configuration for a plugin.

        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name in self._configs:
            del self._configs[plugin_name]
            logger.debug(f"Removed configuration for plugin '{plugin_name}'")

    def clear_all_configs(self) -> None:
        """Clear all plugin configurations."""
        self._configs.clear()
        logger.debug("Cleared all plugin configurations")
