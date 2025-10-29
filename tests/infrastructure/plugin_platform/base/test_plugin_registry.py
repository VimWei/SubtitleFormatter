"""
Tests for PluginRegistry.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from subtitleformatter.plugins import PluginError, PluginRegistry, TextProcessorPlugin


class MockPlugin(TextProcessorPlugin):
    """Mock plugin for registry tests."""

    name = "mock_plugin"
    version = "1.0.0"
    description = "Mock plugin"
    author = "Test Author"
    dependencies = []

    def process(self, text):
        return text


class MockPluginRegistry:
    """Test cases for PluginRegistry."""

    def test_registry_creation(self):
        """Test registry creation."""
        registry = PluginRegistry()
        assert registry.plugin_dirs == []
        assert registry._plugins == {}
        assert registry._plugin_metadata == {}
        assert not registry._scanned

    def test_add_plugin_dir(self):
        """Test adding plugin directory."""
        registry = PluginRegistry()
        plugin_dir = Path("test_plugins")

        registry.add_plugin_dir(plugin_dir)
        assert plugin_dir in registry.plugin_dirs
        assert not registry._scanned  # Should mark for rescan

    def test_add_duplicate_plugin_dir(self):
        """Test adding duplicate plugin directory."""
        registry = PluginRegistry()
        plugin_dir = Path("test_plugins")

        registry.add_plugin_dir(plugin_dir)
        registry.add_plugin_dir(plugin_dir)

        assert registry.plugin_dirs.count(plugin_dir) == 1

    def test_scan_empty_directory(self):
        """Test scanning empty directory."""
        registry = PluginRegistry()

        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir)
            registry.add_plugin_dir(plugin_dir)
            registry.scan_plugins()

            assert registry._scanned
            assert len(registry._plugins) == 0

    def test_scan_nonexistent_directory(self):
        """Test scanning non-existent directory."""
        registry = PluginRegistry()
        registry.add_plugin_dir(Path("nonexistent_dir"))
        registry.scan_plugins()

        assert registry._scanned
        assert len(registry._plugins) == 0

    def test_register_plugin_success(self):
        """Test successful plugin registration."""
        registry = PluginRegistry()

        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir)
            plugin_subdir = plugin_dir / "test_plugin"
            plugin_subdir.mkdir()

            # Create plugin.json
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
        return text
"""

            with open(plugin_subdir / "plugin.py", "w") as f:
                f.write(plugin_code)

            registry.add_plugin_dir(plugin_dir)
            registry.scan_plugins()

            assert "test_plugin" in registry._plugins
            assert "test_plugin" in registry._plugin_metadata

    def test_register_plugin_missing_json(self):
        """Test plugin registration with missing JSON file."""
        registry = PluginRegistry()

        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir)
            plugin_subdir = plugin_dir / "test_plugin"
            plugin_subdir.mkdir()

            # Create only plugin.py, no plugin.json
            plugin_code = """
from subtitleformatter.plugins import TextProcessorPlugin

class MockPlugin(TextProcessorPlugin):
    name = "test_plugin"
    version = "1.0.0"
    description = "Test plugin"
    author = "Test Author"
    dependencies = []
    
    def process(self, text):
        return text
"""

            with open(plugin_subdir / "plugin.py", "w") as f:
                f.write(plugin_code)

            registry.add_plugin_dir(plugin_dir)
            registry.scan_plugins()

            # Should not register plugin without JSON
            assert len(registry._plugins) == 0

    def test_register_plugin_missing_py(self):
        """Test plugin registration with missing Python file."""
        registry = PluginRegistry()

        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir)
            plugin_subdir = plugin_dir / "test_plugin"
            plugin_subdir.mkdir()

            # Create only plugin.json, no plugin.py
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

            registry.add_plugin_dir(plugin_dir)
            registry.scan_plugins()

            # Should not register plugin without Python file
            assert len(registry._plugins) == 0

    def test_register_plugin_invalid_json(self):
        """Test plugin registration with invalid JSON."""
        registry = PluginRegistry()

        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir)
            plugin_subdir = plugin_dir / "test_plugin"
            plugin_subdir.mkdir()

            # Create invalid JSON
            with open(plugin_subdir / "plugin.json", "w") as f:
                f.write("invalid json")

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
        return text
"""

            with open(plugin_subdir / "plugin.py", "w") as f:
                f.write(plugin_code)

            registry.add_plugin_dir(plugin_dir)
            registry.scan_plugins()

            # Should not register plugin with invalid JSON
            assert len(registry._plugins) == 0

    def test_register_plugin_missing_required_field(self):
        """Test plugin registration with missing required field."""
        registry = PluginRegistry()

        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir)
            plugin_subdir = plugin_dir / "test_plugin"
            plugin_subdir.mkdir()

            # Create plugin.json with missing required field
            plugin_json = {
                "name": "test_plugin",
                "version": "1.0.0",
                "description": "Test plugin",
                "author": "Test Author",
                # Missing "class_name"
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
        return text
"""

            with open(plugin_subdir / "plugin.py", "w") as f:
                f.write(plugin_code)

            registry.add_plugin_dir(plugin_dir)
            registry.scan_plugins()

            # Should not register plugin with missing required field
            assert len(registry._plugins) == 0

    def test_register_plugin_invalid_class(self):
        """Test plugin registration with invalid class."""
        registry = PluginRegistry()

        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir)
            plugin_subdir = plugin_dir / "test_plugin"
            plugin_subdir.mkdir()

            # Create plugin.json
            plugin_json = {
                "name": "test_plugin",
                "version": "1.0.0",
                "description": "Test plugin",
                "author": "Test Author",
                "class_name": "InvalidPlugin",
                "dependencies": [],
            }

            with open(plugin_subdir / "plugin.json", "w") as f:
                json.dump(plugin_json, f)

            # Create plugin.py with invalid class
            plugin_code = """
class InvalidPlugin:
    pass
"""

            with open(plugin_subdir / "plugin.py", "w") as f:
                f.write(plugin_code)

            registry.add_plugin_dir(plugin_dir)
            registry.scan_plugins()

            # Should not register plugin with invalid class
            assert len(registry._plugins) == 0

    def test_get_plugin_class(self):
        """Test getting plugin class."""
        registry = PluginRegistry()

        # Mock a registered plugin
        registry._plugins["test_plugin"] = MockPlugin
        registry._scanned = True

        plugin_class = registry.get_plugin_class("test_plugin")
        assert plugin_class == MockPlugin

    def test_get_plugin_class_not_found(self):
        """Test getting non-existent plugin class."""
        registry = PluginRegistry()
        registry._scanned = True

        with pytest.raises(KeyError):
            registry.get_plugin_class("nonexistent_plugin")

    def test_get_plugin_class_not_scanned(self):
        """Test getting plugin class when not scanned."""
        registry = PluginRegistry()

        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir)
            plugin_subdir = plugin_dir / "test_plugin"
            plugin_subdir.mkdir()

            # Create plugin files
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

            plugin_code = """
from subtitleformatter.plugins import TextProcessorPlugin

class MockPlugin(TextProcessorPlugin):
    name = "test_plugin"
    version = "1.0.0"
    description = "Test plugin"
    author = "Test Author"
    dependencies = []
    
    def process(self, text):
        return text
"""

            with open(plugin_subdir / "plugin.py", "w") as f:
                f.write(plugin_code)

            registry.add_plugin_dir(plugin_dir)

            # Should trigger scan when getting plugin class
            plugin_class = registry.get_plugin_class("test_plugin")
            assert plugin_class is not None

    def test_list_plugins(self):
        """Test listing plugins."""
        registry = PluginRegistry()
        registry._plugins = {"plugin1": MockPlugin, "plugin2": MockPlugin}
        registry._scanned = True

        plugins = registry.list_plugins()
        assert set(plugins) == {"plugin1", "plugin2"}

    def test_is_plugin_available(self):
        """Test checking plugin availability."""
        registry = PluginRegistry()
        registry._plugins = {"test_plugin": MockPlugin}
        registry._scanned = True

        assert registry.is_plugin_available("test_plugin")
        assert not registry.is_plugin_available("nonexistent_plugin")

    def test_create_plugin_instance(self):
        """Test creating plugin instance."""
        registry = PluginRegistry()
        registry._plugins = {"test_plugin": MockPlugin}
        registry._scanned = True

        instance = registry.create_plugin_instance("test_plugin")
        assert isinstance(instance, MockPlugin)

    def test_create_plugin_instance_with_config(self):
        """Test creating plugin instance with config."""
        registry = PluginRegistry()
        registry._plugins = {"test_plugin": MockPlugin}
        registry._scanned = True

        config = {"test_param": "test_value"}
        instance = registry.create_plugin_instance("test_plugin", config)
        assert isinstance(instance, MockPlugin)
        assert instance.config == config

    def test_create_plugin_instance_not_found(self):
        """Test creating instance of non-existent plugin."""
        registry = PluginRegistry()
        registry._scanned = True

        with pytest.raises(KeyError):
            registry.create_plugin_instance("nonexistent_plugin")

    def test_get_plugin_dependencies(self):
        """Test getting plugin dependencies."""
        registry = PluginRegistry()
        registry._plugin_metadata = {"test_plugin": {"dependencies": ["dep1", "dep2"]}}
        registry._scanned = True

        deps = registry.get_plugin_dependencies("test_plugin")
        assert deps == ["dep1", "dep2"]

    def test_validate_plugin_dependencies(self):
        """Test validating plugin dependencies."""
        registry = PluginRegistry()
        registry._plugin_metadata = {
            "test_plugin": {"dependencies": ["dep1", "dep2"]},
            "dep1": {"dependencies": []},
        }
        registry._scanned = True

        missing = registry.validate_plugin_dependencies("test_plugin")
        assert "dep2" in missing
        assert "dep1" not in missing
