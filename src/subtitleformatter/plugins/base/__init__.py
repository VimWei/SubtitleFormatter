"""
Plugin base classes and interfaces for SubtitleFormatter.

This package contains the core plugin infrastructure:
- TextProcessorPlugin: Base class for all text processing plugins
- PluginRegistry: Plugin discovery and registration mechanism
"""

from .plugin_base import TextProcessorPlugin
from .plugin_registry import PluginRegistry

__all__ = ["TextProcessorPlugin", "PluginRegistry"]
