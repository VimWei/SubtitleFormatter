"""
Plugin base classes and interfaces for SubtitleFormatter.

This package provides the foundational classes and interfaces that all
plugins must implement, ensuring consistent behavior and type safety.
"""

from .plugin_base import (
    PluginConfigurationError,
    PluginDependencyError,
    PluginError,
    PluginInitializationError,
    PluginProcessingError,
    TextProcessorPlugin,
)
from .plugin_config import (
    PluginConfigManager,
    PluginConfigSchema,
    StandardPluginConfigs,
    get_config_manager,
    register_standard_schemas,
)
from .plugin_interface import (
    ConfigurableProtocol,
    DependencyAwareProtocol,
    LifecycleProtocol,
    MetadataProtocol,
    PluginClass,
    PluginConfig,
    PluginDependencies,
    PluginInstance,
    PluginMetadata,
    PluginTypeValidator,
    TextProcessorInterface,
    TextProcessorProtocol,
)
from .plugin_registry import PluginRegistry

__all__ = [
    # Base plugin class
    "TextProcessorPlugin",
    # Plugin interfaces
    "TextProcessorInterface",
    "TextProcessorProtocol",
    "ConfigurableProtocol",
    "DependencyAwareProtocol",
    "LifecycleProtocol",
    "MetadataProtocol",
    # Configuration management
    "PluginConfigManager",
    "PluginConfigSchema",
    "StandardPluginConfigs",
    "get_config_manager",
    "register_standard_schemas",
    # Type validation
    "PluginTypeValidator",
    # Type aliases
    "PluginClass",
    "PluginInstance",
    "PluginConfig",
    "PluginMetadata",
    "PluginDependencies",
    # Registry
    "PluginRegistry",
    # Exception classes
    "PluginError",
    "PluginInitializationError",
    "PluginConfigurationError",
    "PluginDependencyError",
    "PluginProcessingError",
]
