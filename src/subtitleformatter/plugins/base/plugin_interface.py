"""
Plugin interface specifications for SubtitleFormatter.

This module defines the standard interfaces and protocols that plugins
must implement, ensuring type safety and consistent behavior.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, Union, runtime_checkable

from .plugin_base import TextProcessorPlugin


@runtime_checkable
class TextProcessorProtocol(Protocol):
    """
    Protocol defining the interface for text processing plugins.

    This protocol ensures that all text processing plugins implement
    the required methods for text transformation.
    """

    def process(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Process the input text.

        Args:
            text: Input text (string or list of strings)

        Returns:
            Processed text (same type as input)
        """
        ...


@runtime_checkable
class ConfigurableProtocol(Protocol):
    """
    Protocol defining the interface for configurable plugins.

    This protocol ensures that plugins can be configured with
    external configuration data.
    """

    def get_config(self) -> Dict[str, Any]:
        """Get current plugin configuration."""
        ...

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set plugin configuration."""
        ...

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration data."""
        ...


@runtime_checkable
class DependencyAwareProtocol(Protocol):
    """
    Protocol defining the interface for plugins that use dependencies.

    This protocol ensures that plugins can receive and use
    injected dependencies.
    """

    def set_dependency(self, name: str, dependency: Any) -> None:
        """Set a dependency for this plugin."""
        ...

    def get_dependency(self, name: str) -> Any:
        """Get a dependency by name."""
        ...

    def has_dependency(self, name: str) -> bool:
        """Check if a dependency exists."""
        ...


@runtime_checkable
class LifecycleProtocol(Protocol):
    """
    Protocol defining the interface for plugins with lifecycle management.

    This protocol ensures that plugins can be properly initialized
    and cleaned up.
    """

    def initialize(self) -> None:
        """Initialize the plugin."""
        ...

    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        ...

    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        ...


@runtime_checkable
class MetadataProtocol(Protocol):
    """
    Protocol defining the interface for plugins with metadata.

    This protocol ensures that plugins provide information
    about themselves.
    """

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        ...

    @property
    def name(self) -> str:
        """Plugin name."""
        ...

    @property
    def version(self) -> str:
        """Plugin version."""
        ...

    @property
    def description(self) -> str:
        """Plugin description."""
        ...

    @property
    def author(self) -> str:
        """Plugin author."""
        ...


class TextProcessorInterface(ABC):
    """
    Abstract base class defining the complete text processor interface.

    This class combines all protocols into a single interface that
    plugins can implement for full functionality.
    """

    # Plugin metadata - must be defined by subclasses
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = []
    config_schema: Optional[Dict[str, Any]] = None

    @abstractmethod
    def process(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Process the input text.

        This is the main processing method that all plugins must implement.

        Args:
            text: Input text (string or list of strings)

        Returns:
            Processed text (same type as input)
        """
        raise NotImplementedError("Subclasses must implement the process method")

    def get_config(self) -> Dict[str, Any]:
        """Get current plugin configuration."""
        return getattr(self, "config", {})

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set plugin configuration."""
        self.config = config
        if self.config_schema:
            self.validate_config(config)

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration data."""
        if not self.config_schema:
            return True

        required_fields = self.config_schema.get("required", [])
        for field in required_fields:
            if field not in config:
                return False

        return True

    def set_dependency(self, name: str, dependency: Any) -> None:
        """Set a dependency for this plugin."""
        if not hasattr(self, "_dependencies"):
            self._dependencies = {}
        self._dependencies[name] = dependency

    def get_dependency(self, name: str) -> Any:
        """Get a dependency by name."""
        if not hasattr(self, "_dependencies"):
            raise KeyError(f"Dependency '{name}' not found")
        return self._dependencies[name]

    def has_dependency(self, name: str) -> bool:
        """Check if a dependency exists."""
        return hasattr(self, "_dependencies") and name in self._dependencies

    def initialize(self) -> None:
        """Initialize the plugin."""
        self._initialized = True

    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        self._initialized = False

    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        return getattr(self, "_initialized", False)

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies,
            "initialized": self.is_initialized(),
            "config": self.get_config(),
        }


class PluginTypeValidator:
    """
    Validator for ensuring plugins implement required interfaces.

    This class provides methods to validate that plugin classes
    and instances conform to the required protocols.
    """

    @staticmethod
    def validate_plugin_class(plugin_class: type) -> List[str]:
        """
        Validate that a plugin class implements required interfaces.

        Args:
            plugin_class: Plugin class to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check if it's a subclass of TextProcessorPlugin
        if not issubclass(plugin_class, TextProcessorPlugin):
            errors.append("Plugin class must inherit from TextProcessorPlugin")

        # Check required attributes
        required_attrs = ["name", "version", "description", "author"]
        for attr in required_attrs:
            if not hasattr(plugin_class, attr):
                errors.append(f"Plugin class must have '{attr}' attribute")

        # Check required methods
        required_methods = ["process"]
        for method in required_methods:
            if not hasattr(plugin_class, method):
                errors.append(f"Plugin class must implement '{method}' method")

        return errors

    @staticmethod
    def validate_plugin_instance(plugin_instance: Any) -> List[str]:
        """
        Validate that a plugin instance conforms to protocols.

        Args:
            plugin_instance: Plugin instance to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check protocols
        protocols = [
            TextProcessorProtocol,
            ConfigurableProtocol,
            DependencyAwareProtocol,
            LifecycleProtocol,
            MetadataProtocol,
        ]

        for protocol in protocols:
            if not isinstance(plugin_instance, protocol):
                errors.append(f"Plugin instance must implement {protocol.__name__}")

        return errors

    @staticmethod
    def is_valid_plugin_class(plugin_class: type) -> bool:
        """Check if a plugin class is valid."""
        return len(PluginTypeValidator.validate_plugin_class(plugin_class)) == 0

    @staticmethod
    def is_valid_plugin_instance(plugin_instance: Any) -> bool:
        """Check if a plugin instance is valid."""
        return len(PluginTypeValidator.validate_plugin_instance(plugin_instance)) == 0


# Type aliases for better code readability
PluginClass = type[TextProcessorPlugin]
PluginInstance = TextProcessorPlugin
PluginConfig = Dict[str, Any]
PluginMetadata = Dict[str, Any]
PluginDependencies = List[str]
