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
            self._apply_default_values()

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
    
    def process_batch(self, texts: List[str], batch_size: int = 100) -> List[str]:
        """
        Process a batch of texts efficiently.
        
        This method provides optimized batch processing for large datasets.
        Plugins can override this method to implement custom batch processing logic.
        
        Args:
            texts: List of texts to process
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of processed texts
        """
        if not texts:
            return []
        
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = self.process(batch)
            results.extend(batch_results)
        
        return results

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
    
    def is_initialized(self) -> bool:
        """
        Check if plugin is initialized.
        
        Returns:
            True if plugin is initialized, False otherwise
        """
        return self._initialized

    def get_config(self) -> Dict[str, Any]:
        """Get current plugin configuration."""
        return self.config.copy()
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Set plugin configuration."""
        self.config = config.copy()
        if self.config_schema:
            self._validate_config()
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration data."""
        if not self.config_schema:
            return True
        
        required_fields = self.config_schema.get("required", [])
        for field in required_fields:
            if field not in config:
                return False
        
        return True

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
            "config": self.config,
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

    def _apply_default_values(self) -> None:
        """Apply default values from schema."""
        if not self.config_schema:
            return
        
        default_values = self.config_schema.get("default_values", {})
        for field, default_value in default_values.items():
            if field not in self.config:
                self.config[field] = default_value
    
    def _validate_config(self) -> None:
        """
        Validate plugin configuration against schema.

        Raises:
            PluginConfigurationError: If configuration is invalid
        """
        if not self.config_schema:
            return

        errors = []
        
        # 验证必需字段
        required_fields = self.config_schema.get("required", [])
        for field in required_fields:
            if field not in self.config:
                errors.append(f"Required field '{field}' is missing")
        
        # 验证字段类型
        field_types = self.config_schema.get("field_types", {})
        for field, expected_type in field_types.items():
            if field in self.config:
                if not isinstance(self.config[field], expected_type):
                    errors.append(
                        f"Field '{field}' must be of type {expected_type.__name__}, "
                        f"got {type(self.config[field]).__name__}"
                    )
        
        # 验证字段值
        field_validators = self.config_schema.get("field_validators", {})
        for field, validator in field_validators.items():
            if field in self.config:
                try:
                    result = validator(self.config[field])
                    if result is False:
                        errors.append(f"Field '{field}' validation failed: value '{self.config[field]}' is invalid")
                except Exception as e:
                    errors.append(f"Field '{field}' validation failed: {e}")
        
        # 检查未知字段
        allowed_fields = set(required_fields)
        allowed_fields.update(self.config_schema.get("optional", {}).keys())
        allowed_fields.update(field_types.keys())
        
        for field in self.config.keys():
            if field not in allowed_fields:
                errors.append(f"Unknown field '{field}' is not allowed")
        
        if errors:
            raise PluginConfigurationError(
                f"Configuration validation failed: {'; '.join(errors)}",
                plugin_name=self.name,
                invalid_fields=[field for field in self.config.keys() if field not in allowed_fields]
            )

    def __str__(self) -> str:
        """String representation of the plugin."""
        return f"{self.name} v{self.version} by {self.author}"

    def __repr__(self) -> str:
        """Detailed string representation of the plugin."""
        return f"TextProcessorPlugin(name='{self.name}', version='{self.version}', initialized={self._initialized})"


class PluginError(Exception):
    """Base exception class for plugin-related errors."""
    
    def __init__(self, message: str, plugin_name: str = None, error_code: str = None):
        super().__init__(message)
        self.plugin_name = plugin_name
        self.error_code = error_code
    
    def __str__(self):
        base_msg = super().__str__()
        if self.plugin_name:
            base_msg = f"[{self.plugin_name}] {base_msg}"
        if self.error_code:
            base_msg = f"{base_msg} (Error Code: {self.error_code})"
        return base_msg


class PluginInitializationError(PluginError):
    """Raised when plugin initialization fails."""
    
    def __init__(self, message: str, plugin_name: str = None, cause: Exception = None):
        super().__init__(message, plugin_name, "INIT_ERROR")
        self.cause = cause


class PluginConfigurationError(PluginError):
    """Raised when plugin configuration is invalid."""
    
    def __init__(self, message: str, plugin_name: str = None, invalid_fields: list = None):
        super().__init__(message, plugin_name, "CONFIG_ERROR")
        self.invalid_fields = invalid_fields or []


class PluginDependencyError(PluginError):
    """Raised when plugin dependency is missing or invalid."""
    
    def __init__(self, message: str, plugin_name: str = None, missing_dependencies: list = None):
        super().__init__(message, plugin_name, "DEPENDENCY_ERROR")
        self.missing_dependencies = missing_dependencies or []


class PluginProcessingError(PluginError):
    """Raised when plugin processing fails."""
    
    def __init__(self, message: str, plugin_name: str = None, input_data: str = None, cause: Exception = None):
        super().__init__(message, plugin_name, "PROCESSING_ERROR")
        self.input_data = input_data
        self.cause = cause
