"""
Comprehensive integration tests for the plugin system.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from subtitleformatter.plugins import (
    PluginConfigManager,
    PluginEventSystem,
    PluginLifecycleManager,
    PluginRegistry,
    TextProcessorPlugin,
    create_event_bus,
    register_singleton,
)


class MockPlugin(TextProcessorPlugin):
    """Mock plugin for integration tests."""

    name = "mock_plugin"
    version = "1.0.0"
    description = "Mock plugin for integration tests"
    author = "Test Author"
    dependencies = []

    def process(self, text):
        return text.upper() if isinstance(text, str) else text


class MockPluginWithDependency(TextProcessorPlugin):
    """Mock plugin with dependency."""

    name = "mock_plugin_with_dep"
    version = "1.0.0"
    description = "Mock plugin with dependency"
    author = "Test Author"
    dependencies = ["test_service"]

    def process(self, text):
        return text


class MockPluginIntegration:
    """Integration tests for the complete plugin system."""

    def test_complete_plugin_workflow(self):
        """Test complete plugin workflow from discovery to execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup plugin directory
            plugin_dir = Path(temp_dir) / "plugins"
            plugin_dir.mkdir()

            plugin_subdir = plugin_dir / "test_plugin"
            plugin_subdir.mkdir()

            # Create plugin.json
            import json

            plugin_json = {
                "name": "test_plugin",
                "version": "1.0.0",
                "description": "Test plugin",
                "author": "Test Author",
                "class_name": "MockPlugin",
                "dependencies": [],
            }

            with open(plugin_subdir / "plugin.json", "w") as f:
                json.dump(plugin_json, f)

            # Create plugin.py
            plugin_code = """
from subtitleformatter.plugins import TextProcessorPlugin

class MockPlugin(TextProcessorPlugin):
    name = "test_plugin"
    version = "1.0.0"
    description = "Test plugin"
    author = "Test Author"
    dependencies = []
    
    def process(self, text):
        return text.upper() if isinstance(text, str) else text
"""

            with open(plugin_subdir / "plugin.py", "w") as f:
                f.write(plugin_code)

            # Test complete workflow
            registry = PluginRegistry()
            registry.add_plugin_dir(plugin_dir)
            registry.scan_plugins()

            assert "test_plugin" in registry.list_plugins()

            lifecycle = PluginLifecycleManager(registry)
            plugin = lifecycle.load_plugin("test_plugin")

            assert isinstance(plugin, TextProcessorPlugin)
            assert plugin.process("hello") == "HELLO"

            lifecycle.cleanup_all()

    def test_plugin_with_dependency_injection(self):
        """Test plugin with dependency injection."""
        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []
        registry.create_plugin_instance.return_value = MockPluginWithDependency()

        lifecycle = PluginLifecycleManager(registry)

        # Register dependency
        lifecycle.register_dependency("test_service", "service_value")

        # Load plugin
        plugin = lifecycle.load_plugin("test_plugin_with_dep")

        # Verify dependency was injected
        assert plugin.has_dependency("test_service")
        assert plugin.get_dependency("test_service") == "service_value"

        lifecycle.cleanup_all()

    def test_plugin_with_configuration(self):
        """Test plugin with configuration management."""
        config_manager = PluginConfigManager()

        # Set plugin configuration
        config = {"enabled": True, "param1": "value1"}
        config_manager.set_plugin_config("test_plugin", config)

        # Get configuration
        retrieved_config = config_manager.get_plugin_config("test_plugin")
        assert retrieved_config == config

        # Set default configuration
        default_config = {"enabled": True, "param1": "default_value", "param2": "default_value2"}
        config_manager.set_default_config("test_plugin", default_config)

        # Normalize configuration
        normalized = config_manager.normalize_config("test_plugin", config)
        expected = {"enabled": True, "param1": "value1", "param2": "default_value2"}
        assert normalized == expected

    def test_plugin_with_events(self):
        """Test plugin with event system."""
        event_system = PluginEventSystem()

        # Create event bus for plugin
        event_bus = create_event_bus("test_plugin")

        # Register event handler
        received_events = []

        def handler(event):
            received_events.append(event)

        event_bus.listen("test_event", handler)

        # Emit event
        event_bus.emit("test_event", "test_data")

        assert len(received_events) == 1
        assert received_events[0].name == "test_event"
        assert received_events[0].data == "test_data"
        assert received_events[0].source == "test_plugin"

        # Cleanup
        event_bus.cleanup()

    def test_plugin_chain_execution(self):
        """Test executing multiple plugins in chain."""
        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []

        # Create multiple plugin instances
        plugin1 = MockPlugin()
        plugin2 = MockPlugin()

        def create_instance_side_effect(name, config=None):
            if name == "plugin1":
                return plugin1
            elif name == "plugin2":
                return plugin2
            return MockPlugin()

        registry.create_plugin_instance.side_effect = create_instance_side_effect

        lifecycle = PluginLifecycleManager(registry)

        # Load multiple plugins
        plugin_configs = {"plugin1": {"enabled": True}, "plugin2": {"enabled": True}}

        loaded_plugins = lifecycle.load_plugins(plugin_configs)

        # Execute plugin chain
        text = "hello world"
        result = text

        for plugin_name, plugin in loaded_plugins.items():
            result = plugin.process(result)

        assert result == "HELLO WORLD"

        lifecycle.cleanup_all()

    def test_plugin_error_handling(self):
        """Test plugin error handling."""
        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []

        # Create plugin that raises error
        class ErrorPlugin(TextProcessorPlugin):
            name = "error_plugin"
            version = "1.0.0"
            description = "Plugin that raises error"
            author = "Test Author"
            dependencies = []

            def process(self, text):
                raise Exception("Processing error")

        registry.create_plugin_instance.return_value = ErrorPlugin()

        lifecycle = PluginLifecycleManager(registry)

        # Load plugin
        plugin = lifecycle.load_plugin("error_plugin")

        # Test error handling
        with pytest.raises(Exception, match="Processing error"):
            plugin.process("test")

        lifecycle.cleanup_all()

    def test_plugin_lifecycle_events(self):
        """Test plugin lifecycle events."""
        event_system = PluginEventSystem()

        # Register lifecycle event handlers
        lifecycle_events = []

        def lifecycle_handler(event):
            lifecycle_events.append(event)

        event_system.register_wildcard_handler(lifecycle_handler)

        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []
        registry.create_plugin_instance.return_value = MockPlugin()

        lifecycle = PluginLifecycleManager(registry)

        # Load plugin
        plugin = lifecycle.load_plugin("test_plugin")

        # Emit lifecycle events
        event_bus = create_event_bus("test_plugin")
        event_bus.emit("plugin_loaded", {"plugin_name": "test_plugin"})
        event_bus.emit("plugin_initialized", {"plugin_name": "test_plugin"})

        # Verify events were received
        assert len(lifecycle_events) >= 2

        lifecycle.cleanup_all()
        event_bus.cleanup()

    def test_plugin_configuration_validation(self):
        """Test plugin configuration validation."""
        config_manager = PluginConfigManager()

        # Set configuration schema
        schema = {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "param1": {"type": "string"},
                "param2": {"type": "integer"},
            },
            "required": ["enabled"],
        }

        config_manager._config_schema = schema

        # Test valid configuration
        valid_config = {"enabled": True, "param1": "value1", "param2": 42}
        errors = config_manager.validate_plugin_config("test_plugin", valid_config)
        assert len(errors) == 0

        # Test invalid configuration
        invalid_config = {"param1": "value1"}  # Missing required field
        errors = config_manager.validate_plugin_config("test_plugin", invalid_config)
        assert len(errors) == 1
        assert "Required field 'enabled' missing" in errors[0]

    def test_plugin_dependency_resolution(self):
        """Test plugin dependency resolution."""
        registry = Mock(spec=PluginRegistry)

        # Mock dependency validation
        def validate_dependencies_side_effect(name):
            if name == "plugin_with_dep":
                return ["dependency_plugin"]
            return []

        registry.validate_plugin_dependencies.side_effect = validate_dependencies_side_effect

        lifecycle = PluginLifecycleManager(registry)

        # Test loading plugin with missing dependency
        with pytest.raises(Exception, match="missing dependencies"):
            lifecycle.load_plugin("plugin_with_dep")

    def test_plugin_performance_monitoring(self):
        """Test plugin performance monitoring."""
        import time

        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []

        # Create plugin with timing
        class TimedPlugin(TextProcessorPlugin):
            name = "timed_plugin"
            version = "1.0.0"
            description = "Plugin with timing"
            author = "Test Author"
            dependencies = []

            def process(self, text):
                time.sleep(0.01)  # Simulate processing time
                return text

        registry.create_plugin_instance.return_value = TimedPlugin()

        lifecycle = PluginLifecycleManager(registry)

        # Load plugin
        plugin = lifecycle.load_plugin("timed_plugin")

        # Measure processing time
        start_time = time.time()
        result = plugin.process("test")
        end_time = time.time()

        processing_time = end_time - start_time

        assert result == "test"
        assert processing_time >= 0.01  # Should take at least 10ms

        lifecycle.cleanup_all()
