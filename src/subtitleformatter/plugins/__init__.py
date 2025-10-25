"""
Plugin system for SubtitleFormatter.

This package provides a complete plugin architecture for SubtitleFormatter,
including plugin discovery, registration, lifecycle management, and dependency injection.

Core Components:
- TextProcessorPlugin: Base class for all plugins
- PluginRegistry: Plugin discovery and registration
- PluginLifecycleManager: Plugin loading and initialization
- DependencyContainer: Dependency injection system
- PluginConfigManager: Plugin configuration management
- PluginEventSystem: Plugin event system for communication

Usage:
    from subtitleformatter.plugins import PluginRegistry, PluginLifecycleManager

    # Create registry and scan for plugins
    registry = PluginRegistry()
    registry.add_plugin_dir(Path("plugins"))
    registry.scan_plugins()

    # Create lifecycle manager
    lifecycle = PluginLifecycleManager(registry)

    # Load plugins
    plugins = lifecycle.load_plugins({
        "builtin/text_cleaning": {"enabled": True},
        "builtin/punctuation_adder": {"enabled": True}
    })
"""

from .base import PluginRegistry, TextProcessorPlugin
from .base.plugin_base import (
    PluginConfigurationError,
    PluginDependencyError,
    PluginError,
    PluginInitializationError,
)
from .manager import (
    DependencyContainer,
    DependencyInjector,
    PluginConfigManager,
    PluginEvent,
    PluginEventBus,
    PluginEventSystem,
    PluginLifecycleManager,
    create_event_bus,
    get_container,
    get_event_system,
    get_injector,
    get_service,
    get_typed_service,
    inject_into,
    inject_into_plugin,
    register_alias,
    register_factory,
    register_singleton,
)

__all__ = [
    # Base classes
    "TextProcessorPlugin",
    "PluginRegistry",
    "PluginLifecycleManager",
    # Error classes
    "PluginError",
    "PluginInitializationError",
    "PluginConfigurationError",
    "PluginDependencyError",
    # Configuration and events
    "PluginConfigManager",
    "PluginEventSystem",
    "PluginEventBus",
    "PluginEvent",
    # Dependency injection
    "DependencyContainer",
    "DependencyInjector",
    # Convenience functions
    "get_container",
    "get_injector",
    "get_service",
    "get_typed_service",
    "inject_into",
    "inject_into_plugin",
    "register_alias",
    "register_factory",
    "register_singleton",
    "create_event_bus",
    "get_event_system",
]
