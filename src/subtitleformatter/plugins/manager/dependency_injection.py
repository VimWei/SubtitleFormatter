"""
Dependency injection system for SubtitleFormatter plugins.

This module provides a dependency injection container that manages
dependencies and automatically injects them into plugins.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, TypeVar

from ...utils.unified_logger import logger

T = TypeVar('T')


class DependencyContainer:
    """
    Dependency injection container for managing and injecting dependencies.
    
    This class provides a centralized way to manage dependencies and
    automatically inject them into plugins and other components.
    """
    
    def __init__(self):
        """Initialize the dependency container."""
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._aliases: Dict[str, str] = {}
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Register a singleton instance.
        
        Args:
            name: Service name
            instance: Service instance
        """
        self._services[name] = instance
        self._singletons[name] = instance
        logger.debug(f"Registered singleton: {name}")
    
    def register_factory(self, name: str, factory: callable) -> None:
        """
        Register a factory function for creating instances.
        
        Args:
            name: Service name
            factory: Factory function that creates the service instance
        """
        self._factories[name] = factory
        logger.debug(f"Registered factory: {name}")
    
    def register_alias(self, alias: str, target: str) -> None:
        """
        Register an alias for a service.
        
        Args:
            alias: Alias name
            target: Target service name
        """
        self._aliases[alias] = target
        logger.debug(f"Registered alias: {alias} -> {target}")
    
    def get(self, name: str) -> Any:
        """
        Get a service by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not found
        """
        # Resolve alias if exists
        actual_name = self._aliases.get(name, name)
        
        # Return singleton if exists
        if actual_name in self._singletons:
            return self._singletons[actual_name]
        
        # Create from factory if exists
        if actual_name in self._factories:
            instance = self._factories[actual_name]()
            self._singletons[actual_name] = instance
            return instance
        
        # Return registered service
        if actual_name in self._services:
            return self._services[actual_name]
        
        raise KeyError(f"Service '{name}' not found")
    
    def get_typed(self, name: str, service_type: Type[T]) -> T:
        """
        Get a service with type checking.
        
        Args:
            name: Service name
            service_type: Expected service type
            
        Returns:
            Service instance with type checking
            
        Raises:
            KeyError: If service not found
            TypeError: If service type doesn't match
        """
        instance = self.get(name)
        if not isinstance(instance, service_type):
            raise TypeError(f"Service '{name}' is not of type {service_type.__name__}")
        return instance
    
    def has(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: Service name
            
        Returns:
            True if service is registered, False otherwise
        """
        actual_name = self._aliases.get(name, name)
        return (actual_name in self._services or 
                actual_name in self._factories or 
                actual_name in self._singletons)
    
    def list_services(self) -> List[str]:
        """
        List all registered service names.
        
        Returns:
            List of service names
        """
        services = set(self._services.keys())
        services.update(self._factories.keys())
        services.update(self._aliases.keys())
        return list(services)
    
    def remove(self, name: str) -> None:
        """
        Remove a service registration.
        
        Args:
            name: Service name
        """
        actual_name = self._aliases.get(name, name)
        
        # Remove from all registries
        self._services.pop(actual_name, None)
        self._singletons.pop(actual_name, None)
        self._factories.pop(actual_name, None)
        
        # Remove aliases pointing to this service
        aliases_to_remove = [alias for alias, target in self._aliases.items() if target == actual_name]
        for alias in aliases_to_remove:
            del self._aliases[alias]
        
        logger.debug(f"Removed service: {name}")
    
    def clear(self) -> None:
        """Clear all service registrations."""
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()
        self._aliases.clear()
        logger.debug("Cleared all services")


class DependencyInjector:
    """
    Dependency injector for automatically injecting dependencies into objects.
    
    This class provides methods to automatically inject dependencies
    into plugin instances and other objects.
    """
    
    def __init__(self, container: DependencyContainer):
        """
        Initialize the dependency injector.
        
        Args:
            container: Dependency container to use for injection
        """
        self.container = container
    
    def inject_into(self, target: Any, dependencies: Optional[List[str]] = None) -> None:
        """
        Inject dependencies into a target object.
        
        Args:
            target: Target object to inject dependencies into
            dependencies: List of dependency names to inject (if None, inject all available)
        """
        if dependencies is None:
            dependencies = self.container.list_services()
        
        for dep_name in dependencies:
            try:
                if self.container.has(dep_name):
                    dep_instance = self.container.get(dep_name)
                    
                    # Try to set dependency using set_dependency method
                    if hasattr(target, 'set_dependency'):
                        target.set_dependency(dep_name, dep_instance)
                    # Try to set as attribute
                    elif hasattr(target, dep_name):
                        setattr(target, dep_name, dep_instance)
                    else:
                        logger.warning(f"Cannot inject dependency '{dep_name}' into {type(target).__name__}")
                        
            except Exception as e:
                logger.error(f"Failed to inject dependency '{dep_name}': {e}")
    
    def inject_into_plugin(self, plugin: Any) -> None:
        """
        Inject dependencies into a plugin instance.
        
        Args:
            plugin: Plugin instance to inject dependencies into
        """
        if hasattr(plugin, 'dependencies') and plugin.dependencies:
            # Inject only required dependencies
            self.inject_into(plugin, plugin.dependencies)
        else:
            # Inject all available dependencies
            self.inject_into(plugin)
    
    def create_with_injection(self, class_type: Type[T], *args, **kwargs) -> T:
        """
        Create an instance and inject dependencies.
        
        Args:
            class_type: Class to instantiate
            *args: Positional arguments for constructor
            **kwargs: Keyword arguments for constructor
            
        Returns:
            Created instance with dependencies injected
        """
        instance = class_type(*args, **kwargs)
        self.inject_into(instance)
        return instance


# Global dependency container instance
_dependency_container = DependencyContainer()
_dependency_injector = DependencyInjector(_dependency_container)


def get_container() -> DependencyContainer:
    """Get the global dependency container."""
    return _dependency_container


def get_injector() -> DependencyInjector:
    """Get the global dependency injector."""
    return _dependency_injector


def register_singleton(name: str, instance: Any) -> None:
    """Register a singleton in the global container."""
    _dependency_container.register_singleton(name, instance)


def register_factory(name: str, factory: callable) -> None:
    """Register a factory in the global container."""
    _dependency_container.register_factory(name, factory)


def register_alias(alias: str, target: str) -> None:
    """Register an alias in the global container."""
    _dependency_container.register_alias(alias, target)


def get_service(name: str) -> Any:
    """Get a service from the global container."""
    return _dependency_container.get(name)


def get_typed_service(name: str, service_type: Type[T]) -> T:
    """Get a typed service from the global container."""
    return _dependency_container.get_typed(name, service_type)


def inject_into(target: Any, dependencies: Optional[List[str]] = None) -> None:
    """Inject dependencies into a target object."""
    _dependency_injector.inject_into(target, dependencies)


def inject_into_plugin(plugin: Any) -> None:
    """Inject dependencies into a plugin instance."""
    _dependency_injector.inject_into_plugin(plugin)
