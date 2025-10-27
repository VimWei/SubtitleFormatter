"""Configuration package for SubtitleFormatter.

Exposes `load_config` to consumers.
"""

from .loader import create_config_from_args, load_config
from .config_coordinator import ConfigCoordinator
from .plugin_chain_manager import PluginChainManager
from .plugin_config_manager import PluginConfigManager
from .unified_config_manager import UnifiedConfigManager

__all__ = [
    "load_config",
    "create_config_from_args",
    "ConfigCoordinator",
    "PluginChainManager",
    "PluginConfigManager",
    "UnifiedConfigManager",
]
