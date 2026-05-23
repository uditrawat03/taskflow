# tests/test_decorators.py
import time
import pytest
from taskflow.decorators import timer, retry, validate_non_empty, log_call
from taskflow.errors import ValidationError


class TestTimer:
    def test_timer_returns_function_result(self):
        @timer(label="test")
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_timer_preserves_function_name(self):
        @timer(label="test")
        def my_function():
            pass

        assert my_function.__name__ == "my_function"

    def test_timer_prints_output(self, capsys):
        @timer(label="TestOp")
        def noop():
            pass

        noop()
        captured = capsys.readouterr()
        assert "TestOp" in captured.out

    def test_timer_uses_function_name_when_no_label(self, capsys):
        @timer()
        def my_operation():
            pass

        my_operation()
        captured = capsys.readouterr()
        assert "my_operation" in captured.out


class TestRetry:
    def test_succeeds_on_first_attempt(self):
        call_count = 0

        @retry(times=3, delay=0)
        def succeed():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = succeed()
        assert result == "ok"
        assert call_count == 1

    def test_retries_on_failure_then_succeeds(self):
        attempts = []

        @retry(times=3, delay=0, exceptions=(ValueError,))
        def fail_twice_then_succeed():
            attempts.append(1)
            if len(attempts) < 3:
                raise ValueError("Not yet")
            return "success"

        result = fail_twice_then_succeed()
        assert result == "success"
        assert len(attempts) == 3

    def test_raises_after_max_retries(self):
        @retry(times=2, delay=0, exceptions=(ValueError,))
        def always_fail():
            raise ValueError("Always")

        with pytest.raises(ValueError):
            always_fail()

    def test_does_not_retry_unexpected_exception(self):
        call_count = 0

        @retry(times=3, delay=0, exceptions=(ValueError,))
        def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("Not retried")

        with pytest.raises(TypeError):
            raise_type_error()

        assert call_count == 1  # no retries for TypeError


class TestValidateNonEmpty:
    def test_passes_through_when_tasks_present(self, one_task):
        @validate_non_empty
        def cmd(tasks):
            return "executed"

        assert cmd(one_task) == "executed"

    def test_returns_none_and_prints_when_empty(self, empty_tasks, capsys):
        @validate_non_empty
        def cmd(tasks):
            return "executed"

        result = cmd(empty_tasks)
        assert result is None
        captured = capsys.readouterr()
        assert "No tasks" in captured.out

    def test_preserves_function_name(self):
        @validate_non_empty
        def my_command(tasks):
            pass

        assert my_command.__name__ == "my_command"


class TestLogCall:
    def test_returns_function_result(self):
        @log_call(level="debug")
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_logs_call_and_return(self, caplog):
        import logging

        @log_call(level="debug")
        def multiply(a, b):
            return a * b

        with caplog.at_level(logging.DEBUG):
            result = multiply(3, 4)

        assert result == 12
        log_messages = [r.message for r in caplog.records]
        assert any("[call]" in m for m in log_messages)
        assert any("[return]" in m for m in log_messages)
