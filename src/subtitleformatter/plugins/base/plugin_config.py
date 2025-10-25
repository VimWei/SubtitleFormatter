"""
Plugin configuration standards for SubtitleFormatter.

This module defines the standard configuration format and validation
for plugins, ensuring consistent configuration management.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# 避免循环导入，在需要时动态导入


class PluginConfigSchema:
    """
    Plugin configuration schema definition.
    
    This class defines the structure and validation rules for plugin
    configuration data.
    """
    
    def __init__(
        self,
        required_fields: Optional[List[str]] = None,
        optional_fields: Optional[Dict[str, Any]] = None,
        field_types: Optional[Dict[str, type]] = None,
        field_validators: Optional[Dict[str, callable]] = None,
        default_values: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the configuration schema.
        
        Args:
            required_fields: List of required configuration fields
            optional_fields: Dictionary of optional fields with default values
            field_types: Dictionary mapping field names to expected types
            field_validators: Dictionary mapping field names to validation functions
            default_values: Dictionary of default values for fields
        """
        self.required_fields = required_fields or []
        self.optional_fields = optional_fields or {}
        self.field_types = field_types or {}
        self.field_validators = field_validators or {}
        self.default_values = default_values or {}
    
    def validate(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in config:
                errors.append(f"Required field '{field}' is missing")
        
        # Check field types
        for field, expected_type in self.field_types.items():
            if field in config:
                if not isinstance(config[field], expected_type):
                    errors.append(
                        f"Field '{field}' must be of type {expected_type.__name__}, "
                        f"got {type(config[field]).__name__}"
                    )
        
        # Run custom validators
        for field, validator in self.field_validators.items():
            if field in config:
                try:
                    validator(config[field])
                except Exception as e:
                    errors.append(f"Field '{field}' validation failed: {e}")
        
        return errors
    
    def apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values to configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with defaults applied
        """
        result = config.copy()
        
        # Apply defaults for optional fields
        for field, default_value in self.default_values.items():
            if field not in result:
                result[field] = default_value
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary representation."""
        return {
            "required_fields": self.required_fields,
            "optional_fields": self.optional_fields,
            "field_types": {k: v.__name__ for k, v in self.field_types.items()},
            "field_validators": list(self.field_validators.keys()),
            "default_values": self.default_values,
        }


class PluginConfigManager:
    """
    Manager for plugin configuration loading, validation, and storage.
    
    This class handles the loading and validation of plugin configurations
    from various sources (files, dictionaries, etc.).
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self._schemas: Dict[str, PluginConfigSchema] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}
    
    def register_schema(self, plugin_name: str, schema: PluginConfigSchema) -> None:
        """
        Register a configuration schema for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            schema: Configuration schema
        """
        self._schemas[plugin_name] = schema
    
    def load_config_from_file(self, config_path: Path) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If configuration file is invalid JSON
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with config_path.open("r", encoding="utf-8") as f:
            if config_path.suffix.lower() == ".json":
                return json.load(f)
            else:
                # For other formats, we could add support here
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
    
    def load_config_from_dict(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load configuration from a dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Configuration dictionary
        """
        return config_dict.copy()
    
    def validate_config(self, plugin_name: str, config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration against plugin schema.
        
        Args:
            plugin_name: Name of the plugin
            config: Configuration to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        if plugin_name not in self._schemas:
            return []  # No schema registered, assume valid
        
        schema = self._schemas[plugin_name]
        return schema.validate(config)
    
    def apply_defaults(self, plugin_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values to configuration.
        
        Args:
            plugin_name: Name of the plugin
            config: Configuration dictionary
            
        Returns:
            Configuration with defaults applied
        """
        if plugin_name not in self._schemas:
            return config
        
        schema = self._schemas[plugin_name]
        return schema.apply_defaults(config)
    
    def get_config(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get stored configuration for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Configuration dictionary or None if not found
        """
        return self._configs.get(plugin_name)
    
    def set_config(self, plugin_name: str, config: Dict[str, Any]) -> None:
        """
        Store configuration for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            config: Configuration dictionary
        """
        self._configs[plugin_name] = config
    
    def save_config_to_file(self, plugin_name: str, config_path: Path) -> None:
        """
        Save plugin configuration to a file.
        
        Args:
            plugin_name: Name of the plugin
            config_path: Path to save configuration to
        """
        config = self.get_config(plugin_name)
        if config is None:
            raise ValueError(f"No configuration found for plugin '{plugin_name}'")
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def list_plugins_with_configs(self) -> List[str]:
        """List all plugins that have stored configurations."""
        return list(self._configs.keys())
    
    def clear_config(self, plugin_name: str) -> None:
        """Clear stored configuration for a plugin."""
        self._configs.pop(plugin_name, None)
    
    def clear_all_configs(self) -> None:
        """Clear all stored configurations."""
        self._configs.clear()


class StandardPluginConfigs:
    """
    Standard configuration schemas for built-in plugins.
    
    This class provides pre-defined configuration schemas for
    common plugin types.
    """
    
    @staticmethod
    def get_text_cleaning_schema() -> PluginConfigSchema:
        """Get configuration schema for text cleaning plugins."""
        return PluginConfigSchema(
            required_fields=["enabled"],
            optional_fields={
                "preserve_formatting": True,
                "remove_extra_spaces": True,
                "normalize_punctuation": True,
            },
            field_types={
                "enabled": bool,
                "preserve_formatting": bool,
                "remove_extra_spaces": bool,
                "normalize_punctuation": bool,
            },
            default_values={
                "enabled": True,
                "preserve_formatting": True,
                "remove_extra_spaces": True,
                "normalize_punctuation": True,
            },
        )
    
    @staticmethod
    def get_punctuation_adder_schema() -> PluginConfigSchema:
        """Get configuration schema for punctuation adder plugins."""
        return PluginConfigSchema(
            required_fields=["enabled", "model_name"],
            optional_fields={
                "local_models_dir": "models/",
                "batch_size": 32,
                "max_length": 512,
            },
            field_types={
                "enabled": bool,
                "model_name": str,
                "local_models_dir": str,
                "batch_size": int,
                "max_length": int,
            },
            field_validators={
                "batch_size": lambda x: x > 0,
                "max_length": lambda x: x > 0,
            },
            default_values={
                "enabled": True,
                "model_name": "oliverguhr/fullstop-punctuation-multilang-large",
                "local_models_dir": "models/",
                "batch_size": 32,
                "max_length": 512,
            },
        )
    
    @staticmethod
    def get_sentence_splitter_schema() -> PluginConfigSchema:
        """Get configuration schema for sentence splitter plugins."""
        return PluginConfigSchema(
            required_fields=["enabled"],
            optional_fields={
                "min_recursive_length": 70,
                "max_depth": 8,
                "preserve_quotes": True,
                "split_on_conjunctions": True,
            },
            field_types={
                "enabled": bool,
                "min_recursive_length": int,
                "max_depth": int,
                "preserve_quotes": bool,
                "split_on_conjunctions": bool,
            },
            field_validators={
                "min_recursive_length": lambda x: x > 0,
                "max_depth": lambda x: x > 0,
            },
            default_values={
                "enabled": True,
                "min_recursive_length": 70,
                "max_depth": 8,
                "preserve_quotes": True,
                "split_on_conjunctions": True,
            },
        )
    
    @staticmethod
    def get_text_to_sentences_schema() -> PluginConfigSchema:
        """Get configuration schema for text to sentences plugins."""
        return PluginConfigSchema(
            required_fields=["enabled"],
            optional_fields={
                "preserve_line_breaks": False,
                "handle_abbreviations": True,
            },
            field_types={
                "enabled": bool,
                "preserve_line_breaks": bool,
                "handle_abbreviations": bool,
            },
            default_values={
                "enabled": True,
                "preserve_line_breaks": False,
                "handle_abbreviations": True,
            },
        )


# Global configuration manager instance
_config_manager = PluginConfigManager()


def get_config_manager() -> PluginConfigManager:
    """Get the global configuration manager."""
    return _config_manager


def register_standard_schemas() -> None:
    """Register standard configuration schemas."""
    schemas = StandardPluginConfigs()
    
    _config_manager.register_schema("text_cleaning", schemas.get_text_cleaning_schema())
    _config_manager.register_schema("punctuation_adder", schemas.get_punctuation_adder_schema())
    _config_manager.register_schema("sentence_splitter", schemas.get_sentence_splitter_schema())
    _config_manager.register_schema("text_to_sentences", schemas.get_text_to_sentences_schema())


# Initialize standard schemas
register_standard_schemas()
