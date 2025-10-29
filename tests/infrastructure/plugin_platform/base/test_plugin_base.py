"""
Tests for TextProcessorPlugin base class.
"""

from unittest.mock import Mock, patch

import pytest

from subtitleformatter.plugins import (
    PluginConfigurationError,
    PluginError,
    PluginInitializationError,
    TextProcessorPlugin,
)


class MockPlugin(TextProcessorPlugin):
    """Mock plugin implementation for testing."""

    name = "mock_plugin"
    version = "1.0.0"
    description = "Mock plugin"
    author = "Test Author"
    dependencies = []

    def process(self, text):
        """Mock process method."""
        return text.upper() if isinstance(text, str) else text


class MockPluginWithConfig(TextProcessorPlugin):
    """Mock plugin with configuration schema."""

    name = "mock_plugin_with_config"
    version = "1.0.0"
    description = "Mock plugin with config"
    author = "Test Author"
    dependencies = []
    config_schema = {
        "required": ["enabled"],
        "optional": {"param1": "default_value"},
        "field_types": {"enabled": bool, "param1": str},
        "default_values": {"enabled": True, "param1": "default_value"},
    }

    def process(self, text):
        """Mock process method."""
        return text


class TestTextProcessorPlugin:
    """Test cases for TextProcessorPlugin base class."""

    def test_plugin_creation(self):
        """Test basic plugin creation."""
        plugin = MockPlugin()
        assert plugin.name == "mock_plugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "Mock plugin"
        assert plugin.author == "Test Author"
        assert plugin.dependencies == []
        assert not plugin._initialized

    def test_plugin_creation_with_config(self):
        """Test plugin creation with configuration."""
        config = {"enabled": True, "param1": "test"}
        plugin = MockPluginWithConfig(config)
        assert plugin.config == config

    def test_plugin_config_validation(self):
        """Test plugin configuration validation."""
        # Test missing required field
        with pytest.raises(PluginConfigurationError):
            MockPluginWithConfig({"param1": "test"})

        # Test valid configuration
        config = {"enabled": True, "param1": "test"}
        plugin = MockPluginWithConfig(config)
        assert plugin.config == config

    def test_plugin_process_method(self):
        """Test plugin process method."""
        plugin = MockPlugin()
        result = plugin.process("hello")
        assert result == "HELLO"

        result = plugin.process(["hello", "world"])
        assert result == ["hello", "world"]

    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = MockPlugin()
        assert not plugin._initialized

        plugin.initialize()
        assert plugin._initialized

    def test_plugin_cleanup(self):
        """Test plugin cleanup."""
        plugin = MockPlugin()
        plugin.initialize()
        assert plugin._initialized

        plugin.cleanup()
        assert not plugin._initialized

    def test_plugin_info(self):
        """Test plugin info retrieval."""
        plugin = MockPlugin()
        info = plugin.get_info()

        assert info["name"] == "mock_plugin"
        assert info["version"] == "1.0.0"
        assert info["description"] == "Mock plugin"
        assert info["author"] == "Test Author"
        assert info["dependencies"] == []
        assert info["initialized"] is False
        assert info["config"] == {}

    def test_dependency_management(self):
        """Test dependency management."""
        plugin = MockPlugin()

        # Test setting dependency
        plugin.set_dependency("test_dep", "test_value")
        assert plugin.has_dependency("test_dep")

        # Test getting dependency
        dep = plugin.get_dependency("test_dep")
        assert dep == "test_value"

        # Test missing dependency
        with pytest.raises(KeyError):
            plugin.get_dependency("missing_dep")

    def test_plugin_string_representation(self):
        """Test plugin string representation."""
        plugin = MockPlugin()
        str_repr = str(plugin)
        assert "mock_plugin" in str_repr
        assert "1.0.0" in str_repr
        assert "Test Author" in str_repr

    def test_plugin_repr(self):
        """Test plugin detailed representation."""
        plugin = MockPlugin()
        repr_str = repr(plugin)
        assert "TextProcessorPlugin" in repr_str
        assert "mock_plugin" in repr_str
        assert "1.0.0" in repr_str


class TestPluginErrors:
    """Test cases for plugin error classes."""

    def test_plugin_error(self):
        """Test PluginError exception."""
        error = PluginError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_plugin_initialization_error(self):
        """Test PluginInitializationError exception."""
        error = PluginInitializationError("Init error")
        assert "Init error" in str(error)
        assert "(Error Code: INIT_ERROR)" in str(error)
        assert isinstance(error, PluginError)

    def test_plugin_configuration_error(self):
        """Test PluginConfigurationError exception."""
        error = PluginConfigurationError("Config error")
        assert "Config error" in str(error)
        assert "(Error Code: CONFIG_ERROR)" in str(error)
        assert isinstance(error, PluginError)

    def test_plugin_dependency_error(self):
        """Test PluginDependencyError exception."""
        from subtitleformatter.plugins import PluginDependencyError

        error = PluginDependencyError("Dependency error")
        assert "Dependency error" in str(error)
        assert "(Error Code: DEPENDENCY_ERROR)" in str(error)
        assert isinstance(error, PluginError)
