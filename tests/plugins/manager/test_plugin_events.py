"""
Tests for PluginEventSystem.
"""

import asyncio
import pytest
from unittest.mock import Mock

from subtitleformatter.plugins import (
    PluginEvent,
    PluginEventSystem,
    PluginEventBus,
    create_event_bus,
    get_event_system
)


class TestPluginEvent:
    """Test cases for PluginEvent."""
    
    def test_event_creation(self):
        """Test event creation."""
        event = PluginEvent("test_event", "test_data", "test_source")
        
        assert event.name == "test_event"
        assert event.data == "test_data"
        assert event.source == "test_source"
        assert event.timestamp >= 0
    
    def test_event_creation_minimal(self):
        """Test event creation with minimal parameters."""
        event = PluginEvent("test_event")
        
        assert event.name == "test_event"
        assert event.data is None
        assert event.source is None
        assert event.timestamp >= 0
    
    def test_event_string_representation(self):
        """Test event string representation."""
        event = PluginEvent("test_event", "test_data", "test_source")
        str_repr = str(event)
        
        assert "test_event" in str_repr
        assert "test_source" in str_repr
        assert "test_data" in str_repr
    
    def test_event_repr(self):
        """Test event detailed representation."""
        event = PluginEvent("test_event", "test_data", "test_source")
        repr_str = repr(event)
        
        assert "PluginEvent" in repr_str
        assert "test_event" in repr_str
        assert "test_source" in repr_str
        assert "test_data" in repr_str


class TestPluginEventSystem:
    """Test cases for PluginEventSystem."""
    
    def test_event_system_creation(self):
        """Test event system creation."""
        event_system = PluginEventSystem()
        
        assert event_system._handlers == {}
        assert event_system._wildcard_handlers == []
        assert event_system._event_history == []
        assert event_system._max_history == 1000
        assert event_system._enabled
    
    def test_register_handler(self):
        """Test registering event handler."""
        event_system = PluginEventSystem()
        
        def handler(event):
            pass
        
        event_system.register_handler("test_event", handler)
        
        assert "test_event" in event_system._handlers
        assert handler in event_system._handlers["test_event"]
    
    def test_register_multiple_handlers(self):
        """Test registering multiple handlers for same event."""
        event_system = PluginEventSystem()
        
        def handler1(event):
            pass
        
        def handler2(event):
            pass
        
        event_system.register_handler("test_event", handler1)
        event_system.register_handler("test_event", handler2)
        
        assert len(event_system._handlers["test_event"]) == 2
        assert handler1 in event_system._handlers["test_event"]
        assert handler2 in event_system._handlers["test_event"]
    
    def test_register_wildcard_handler(self):
        """Test registering wildcard handler."""
        event_system = PluginEventSystem()
        
        def handler(event):
            pass
        
        event_system.register_wildcard_handler(handler)
        
        assert handler in event_system._wildcard_handlers
    
    def test_unregister_handler(self):
        """Test unregistering event handler."""
        event_system = PluginEventSystem()
        
        def handler(event):
            pass
        
        event_system.register_handler("test_event", handler)
        assert handler in event_system._handlers["test_event"]
        
        event_system.unregister_handler("test_event", handler)
        assert handler not in event_system._handlers["test_event"]
    
    def test_unregister_wildcard_handler(self):
        """Test unregistering wildcard handler."""
        event_system = PluginEventSystem()
        
        def handler(event):
            pass
        
        event_system.register_wildcard_handler(handler)
        assert handler in event_system._wildcard_handlers
        
        event_system.unregister_wildcard_handler(handler)
        assert handler not in event_system._wildcard_handlers
    
    def test_emit_event(self):
        """Test emitting event."""
        event_system = PluginEventSystem()
        
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        event_system.register_handler("test_event", handler)
        event_system.emit("test_event", "test_data", "test_source")
        
        assert len(received_events) == 1
        assert received_events[0].name == "test_event"
        assert received_events[0].data == "test_data"
        assert received_events[0].source == "test_source"
    
    def test_emit_event_multiple_handlers(self):
        """Test emitting event to multiple handlers."""
        event_system = PluginEventSystem()
        
        received_events1 = []
        received_events2 = []
        
        def handler1(event):
            received_events1.append(event)
        
        def handler2(event):
            received_events2.append(event)
        
        event_system.register_handler("test_event", handler1)
        event_system.register_handler("test_event", handler2)
        
        event_system.emit("test_event", "test_data")
        
        assert len(received_events1) == 1
        assert len(received_events2) == 1
        assert received_events1[0].name == "test_event"
        assert received_events2[0].name == "test_event"
    
    def test_emit_event_wildcard_handler(self):
        """Test emitting event to wildcard handler."""
        event_system = PluginEventSystem()
        
        received_events = []
        
        def wildcard_handler(event):
            received_events.append(event)
        
        event_system.register_wildcard_handler(wildcard_handler)
        event_system.emit("test_event", "test_data")
        
        assert len(received_events) == 1
        assert received_events[0].name == "test_event"
        assert received_events[0].data == "test_data"
    
    def test_emit_event_handler_error(self):
        """Test emitting event when handler raises error."""
        event_system = PluginEventSystem()
        
        received_events = []
        
        def error_handler(event):
            raise Exception("Handler error")
        
        def normal_handler(event):
            received_events.append(event)
        
        event_system.register_handler("test_event", error_handler)
        event_system.register_handler("test_event", normal_handler)
        
        # Should not raise error, normal handler should still be called
        event_system.emit("test_event", "test_data")
        
        assert len(received_events) == 1
        assert received_events[0].name == "test_event"
    
    def test_emit_event_disabled(self):
        """Test emitting event when system is disabled."""
        event_system = PluginEventSystem()
        event_system.disable()
        
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        event_system.register_handler("test_event", handler)
        event_system.emit("test_event", "test_data")
        
        assert len(received_events) == 0
    
    def test_emit_async_event(self):
        """Test emitting async event."""
        event_system = PluginEventSystem()
        
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        event_system.register_handler("test_event", handler)
        
        # Run in event loop
        async def test_emit():
            event_system.emit_async("test_event", "test_data")
            # Give time for async handlers to run
            await asyncio.sleep(0.01)
        
        asyncio.run(test_emit())
        
        assert len(received_events) == 1
        assert received_events[0].name == "test_event"
        assert received_events[0].data == "test_data"
    
    def test_event_history(self):
        """Test event history tracking."""
        event_system = PluginEventSystem()
        
        def handler(event):
            pass
        
        event_system.register_handler("test_event", handler)
        
        event_system.emit("test_event", "data1")
        event_system.emit("test_event", "data2")
        event_system.emit("other_event", "data3")
        
        history = event_system.get_event_history()
        assert len(history) == 3
        
        history_by_name = event_system.get_event_history("test_event")
        assert len(history_by_name) == 2
        
        history_limited = event_system.get_event_history(limit=2)
        assert len(history_limited) == 2
    
    def test_clear_event_history(self):
        """Test clearing event history."""
        event_system = PluginEventSystem()
        
        def handler(event):
            pass
        
        event_system.register_handler("test_event", handler)
        event_system.emit("test_event", "test_data")
        
        assert len(event_system._event_history) == 1
        
        event_system.clear_event_history()
        
        assert len(event_system._event_history) == 0
    
    def test_list_registered_events(self):
        """Test listing registered events."""
        event_system = PluginEventSystem()
        
        def handler(event):
            pass
        
        event_system.register_handler("event1", handler)
        event_system.register_handler("event2", handler)
        
        events = event_system.list_registered_events()
        
        assert set(events) == {"event1", "event2"}
    
    def test_get_handler_count(self):
        """Test getting handler count for event."""
        event_system = PluginEventSystem()
        
        def handler1(event):
            pass
        
        def handler2(event):
            pass
        
        event_system.register_handler("test_event", handler1)
        event_system.register_handler("test_event", handler2)
        
        count = event_system.get_handler_count("test_event")
        assert count == 2
        
        count = event_system.get_handler_count("nonexistent_event")
        assert count == 0
    
    def test_enable_disable(self):
        """Test enabling and disabling event system."""
        event_system = PluginEventSystem()
        
        assert event_system.is_enabled()
        
        event_system.disable()
        assert not event_system.is_enabled()
        
        event_system.enable()
        assert event_system.is_enabled()
    
    def test_set_max_history(self):
        """Test setting max history."""
        event_system = PluginEventSystem()
        
        assert event_system._max_history == 1000
        
        event_system.set_max_history(500)
        assert event_system._max_history == 500


class TestPluginEventBus:
    """Test cases for PluginEventBus."""
    
    def test_event_bus_creation(self):
        """Test event bus creation."""
        event_system = PluginEventSystem()
        event_bus = PluginEventBus(event_system, "test_plugin")
        
        assert event_bus.event_system == event_system
        assert event_bus.plugin_name == "test_plugin"
        assert event_bus._registered_handlers == set()
    
    def test_emit_event(self):
        """Test emitting event from event bus."""
        event_system = PluginEventSystem()
        event_bus = PluginEventBus(event_system, "test_plugin")
        
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        event_system.register_handler("test_event", handler)
        
        event_bus.emit("test_event", "test_data")
        
        assert len(received_events) == 1
        assert received_events[0].name == "test_event"
        assert received_events[0].data == "test_data"
        assert received_events[0].source == "test_plugin"
    
    def test_emit_async_event(self):
        """Test emitting async event from event bus."""
        event_system = PluginEventSystem()
        event_bus = PluginEventBus(event_system, "test_plugin")
        
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        event_system.register_handler("test_event", handler)
        
        async def test_emit():
            event_bus.emit_async("test_event", "test_data")
            await asyncio.sleep(0.01)
        
        asyncio.run(test_emit())
        
        assert len(received_events) == 1
        assert received_events[0].name == "test_event"
        assert received_events[0].data == "test_data"
        assert received_events[0].source == "test_plugin"
    
    def test_listen_to_event(self):
        """Test listening to event from event bus."""
        event_system = PluginEventSystem()
        event_bus = PluginEventBus(event_system, "test_plugin")
        
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        event_bus.listen("test_event", handler)
        
        assert "test_event" in event_bus._registered_handlers
        assert handler in event_system._handlers["test_event"]
    
    def test_listen_to_all_events(self):
        """Test listening to all events from event bus."""
        event_system = PluginEventSystem()
        event_bus = PluginEventBus(event_system, "test_plugin")
        
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        event_bus.listen_to_all(handler)
        
        assert handler in event_system._wildcard_handlers
    
    def test_stop_listening(self):
        """Test stopping listening to event from event bus."""
        event_system = PluginEventSystem()
        event_bus = PluginEventBus(event_system, "test_plugin")
        
        def handler(event):
            pass
        
        event_bus.listen("test_event", handler)
        assert "test_event" in event_bus._registered_handlers
        
        event_bus.stop_listening("test_event", handler)
        assert "test_event" not in event_bus._registered_handlers
    
    def test_cleanup(self):
        """Test cleaning up event bus."""
        event_system = PluginEventSystem()
        event_bus = PluginEventBus(event_system, "test_plugin")
        
        def handler(event):
            pass
        
        event_bus.listen("test_event", handler)
        assert "test_event" in event_bus._registered_handlers
        
        event_bus.cleanup()
        assert len(event_bus._registered_handlers) == 0


class TestGlobalFunctions:
    """Test cases for global event system functions."""
    
    def test_get_event_system(self):
        """Test getting global event system."""
        event_system = get_event_system()
        assert isinstance(event_system, PluginEventSystem)
    
    def test_create_event_bus(self):
        """Test creating event bus."""
        event_bus = create_event_bus("test_plugin")
        assert isinstance(event_bus, PluginEventBus)
        assert event_bus.plugin_name == "test_plugin"
