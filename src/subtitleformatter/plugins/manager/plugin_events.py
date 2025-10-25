"""
Plugin event system for SubtitleFormatter.

This module provides an event system for plugins to communicate with each other
and with the main application through events and callbacks.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional, Set, Union

from ...utils.unified_logger import logger


class PluginEvent:
    """
    Plugin event class for carrying event data.
    
    This class represents an event that can be emitted and handled by plugins.
    """
    
    def __init__(self, name: str, data: Optional[Any] = None, source: Optional[str] = None):
        """
        Initialize a plugin event.
        
        Args:
            name: Event name
            data: Event data
            source: Event source (plugin name)
        """
        self.name = name
        self.data = data
        self.source = source
        self.timestamp = 0  # Use simple timestamp for now
    
    def __str__(self) -> str:
        """String representation of the event."""
        return f"PluginEvent(name='{self.name}', source='{self.source}', data={self.data})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the event."""
        return f"PluginEvent(name='{self.name}', source='{self.source}', timestamp={self.timestamp}, data={self.data})"


class PluginEventSystem:
    """
    Plugin event system for managing events and callbacks.
    
    This class provides a centralized event system that allows plugins to
    emit events and register event handlers.
    """
    
    def __init__(self):
        """Initialize the plugin event system."""
        self._handlers: Dict[str, List[Callable[[PluginEvent], None]]] = {}
        self._wildcard_handlers: List[Callable[[PluginEvent], None]] = []
        self._event_history: List[PluginEvent] = []
        self._max_history = 1000
        self._enabled = True
    
    def register_handler(self, event_name: str, handler: Callable[[PluginEvent], None]) -> None:
        """
        Register an event handler.
        
        Args:
            event_name: Name of the event to handle
            handler: Handler function that takes a PluginEvent and returns None
        """
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        
        self._handlers[event_name].append(handler)
        logger.debug(f"Registered handler for event '{event_name}'")
    
    def register_wildcard_handler(self, handler: Callable[[PluginEvent], None]) -> None:
        """
        Register a wildcard handler that receives all events.
        
        Args:
            handler: Handler function that takes a PluginEvent and returns None
        """
        self._wildcard_handlers.append(handler)
        logger.debug("Registered wildcard event handler")
    
    def unregister_handler(self, event_name: str, handler: Callable[[PluginEvent], None]) -> None:
        """
        Unregister an event handler.
        
        Args:
            event_name: Name of the event
            handler: Handler function to remove
        """
        if event_name in self._handlers:
            if handler in self._handlers[event_name]:
                self._handlers[event_name].remove(handler)
                logger.debug(f"Unregistered handler for event '{event_name}'")
    
    def unregister_wildcard_handler(self, handler: Callable[[PluginEvent], None]) -> None:
        """
        Unregister a wildcard handler.
        
        Args:
            handler: Handler function to remove
        """
        if handler in self._wildcard_handlers:
            self._wildcard_handlers.remove(handler)
            logger.debug("Unregistered wildcard event handler")
    
    def emit(self, event_name: str, data: Optional[Any] = None, source: Optional[str] = None) -> None:
        """
        Emit an event.
        
        Args:
            event_name: Name of the event
            data: Event data
            source: Event source (plugin name)
        """
        if not self._enabled:
            return
        
        event = PluginEvent(event_name, data, source)
        
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Call specific handlers
        if event_name in self._handlers:
            for handler in self._handlers[event_name]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for '{event_name}': {e}")
        
        # Call wildcard handlers
        for handler in self._wildcard_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in wildcard event handler: {e}")
        
        logger.debug(f"Emitted event '{event_name}' from '{source}'")
    
    def emit_async(self, event_name: str, data: Optional[Any] = None, source: Optional[str] = None) -> None:
        """
        Emit an event asynchronously.
        
        Args:
            event_name: Name of the event
            data: Event data
            source: Event source (plugin name)
        """
        if not self._enabled:
            return
        
        event = PluginEvent(event_name, data, source)
        
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Schedule handlers to run asynchronously
        loop = asyncio.get_event_loop()
        
        # Call specific handlers
        if event_name in self._handlers:
            for handler in self._handlers[event_name]:
                loop.create_task(self._call_handler_async(handler, event))
        
        # Call wildcard handlers
        for handler in self._wildcard_handlers:
            loop.create_task(self._call_handler_async(handler, event))
        
        logger.debug(f"Emitted async event '{event_name}' from '{source}'")
    
    async def _call_handler_async(self, handler: Callable[[PluginEvent], None], event: PluginEvent) -> None:
        """
        Call a handler asynchronously.
        
        Args:
            handler: Handler function
            event: Event to pass to handler
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Error in async event handler: {e}")
    
    def get_event_history(self, event_name: Optional[str] = None, limit: Optional[int] = None) -> List[PluginEvent]:
        """
        Get event history.
        
        Args:
            event_name: Optional event name to filter by
            limit: Optional limit on number of events to return
            
        Returns:
            List of events
        """
        events = self._event_history
        
        if event_name:
            events = [e for e in events if e.name == event_name]
        
        if limit:
            events = events[-limit:]
        
        return events
    
    def clear_event_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
        logger.debug("Cleared event history")
    
    def list_registered_events(self) -> List[str]:
        """
        List all registered event names.
        
        Returns:
            List of event names
        """
        return list(self._handlers.keys())
    
    def get_handler_count(self, event_name: str) -> int:
        """
        Get the number of handlers for an event.
        
        Args:
            event_name: Name of the event
            
        Returns:
            Number of handlers
        """
        return len(self._handlers.get(event_name, []))
    
    def enable(self) -> None:
        """Enable the event system."""
        self._enabled = True
        logger.debug("Plugin event system enabled")
    
    def disable(self) -> None:
        """Disable the event system."""
        self._enabled = False
        logger.debug("Plugin event system disabled")
    
    def is_enabled(self) -> bool:
        """
        Check if the event system is enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        return self._enabled
    
    def set_max_history(self, max_history: int) -> None:
        """
        Set the maximum number of events to keep in history.
        
        Args:
            max_history: Maximum number of events
        """
        self._max_history = max_history
        logger.debug(f"Set max event history to {max_history}")


class PluginEventBus:
    """
    Plugin event bus for managing plugin-specific events.
    
    This class provides a simplified interface for plugins to emit and
    listen to events without directly managing the event system.
    """
    
    def __init__(self, event_system: PluginEventSystem, plugin_name: str):
        """
        Initialize the plugin event bus.
        
        Args:
            event_system: Plugin event system instance
            plugin_name: Name of the plugin
        """
        self.event_system = event_system
        self.plugin_name = plugin_name
        self._registered_handlers: Set[str] = set()
    
    def emit(self, event_name: str, data: Optional[Any] = None) -> None:
        """
        Emit an event from this plugin.
        
        Args:
            event_name: Name of the event
            data: Event data
        """
        self.event_system.emit(event_name, data, self.plugin_name)
    
    def emit_async(self, event_name: str, data: Optional[Any] = None) -> None:
        """
        Emit an event asynchronously from this plugin.
        
        Args:
            event_name: Name of the event
            data: Event data
        """
        self.event_system.emit_async(event_name, data, self.plugin_name)
    
    def listen(self, event_name: str, handler: Callable[[PluginEvent], None]) -> None:
        """
        Listen to an event.
        
        Args:
            event_name: Name of the event to listen to
            handler: Handler function
        """
        self.event_system.register_handler(event_name, handler)
        self._registered_handlers.add(event_name)
        logger.debug(f"Plugin '{self.plugin_name}' listening to event '{event_name}'")
    
    def listen_to_all(self, handler: Callable[[PluginEvent], None]) -> None:
        """
        Listen to all events.
        
        Args:
            handler: Handler function
        """
        self.event_system.register_wildcard_handler(handler)
        logger.debug(f"Plugin '{self.plugin_name}' listening to all events")
    
    def stop_listening(self, event_name: str, handler: Callable[[PluginEvent], None]) -> None:
        """
        Stop listening to an event.
        
        Args:
            event_name: Name of the event
            handler: Handler function
        """
        self.event_system.unregister_handler(event_name, handler)
        self._registered_handlers.discard(event_name)
        logger.debug(f"Plugin '{self.plugin_name}' stopped listening to event '{event_name}'")
    
    def cleanup(self) -> None:
        """Clean up all registered handlers for this plugin."""
        # Note: This is a simplified cleanup - in a real implementation,
        # you'd need to track handler instances to properly unregister them
        self._registered_handlers.clear()
        logger.debug(f"Cleaned up event handlers for plugin '{self.plugin_name}'")


# Global event system instance
_event_system = PluginEventSystem()


def get_event_system() -> PluginEventSystem:
    """Get the global plugin event system."""
    return _event_system


def create_event_bus(plugin_name: str) -> PluginEventBus:
    """Create an event bus for a plugin."""
    return PluginEventBus(_event_system, plugin_name)
