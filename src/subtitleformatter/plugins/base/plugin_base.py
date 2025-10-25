"""
TextProcessorPlugin base class for SubtitleFormatter plugins.

This module defines the base class that all text processing plugins must inherit from.
It provides a unified interface for plugin development and ensures type safety.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ...utils.unified_logger import logger


class TextProcessorPlugin(ABC):
    """
    Base class for all text processing plugins.
    
    This class defines the standard interface that all plugins must implement.
    It provides dependency injection, configuration management, and lifecycle hooks.
    
    Attributes:
        name: Plugin name (must be unique)
        version: Plugin version
        description: Plugin description
        author: Plugin author
        dependencies: List of required dependencies
        config_schema: JSON schema for plugin configuration validation
    """
    
    # Plugin metadata - must be defined by subclasses
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = []
    config_schema: Optional[Dict[str, Any]] = None
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin.
        
        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self._initialized = False
        self._dependencies: Dict[str, Any] = {}
        
        # Validate configuration if schema is provided
        if self.config_schema:
            self._validate_config()
    
    @abstractmethod
    def process(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Process the input text.
        
        This is the main processing method that all plugins must implement.
        
        Args:
            text: Input text (string or list of strings)
            
        Returns:
            Processed text (same type as input)
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement the process method")
    
    def initialize(self) -> None:
        """
        Initialize the plugin.
        
        This method is called after all dependencies are injected.
        Override this method to perform any initialization that requires dependencies.
        """
        self._initialized = True
        logger.debug(f"Plugin {self.name} initialized")
    
    def cleanup(self) -> None:
        """
        Cleanup plugin resources.
        
        This method is called when the plugin is being unloaded.
        Override this method to clean up any resources.
        """
        self._initialized = False
        logger.debug(f"Plugin {self.name} cleaned up")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information.
        
        Returns:
            Dictionary containing plugin metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies,
            "initialized": self._initialized,
            "config": self.config
        }
    
    def set_dependency(self, name: str, dependency: Any) -> None:
        """
        Set a dependency for this plugin.
        
        Args:
            name: Dependency name
            dependency: Dependency object
        """
        self._dependencies[name] = dependency
        logger.debug(f"Plugin {self.name} received dependency: {name}")
    
    def get_dependency(self, name: str) -> Any:
        """
        Get a dependency by name.
        
        Args:
            name: Dependency name
            
        Returns:
            Dependency object
            
        Raises:
            KeyError: If dependency not found
        """
        if name not in self._dependencies:
            raise KeyError(f"Dependency '{name}' not found for plugin '{self.name}'")
        return self._dependencies[name]
    
    def has_dependency(self, name: str) -> bool:
        """
        Check if a dependency exists.
        
        Args:
            name: Dependency name
            
        Returns:
            True if dependency exists, False otherwise
        """
        return name in self._dependencies
    
    def _validate_config(self) -> None:
        """
        Validate plugin configuration against schema.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.config_schema:
            return
            
        # Basic validation - can be extended with jsonschema library
        required_fields = self.config_schema.get("required", [])
        for field in required_fields:
            if field not in self.config:
                raise PluginConfigurationError(f"Required configuration field '{field}' missing for plugin '{self.name}'")
    
    def __str__(self) -> str:
        """String representation of the plugin."""
        return f"{self.name} v{self.version} by {self.author}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the plugin."""
        return f"TextProcessorPlugin(name='{self.name}', version='{self.version}', initialized={self._initialized})"


class PluginError(Exception):
    """Base exception class for plugin-related errors."""
    pass


class PluginInitializationError(PluginError):
    """Raised when plugin initialization fails."""
    pass


class PluginConfigurationError(PluginError):
    """Raised when plugin configuration is invalid."""
    pass


class PluginDependencyError(PluginError):
    """Raised when plugin dependency is missing or invalid."""
    pass
