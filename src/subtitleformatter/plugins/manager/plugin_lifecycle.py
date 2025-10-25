"""
Plugin lifecycle manager for SubtitleFormatter.

This module provides plugin lifecycle management including loading, initialization,
dependency injection, and cleanup.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...utils.unified_logger import logger
from ..base.plugin_base import (
    PluginError,
    PluginInitializationError,
    TextProcessorPlugin,
)
from ..base.plugin_registry import PluginRegistry


class PluginLifecycleManager:
    """
    Plugin lifecycle manager for handling plugin loading, initialization, and cleanup.

    This class manages the complete lifecycle of plugins including dependency
    injection, initialization order, and resource cleanup.
    """

    def __init__(self, registry: PluginRegistry):
        """
        Initialize the lifecycle manager.

        Args:
            registry: Plugin registry instance
        """
        self.registry = registry
        self._instances: Dict[str, TextProcessorPlugin] = {}
        self._initialization_order: List[str] = []
        self._dependencies: Dict[str, Any] = {}

    def register_dependency(self, name: str, dependency: Any) -> None:
        """
        Register a dependency for injection into plugins.

        Args:
            name: Dependency name
            dependency: Dependency object
        """
        self._dependencies[name] = dependency
        logger.debug(f"Registered dependency: {name}")

    def load_plugin(
        self, name: str, config: Optional[Dict[str, Any]] = None
    ) -> TextProcessorPlugin:
        """
        Load and initialize a plugin.

        Args:
            name: Plugin name
            config: Plugin configuration

        Returns:
            Initialized plugin instance

        Raises:
            PluginError: If plugin loading fails
        """
        if name in self._instances:
            logger.warning(f"Plugin '{name}' is already loaded")
            return self._instances[name]

        # Validate dependencies
        missing_deps = self.registry.validate_plugin_dependencies(name)
        if missing_deps:
            raise PluginError(f"Plugin '{name}' has missing dependencies: {missing_deps}")

        # Create plugin instance
        try:
            instance = self.registry.create_plugin_instance(name, config)
            self._instances[name] = instance

            # Inject dependencies
            self._inject_dependencies(instance)

            # Initialize plugin
            instance.initialize()

            # Track initialization order
            if name not in self._initialization_order:
                self._initialization_order.append(name)

            logger.info(f"Plugin '{name}' loaded and initialized successfully")
            return instance

        except Exception as e:
            # Clean up on failure
            if name in self._instances:
                del self._instances[name]
            raise PluginInitializationError(f"Failed to load plugin '{name}': {e}")

    def load_plugins(
        self, plugin_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, TextProcessorPlugin]:
        """
        Load multiple plugins with their configurations.

        Args:
            plugin_configs: Dictionary mapping plugin names to their configurations

        Returns:
            Dictionary mapping plugin names to their instances

        Raises:
            PluginError: If any plugin loading fails
        """
        loaded_plugins = {}

        # First pass: create all instances
        for name, config in plugin_configs.items():
            if not config.get("enabled", True):
                logger.info(f"Skipping disabled plugin: {name}")
                continue

            try:
                instance = self.registry.create_plugin_instance(name, config)
                self._instances[name] = instance
                loaded_plugins[name] = instance
            except Exception as e:
                raise PluginError(f"Failed to create plugin instance '{name}': {e}")

        # Second pass: inject dependencies and initialize
        for name, instance in loaded_plugins.items():
            try:
                self._inject_dependencies(instance)
                instance.initialize()

                if name not in self._initialization_order:
                    self._initialization_order.append(name)

                logger.info(f"Plugin '{name}' initialized successfully")
            except Exception as e:
                # Clean up all loaded plugins on failure
                self.cleanup_all()
                raise PluginInitializationError(f"Failed to initialize plugin '{name}': {e}")

        return loaded_plugins

    def _inject_dependencies(self, plugin: TextProcessorPlugin) -> None:
        """
        Inject dependencies into a plugin.

        Args:
            plugin: Plugin instance to inject dependencies into
        """
        # Inject registered dependencies
        for dep_name, dep_obj in self._dependencies.items():
            plugin.set_dependency(dep_name, dep_obj)

        # Inject other plugin instances as dependencies
        for other_name, other_instance in self._instances.items():
            if other_name != plugin.name:
                plugin.set_dependency(other_name, other_instance)

    def unload_plugin(self, name: str) -> None:
        """
        Unload a plugin and clean up its resources.

        Args:
            name: Plugin name
        """
        if name not in self._instances:
            logger.warning(f"Plugin '{name}' is not loaded")
            return

        try:
            # Cleanup plugin
            plugin = self._instances[name]
            plugin.cleanup()

            # Remove from instances
            del self._instances[name]

            # Remove from initialization order
            if name in self._initialization_order:
                self._initialization_order.remove(name)

            logger.info(f"Plugin '{name}' unloaded successfully")

        except Exception as e:
            logger.error(f"Error unloading plugin '{name}': {e}")

    def cleanup_all(self) -> None:
        """
        Clean up all loaded plugins in reverse initialization order.
        """
        # Cleanup in reverse order
        for name in reversed(self._initialization_order):
            try:
                if name in self._instances:
                    self._instances[name].cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up plugin '{name}': {e}")

        self._instances.clear()
        self._initialization_order.clear()
        logger.info("All plugins cleaned up")

    def get_plugin_instance(self, name: str) -> Optional[TextProcessorPlugin]:
        """
        Get a loaded plugin instance.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None if not loaded
        """
        return self._instances.get(name)

    def is_plugin_loaded(self, name: str) -> bool:
        """
        Check if a plugin is loaded.

        Args:
            name: Plugin name

        Returns:
            True if plugin is loaded, False otherwise
        """
        return name in self._instances

    def list_loaded_plugins(self) -> List[str]:
        """
        List all loaded plugin names.

        Returns:
            List of loaded plugin names
        """
        return list(self._instances.keys())

    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a loaded plugin.

        Args:
            name: Plugin name

        Returns:
            Plugin information dictionary or None if not loaded
        """
        if name not in self._instances:
            return None

        plugin = self._instances[name]
        return plugin.get_info()

    def reload_plugin(
        self, name: str, config: Optional[Dict[str, Any]] = None
    ) -> TextProcessorPlugin:
        """
        Reload a plugin with new configuration.

        Args:
            name: Plugin name
            config: New plugin configuration

        Returns:
            Reloaded plugin instance
        """
        # Unload existing instance
        if name in self._instances:
            self.unload_plugin(name)

        # Load with new configuration
        return self.load_plugin(name, config)

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the dependency graph of loaded plugins.

        Returns:
            Dictionary mapping plugin names to their dependencies
        """
        graph = {}
        for name in self._instances:
            plugin = self._instances[name]
            dependencies = []
            for dep_name in plugin.dependencies:
                if self.is_plugin_loaded(dep_name):
                    dependencies.append(dep_name)
            graph[name] = dependencies
        return graph
