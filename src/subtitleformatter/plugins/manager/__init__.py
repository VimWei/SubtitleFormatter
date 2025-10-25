"""
Plugin management components for SubtitleFormatter.

This package contains the plugin management infrastructure:
- PluginLifecycleManager: Plugin loading, initialization, and cleanup
- DependencyContainer: Dependency injection container
- DependencyInjector: Automatic dependency injection
- PluginConfigManager: Plugin configuration management
- PluginEventSystem: Plugin event system for communication
"""

from .dependency_injection import (
    DependencyContainer,
    DependencyInjector,
    get_container,
    get_injector,
    get_service,
    get_typed_service,
    inject_into,
    inject_into_plugin,
    register_alias,
    register_factory,
    register_singleton,
)
from .plugin_config import PluginConfigManager
from .plugin_events import (
    PluginEvent,
    PluginEventBus,
    PluginEventSystem,
    create_event_bus,
    get_event_system,
)
from .plugin_lifecycle import PluginLifecycleManager

__all__ = [
    "PluginLifecycleManager",
    "DependencyContainer",
    "DependencyInjector",
    "PluginConfigManager",
    "PluginEventSystem",
    "PluginEventBus",
    "PluginEvent",
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
