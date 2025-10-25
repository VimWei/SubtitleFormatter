"""
Plugin registry for SubtitleFormatter.

This module provides plugin discovery, registration, and management functionality.
It scans plugin directories and maintains a registry of available plugins.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from .plugin_base import PluginError, TextProcessorPlugin


class PluginRegistry:
    """
    Plugin registry for discovering and managing plugins.

    This class handles plugin discovery, registration, and provides access
    to plugin metadata and instances.
    """

    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        """
        Initialize the plugin registry.

        Args:
            plugin_dirs: List of directories to scan for plugins
        """
        self.plugin_dirs = plugin_dirs or []
        self._plugins: Dict[str, Type[TextProcessorPlugin]] = {}
        self._plugin_metadata: Dict[str, Dict[str, Any]] = {}
        self._scanned = False

    def add_plugin_dir(self, plugin_dir: Path) -> None:
        """
        Add a plugin directory to scan.

        Args:
            plugin_dir: Directory path to add
        """
        if plugin_dir not in self.plugin_dirs:
            self.plugin_dirs.append(plugin_dir)
            self._scanned = False  # Mark for rescan

    def scan_plugins(self) -> None:
        """
        Scan all plugin directories for plugins.

        This method discovers plugins by looking for plugin.json files
        and corresponding Python modules.
        """
        self._plugins.clear()
        self._plugin_metadata.clear()

        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue

            self._scan_directory(plugin_dir)

        self._scanned = True

    def _scan_directory(self, plugin_dir: Path) -> None:
        """
        Scan a single directory for plugins.

        Args:
            plugin_dir: Directory to scan
        """
        for item in plugin_dir.iterdir():
            if not item.is_dir():
                continue

            plugin_json_path = item / "plugin.json"
            plugin_py_path = item / "plugin.py"

            if plugin_json_path.exists() and plugin_py_path.exists():
                try:
                    self._register_plugin(item)
                except Exception as e:
                    print(f"Warning: Failed to register plugin in {item}: {e}")

    def _register_plugin(self, plugin_path: Path) -> None:
        """
        Register a single plugin.

        Args:
            plugin_path: Path to plugin directory
        """
        # Load plugin metadata
        plugin_json_path = plugin_path / "plugin.json"
        with plugin_json_path.open("r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Validate required fields
        required_fields = ["name", "version", "description", "author", "class_name"]
        for field in required_fields:
            if field not in metadata:
                raise PluginError(f"Plugin metadata missing required field: {field}")

        plugin_name = metadata["name"]

        # Check for name conflicts
        if plugin_name in self._plugins:
            raise PluginError(f"Plugin name conflict: {plugin_name}")

        # Load plugin class
        plugin_class = self._load_plugin_class(plugin_path, metadata["class_name"])

        # Validate plugin class
        if not issubclass(plugin_class, TextProcessorPlugin):
            raise PluginError(f"Plugin class must inherit from TextProcessorPlugin: {plugin_name}")

        # Register plugin
        self._plugins[plugin_name] = plugin_class
        self._plugin_metadata[plugin_name] = metadata

        print(f"Registered plugin: {plugin_name} v{metadata['version']}")

    def _load_plugin_class(self, plugin_path: Path, class_name: str) -> Type[TextProcessorPlugin]:
        """
        Load plugin class from Python module.

        Args:
            plugin_path: Path to plugin directory
            class_name: Name of the plugin class

        Returns:
            Plugin class
        """
        plugin_py_path = plugin_path / "plugin.py"

        if not plugin_py_path.exists():
            raise PluginError(f"Plugin file not found: {plugin_py_path}")

        # Add plugin directory to Python path temporarily
        import sys

        plugin_parent = plugin_path.parent
        if str(plugin_parent) not in sys.path:
            sys.path.insert(0, str(plugin_parent))

        try:
            # Create module name from path
            module_name = f"{plugin_path.name}.plugin"

            # Import the module
            module = importlib.import_module(module_name)

            # Get the plugin class
            if not hasattr(module, class_name):
                raise PluginError(f"Plugin class '{class_name}' not found in module")

            plugin_class = getattr(module, class_name)
            return plugin_class

        except ImportError as e:
            raise PluginError(f"Failed to import plugin module: {e}")
        finally:
            # Clean up Python path
            if str(plugin_parent) in sys.path:
                sys.path.remove(str(plugin_parent))

    def get_plugin_class(self, name: str) -> Type[TextProcessorPlugin]:
        """
        Get plugin class by name.

        Args:
            name: Plugin name

        Returns:
            Plugin class

        Raises:
            KeyError: If plugin not found
        """
        if not self._scanned:
            self.scan_plugins()

        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found")

        return self._plugins[name]

    def get_plugin_metadata(self, name: str) -> Dict[str, Any]:
        """
        Get plugin metadata by name.

        Args:
            name: Plugin name

        Returns:
            Plugin metadata dictionary

        Raises:
            KeyError: If plugin not found
        """
        if not self._scanned:
            self.scan_plugins()

        if name not in self._plugin_metadata:
            raise KeyError(f"Plugin '{name}' not found")

        return self._plugin_metadata[name]

    def list_plugins(self) -> List[str]:
        """
        List all registered plugin names.

        Returns:
            List of plugin names
        """
        if not self._scanned:
            self.scan_plugins()

        return list(self._plugins.keys())

    def get_plugin_info(self, name: str) -> Dict[str, Any]:
        """
        Get comprehensive plugin information.

        Args:
            name: Plugin name

        Returns:
            Plugin information dictionary
        """
        metadata = self.get_plugin_metadata(name)
        plugin_class = self.get_plugin_class(name)

        return {
            "name": metadata["name"],
            "version": metadata["version"],
            "description": metadata["description"],
            "author": metadata["author"],
            "class_name": metadata["class_name"],
            "dependencies": metadata.get("dependencies", []),
            "config_schema": metadata.get("config_schema"),
            "path": metadata.get("path"),
            "class": plugin_class,
        }

    def is_plugin_available(self, name: str) -> bool:
        """
        Check if a plugin is available.

        Args:
            name: Plugin name

        Returns:
            True if plugin is available, False otherwise
        """
        if not self._scanned:
            self.scan_plugins()

        return name in self._plugins

    def create_plugin_instance(
        self, name: str, config: Optional[Dict[str, Any]] = None
    ) -> TextProcessorPlugin:
        """
        Create a plugin instance.

        Args:
            name: Plugin name
            config: Plugin configuration

        Returns:
            Plugin instance

        Raises:
            KeyError: If plugin not found
            PluginError: If plugin creation fails
        """
        plugin_class = self.get_plugin_class(name)

        try:
            instance = plugin_class(config)
            return instance
        except Exception as e:
            raise PluginError(f"Failed to create plugin instance '{name}': {e}")

    def get_plugin_dependencies(self, name: str) -> List[str]:
        """
        Get plugin dependencies.

        Args:
            name: Plugin name

        Returns:
            List of dependency names
        """
        metadata = self.get_plugin_metadata(name)
        return metadata.get("dependencies", [])

    def validate_plugin_dependencies(self, name: str) -> List[str]:
        """
        Validate plugin dependencies and return missing ones.

        Args:
            name: Plugin name

        Returns:
            List of missing dependency names
        """
        dependencies = self.get_plugin_dependencies(name)
        missing = []

        for dep in dependencies:
            if not self.is_plugin_available(dep):
                missing.append(dep)

        return missing
