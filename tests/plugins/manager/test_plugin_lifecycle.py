"""
Tests for PluginLifecycleManager.
"""

import pytest
from unittest.mock import Mock, patch

from subtitleformatter.plugins import (
    PluginLifecycleManager,
    PluginRegistry,
    TextProcessorPlugin,
    PluginError,
    PluginInitializationError
)


class MockPlugin(TextProcessorPlugin):
    """Mock plugin for lifecycle tests."""
    
    name = "mock_plugin"
    version = "1.0.0"
    description = "Mock plugin"
    author = "Test Author"
    dependencies = []
    
    def process(self, text):
        return text


class MockPluginWithDependency(TextProcessorPlugin):
    """Mock plugin with dependency."""
    
    name = "mock_plugin_with_dep"
    version = "1.0.0"
    description = "Mock plugin with dependency"
    author = "Test Author"
    dependencies = ["test_service"]
    
    def process(self, text):
        return text


class MockPluginWithInitError(TextProcessorPlugin):
    """Mock plugin that raises error during initialization."""
    
    name = "mock_plugin_init_error"
    version = "1.0.0"
    description = "Mock plugin with init error"
    author = "Test Author"
    dependencies = []
    
    def process(self, text):
        return text
    
    def initialize(self):
        raise Exception("Initialization failed")


class MockPluginLifecycleManager:
    """Test cases for PluginLifecycleManager."""
    
    def test_lifecycle_manager_creation(self):
        """Test lifecycle manager creation."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        assert lifecycle.registry == registry
        assert lifecycle._instances == {}
        assert lifecycle._initialization_order == []
        assert lifecycle._dependencies == {}
    
    def test_register_dependency(self):
        """Test registering dependency."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        lifecycle.register_dependency("test_service", "test_value")
        assert lifecycle._dependencies["test_service"] == "test_value"
    
    def test_load_plugin_success(self):
        """Test successful plugin loading."""
        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []
        registry.create_plugin_instance.return_value = MockPlugin()
        
        lifecycle = PluginLifecycleManager(registry)
        plugin = lifecycle.load_plugin("test_plugin")
        
        assert isinstance(plugin, MockPlugin)
        assert "test_plugin" in lifecycle._instances
        assert "test_plugin" in lifecycle._initialization_order
        assert plugin._initialized
    
    def test_load_plugin_with_config(self):
        """Test loading plugin with configuration."""
        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []
        
        config = {"test_param": "test_value"}
        plugin_instance = MockPlugin(config)
        registry.create_plugin_instance.return_value = plugin_instance
        
        lifecycle = PluginLifecycleManager(registry)
        plugin = lifecycle.load_plugin("test_plugin", config)
        
        assert plugin.config == config
    
    def test_load_plugin_already_loaded(self):
        """Test loading already loaded plugin."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        # Pre-load a plugin
        existing_plugin = MockPlugin()
        lifecycle._instances["test_plugin"] = existing_plugin
        
        plugin = lifecycle.load_plugin("test_plugin")
        assert plugin == existing_plugin
    
    def test_load_plugin_missing_dependencies(self):
        """Test loading plugin with missing dependencies."""
        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = ["missing_dep"]
        
        lifecycle = PluginLifecycleManager(registry)
        
        with pytest.raises(PluginError, match="missing dependencies"):
            lifecycle.load_plugin("test_plugin")
    
    def test_load_plugin_initialization_error(self):
        """Test loading plugin with initialization error."""
        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []
        registry.create_plugin_instance.return_value = MockPluginWithInitError()
        
        lifecycle = PluginLifecycleManager(registry)
        
        with pytest.raises(PluginInitializationError):
            lifecycle.load_plugin("test_plugin")
    
    def test_load_plugins_success(self):
        """Test loading multiple plugins successfully."""
        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []
        
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
        
        plugin_configs = {
            "plugin1": {"enabled": True},
            "plugin2": {"enabled": True},
            "plugin3": {"enabled": False}  # Disabled plugin
        }
        
        loaded_plugins = lifecycle.load_plugins(plugin_configs)
        
        assert "plugin1" in loaded_plugins
        assert "plugin2" in loaded_plugins
        assert "plugin3" not in loaded_plugins
        assert len(loaded_plugins) == 2
    
    def test_load_plugins_initialization_error(self):
        """Test loading plugins with initialization error."""
        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []
        
        plugin1 = MockPlugin()
        plugin2 = MockPluginWithInitError()
        
        def create_instance_side_effect(name, config=None):
            if name == "plugin1":
                return plugin1
            elif name == "plugin2":
                return plugin2
            return MockPlugin()
        
        registry.create_plugin_instance.side_effect = create_instance_side_effect
        
        lifecycle = PluginLifecycleManager(registry)
        
        plugin_configs = {
            "plugin1": {"enabled": True},
            "plugin2": {"enabled": True}
        }
        
        with pytest.raises(PluginInitializationError):
            lifecycle.load_plugins(plugin_configs)
        
        # Should clean up all plugins on error
        assert len(lifecycle._instances) == 0
    
    def test_inject_dependencies(self):
        """Test dependency injection."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        # Register dependencies
        lifecycle.register_dependency("service1", "value1")
        lifecycle.register_dependency("service2", "value2")
        
        # Create plugin instance
        plugin = MockPlugin()
        lifecycle._instances["test_plugin"] = plugin
        
        # Inject dependencies
        lifecycle._inject_dependencies(plugin)
        
        assert plugin.has_dependency("service1")
        assert plugin.has_dependency("service2")
        assert plugin.get_dependency("service1") == "value1"
        assert plugin.get_dependency("service2") == "value2"
    
    def test_inject_plugin_dependencies(self):
        """Test injecting other plugins as dependencies."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        # Create multiple plugin instances
        plugin1 = MockPlugin()
        plugin2 = MockPlugin()
        lifecycle._instances["plugin1"] = plugin1
        lifecycle._instances["plugin2"] = plugin2
        
        # Inject dependencies into plugin1
        lifecycle._inject_dependencies(plugin1)
        
        assert plugin1.has_dependency("plugin2")
        assert plugin1.get_dependency("plugin2") == plugin2
    
    def test_unload_plugin(self):
        """Test unloading plugin."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        # Load a plugin
        plugin = MockPlugin()
        lifecycle._instances["test_plugin"] = plugin
        lifecycle._initialization_order = ["test_plugin"]
        
        lifecycle.unload_plugin("test_plugin")
        
        assert "test_plugin" not in lifecycle._instances
        assert "test_plugin" not in lifecycle._initialization_order
    
    def test_unload_nonexistent_plugin(self):
        """Test unloading non-existent plugin."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        # Should not raise error
        lifecycle.unload_plugin("nonexistent_plugin")
    
    def test_cleanup_all(self):
        """Test cleaning up all plugins."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        # Load multiple plugins
        plugin1 = MockPlugin()
        plugin2 = MockPlugin()
        lifecycle._instances["plugin1"] = plugin1
        lifecycle._instances["plugin2"] = plugin2
        lifecycle._initialization_order = ["plugin1", "plugin2"]
        
        lifecycle.cleanup_all()
        
        assert len(lifecycle._instances) == 0
        assert len(lifecycle._initialization_order) == 0
    
    def test_get_plugin_instance(self):
        """Test getting plugin instance."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        plugin = MockPlugin()
        lifecycle._instances["test_plugin"] = plugin
        
        instance = lifecycle.get_plugin_instance("test_plugin")
        assert instance == plugin
        
        instance = lifecycle.get_plugin_instance("nonexistent")
        assert instance is None
    
    def test_is_plugin_loaded(self):
        """Test checking if plugin is loaded."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        plugin = MockPlugin()
        lifecycle._instances["test_plugin"] = plugin
        
        assert lifecycle.is_plugin_loaded("test_plugin")
        assert not lifecycle.is_plugin_loaded("nonexistent")
    
    def test_list_loaded_plugins(self):
        """Test listing loaded plugins."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        plugin1 = MockPlugin()
        plugin2 = MockPlugin()
        lifecycle._instances["plugin1"] = plugin1
        lifecycle._instances["plugin2"] = plugin2
        
        loaded = lifecycle.list_loaded_plugins()
        assert set(loaded) == {"plugin1", "plugin2"}
    
    def test_get_plugin_info(self):
        """Test getting plugin info."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        plugin = MockPlugin()
        lifecycle._instances["test_plugin"] = plugin
        
        info = lifecycle.get_plugin_info("test_plugin")
        assert info is not None
        assert info["name"] == "test_plugin"
        
        info = lifecycle.get_plugin_info("nonexistent")
        assert info is None
    
    def test_reload_plugin(self):
        """Test reloading plugin."""
        registry = Mock(spec=PluginRegistry)
        registry.validate_plugin_dependencies.return_value = []
        
        old_plugin = MockPlugin()
        new_plugin = MockPlugin()
        
        def create_instance_side_effect(name, config=None):
            return new_plugin
        
        registry.create_plugin_instance.side_effect = create_instance_side_effect
        
        lifecycle = PluginLifecycleManager(registry)
        
        # Load initial plugin
        lifecycle._instances["test_plugin"] = old_plugin
        
        # Reload plugin
        reloaded_plugin = lifecycle.reload_plugin("test_plugin")
        
        assert reloaded_plugin == new_plugin
        assert lifecycle._instances["test_plugin"] == new_plugin
    
    def test_get_dependency_graph(self):
        """Test getting dependency graph."""
        registry = Mock(spec=PluginRegistry)
        lifecycle = PluginLifecycleManager(registry)
        
        # Create plugins with dependencies
        plugin1 = MockPlugin()
        plugin2 = MockPlugin()
        plugin3 = MockPlugin()
        
        plugin1.dependencies = ["plugin2"]
        plugin2.dependencies = ["plugin3"]
        plugin3.dependencies = []
        
        lifecycle._instances["plugin1"] = plugin1
        lifecycle._instances["plugin2"] = plugin2
        lifecycle._instances["plugin3"] = plugin3
        
        graph = lifecycle.get_dependency_graph()
        
        assert graph["plugin1"] == ["plugin2"]
        assert graph["plugin2"] == ["plugin3"]
        assert graph["plugin3"] == []
