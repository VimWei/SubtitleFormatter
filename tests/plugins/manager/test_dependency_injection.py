"""
Tests for dependency injection system.
"""

import pytest
from unittest.mock import Mock

from subtitleformatter.plugins import (
    DependencyContainer,
    DependencyInjector,
    TextProcessorPlugin,
    get_container,
    get_injector,
    register_singleton,
    register_factory,
    register_alias,
    get_service,
    inject_into,
    inject_into_plugin
)


class MockPlugin(TextProcessorPlugin):
    """Mock plugin for dependency injection tests."""
    
    name = "mock_plugin"
    version = "1.0.0"
    description = "Mock plugin"
    author = "Test Author"
    dependencies = []
    
    def process(self, text):
        return text


class TestDependencyContainer:
    """Test cases for DependencyContainer."""
    
    def test_container_creation(self):
        """Test container creation."""
        container = DependencyContainer()
        
        assert container._services == {}
        assert container._singletons == {}
        assert container._factories == {}
        assert container._aliases == {}
    
    def test_register_singleton(self):
        """Test registering singleton."""
        container = DependencyContainer()
        
        container.register_singleton("test_service", "test_value")
        
        assert container._services["test_service"] == "test_value"
        assert container._singletons["test_service"] == "test_value"
    
    def test_register_factory(self):
        """Test registering factory."""
        container = DependencyContainer()
        
        def factory():
            return "factory_value"
        
        container.register_factory("test_service", factory)
        
        assert container._factories["test_service"] == factory
    
    def test_register_alias(self):
        """Test registering alias."""
        container = DependencyContainer()
        
        container.register_alias("alias", "target")
        
        assert container._aliases["alias"] == "target"
    
    def test_get_singleton(self):
        """Test getting singleton service."""
        container = DependencyContainer()
        
        container.register_singleton("test_service", "test_value")
        
        service = container.get("test_service")
        assert service == "test_value"
    
    def test_get_factory(self):
        """Test getting service from factory."""
        container = DependencyContainer()
        
        def factory():
            return "factory_value"
        
        container.register_factory("test_service", factory)
        
        service = container.get("test_service")
        assert service == "factory_value"
        
        # Should be cached as singleton
        assert "test_service" in container._singletons
    
    def test_get_alias(self):
        """Test getting service through alias."""
        container = DependencyContainer()
        
        container.register_singleton("target_service", "target_value")
        container.register_alias("alias", "target_service")
        
        service = container.get("alias")
        assert service == "target_value"
    
    def test_get_nonexistent_service(self):
        """Test getting non-existent service."""
        container = DependencyContainer()
        
        with pytest.raises(KeyError):
            container.get("nonexistent_service")
    
    def test_get_typed_service(self):
        """Test getting typed service."""
        container = DependencyContainer()
        
        container.register_singleton("test_service", "test_value")
        
        service = container.get_typed("test_service", str)
        assert service == "test_value"
    
    def test_get_typed_service_wrong_type(self):
        """Test getting service with wrong type."""
        container = DependencyContainer()
        
        container.register_singleton("test_service", "test_value")
        
        with pytest.raises(TypeError):
            container.get_typed("test_service", int)
    
    def test_has_service(self):
        """Test checking if service exists."""
        container = DependencyContainer()
        
        container.register_singleton("test_service", "test_value")
        container.register_alias("alias", "test_service")
        
        assert container.has("test_service")
        assert container.has("alias")
        assert not container.has("nonexistent")
    
    def test_list_services(self):
        """Test listing services."""
        container = DependencyContainer()
        
        container.register_singleton("service1", "value1")
        container.register_factory("service2", lambda: "value2")
        container.register_alias("alias1", "service1")
        
        services = container.list_services()
        assert set(services) == {"service1", "service2", "alias1"}
    
    def test_remove_service(self):
        """Test removing service."""
        container = DependencyContainer()
        
        container.register_singleton("test_service", "test_value")
        container.register_alias("alias", "test_service")
        
        container.remove("test_service")
        
        assert "test_service" not in container._services
        assert "test_service" not in container._singletons
        assert "alias" not in container._aliases
    
    def test_clear_services(self):
        """Test clearing all services."""
        container = DependencyContainer()
        
        container.register_singleton("service1", "value1")
        container.register_factory("service2", lambda: "value2")
        container.register_alias("alias", "service1")
        
        container.clear()
        
        assert len(container._services) == 0
        assert len(container._singletons) == 0
        assert len(container._factories) == 0
        assert len(container._aliases) == 0


class TestDependencyInjector:
    """Test cases for DependencyInjector."""
    
    def test_injector_creation(self):
        """Test injector creation."""
        container = DependencyContainer()
        injector = DependencyInjector(container)
        
        assert injector.container == container
    
    def test_inject_into_with_set_dependency_method(self):
        """Test injecting into object with set_dependency method."""
        container = DependencyContainer()
        container.register_singleton("test_service", "test_value")
        
        injector = DependencyInjector(container)
        
        plugin = MockPlugin()
        injector.inject_into(plugin, ["test_service"])
        
        assert plugin.has_dependency("test_service")
        assert plugin.get_dependency("test_service") == "test_value"
    
    def test_inject_into_with_attribute(self):
        """Test injecting into object with attribute."""
        container = DependencyContainer()
        container.register_singleton("test_service", "test_value")
        
        injector = DependencyInjector(container)
        
        class TestObject:
            def __init__(self):
                self.test_service = None
        
        obj = TestObject()
        injector.inject_into(obj, ["test_service"])
        
        assert obj.test_service == "test_value"
    
    def test_inject_into_plugin(self):
        """Test injecting into plugin."""
        container = DependencyContainer()
        container.register_singleton("test_service", "test_value")
        
        injector = DependencyInjector(container)
        
        plugin = MockPlugin()
        plugin.dependencies = ["test_service"]
        
        injector.inject_into_plugin(plugin)
        
        assert plugin.has_dependency("test_service")
        assert plugin.get_dependency("test_service") == "test_value"
    
    def test_inject_into_plugin_no_dependencies(self):
        """Test injecting into plugin with no dependencies."""
        container = DependencyContainer()
        container.register_singleton("test_service", "test_value")
        
        injector = DependencyInjector(container)
        
        plugin = MockPlugin()
        plugin.dependencies = []
        
        injector.inject_into_plugin(plugin)
        
        # Should inject all available services
        assert plugin.has_dependency("test_service")
    
    def test_create_with_injection(self):
        """Test creating instance with injection."""
        container = DependencyContainer()
        container.register_singleton("test_service", "test_value")
        
        injector = DependencyInjector(container)
        
        class TestClass:
            def __init__(self):
                self.test_service = None
        
        instance = injector.create_with_injection(TestClass)
        
        assert instance.test_service == "test_value"


class TestGlobalFunctions:
    """Test cases for global dependency injection functions."""
    
    def test_register_singleton_global(self):
        """Test global register_singleton function."""
        register_singleton("global_service", "global_value")
        
        container = get_container()
        assert container.has("global_service")
        assert container.get("global_service") == "global_value"
    
    def test_register_factory_global(self):
        """Test global register_factory function."""
        def factory():
            return "factory_value"
        
        register_factory("global_factory", factory)
        
        container = get_container()
        assert container.has("global_factory")
        assert container.get("global_factory") == "factory_value"
    
    def test_register_alias_global(self):
        """Test global register_alias function."""
        register_singleton("target_service", "target_value")
        register_alias("global_alias", "target_service")
        
        container = get_container()
        assert container.has("global_alias")
        assert container.get("global_alias") == "target_value"
    
    def test_get_service_global(self):
        """Test global get_service function."""
        register_singleton("global_service", "global_value")
        
        service = get_service("global_service")
        assert service == "global_value"
    
    def test_inject_into_global(self):
        """Test global inject_into function."""
        register_singleton("global_service", "global_value")
        
        plugin = MockPlugin()
        inject_into(plugin, ["global_service"])
        
        assert plugin.has_dependency("global_service")
        assert plugin.get_dependency("global_service") == "global_value"
    
    def test_inject_into_plugin_global(self):
        """Test global inject_into_plugin function."""
        register_singleton("global_service", "global_value")
        
        plugin = MockPlugin()
        plugin.dependencies = ["global_service"]
        
        inject_into_plugin(plugin)
        
        assert plugin.has_dependency("global_service")
        assert plugin.get_dependency("global_service") == "global_value"
    
    def test_get_container_global(self):
        """Test global get_container function."""
        container = get_container()
        assert isinstance(container, DependencyContainer)
    
    def test_get_injector_global(self):
        """Test global get_injector function."""
        injector = get_injector()
        assert isinstance(injector, DependencyInjector)
