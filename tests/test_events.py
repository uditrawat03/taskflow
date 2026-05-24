# tests/test_events.py — Tests for taskflow/events.py (Observer / Event Bus)
import pytest
from taskflow.events import EventBus, Events, event_bus
from taskflow.core.task import Task


@pytest.fixture
def bus() -> EventBus:
    """Fresh EventBus for each test — independent of the global event_bus."""
    b = EventBus()
    yield b
    b.clear()


class TestEventBus:
    def test_emit_calls_handler(self, bus):
        received = []
        bus.subscribe("test.event", lambda x: received.append(x))
        bus.emit("test.event", "payload")
        assert received == ["payload"]

    def test_multiple_handlers_all_called(self, bus):
        called = []
        bus.subscribe("test.event", lambda: called.append("a"))
        bus.subscribe("test.event", lambda: called.append("b"))
        bus.emit("test.event")
        assert called == ["a", "b"]

    def test_emit_no_subscribers_no_raise(self, bus):
        bus.emit("no.subscribers")  # must not raise

    def test_handler_error_does_not_stop_others(self, bus):
        called = []

        def bad_handler():
            raise RuntimeError("Broken")

        def good_handler():
            called.append("good")

        bus.subscribe("test.event", bad_handler)
        bus.subscribe("test.event", good_handler)
        bus.emit("test.event")
        assert "good" in called

    def test_decorator_registration(self, bus):
        @bus.on("task.added")
        def handler(task): pass
        assert handler in bus.handlers_for("task.added")

    def test_unsubscribe(self, bus):
        received = []
        handler  = lambda x: received.append(x)
        bus.subscribe("test.event", handler)
        bus.unsubscribe("test.event", handler)
        bus.emit("test.event", "payload")
        assert received == []

    def test_unsubscribe_nonexistent_no_raise(self, bus):
        bus.unsubscribe("test.event", lambda: None)  # must not raise

    def test_clear_specific_event(self, bus):
        bus.subscribe("event.a", lambda: None)
        bus.subscribe("event.b", lambda: None)
        bus.clear("event.a")
        assert bus.handlers_for("event.a") == []
        assert len(bus.handlers_for("event.b")) == 1

    def test_clear_all(self, bus):
        bus.subscribe("event.a", lambda: None)
        bus.subscribe("event.b", lambda: None)
        bus.clear()
        assert bus.handlers_for("event.a") == []
        assert bus.handlers_for("event.b") == []

    def test_repr(self, bus):
        bus.subscribe("event.x", lambda: None)
        r = repr(bus)
        assert "EventBus" in r
        assert "1" in r

    def test_handlers_for_returns_copy(self, bus):
        bus.subscribe("test", lambda: None)
        copy = bus.handlers_for("test")
        copy.clear()
        assert len(bus.handlers_for("test")) == 1

    def test_emit_with_kwargs(self, bus):
        received = []
        bus.subscribe("test", lambda task, extra=None: received.append((task, extra)))
        bus.emit("test", "mytask", extra="val")
        assert received == [("mytask", "val")]


class TestEventsConstants:
    def test_all_event_names_are_strings(self):
        for attr in ["TASK_ADDED","TASK_DONE","TASK_REMOVED","TASK_RENAMED",
                     "LIMIT_REACHED","STORAGE_SAVED","STORAGE_ERROR"]:
            value = getattr(Events, attr)
            assert isinstance(value, str)
            assert "." in value

    def test_event_names_are_unique(self):
        names = [v for k, v in Events.__dict__.items() if not k.startswith("_")]
        assert len(names) == len(set(names))


class TestGlobalEventBus:
    def test_global_event_bus_is_eventbus(self):
        assert isinstance(event_bus, EventBus)

    def test_global_bus_cleared_between_tests(self):
        # autouse fixture in conftest clears the bus — handlers should be empty
        handlers = event_bus.handlers_for(Events.TASK_ADDED)
        assert handlers == []

    def test_subscribe_and_emit_global(self):
        received = []
        event_bus.subscribe(Events.TASK_ADDED, lambda t: received.append(t.title))
        task = Task("Test task", "high", "work")
        event_bus.emit(Events.TASK_ADDED, task)
        assert received == ["Test task"]