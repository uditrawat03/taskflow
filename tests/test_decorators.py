# tests/test_decorators.py — Tests for taskflow/decorators.py
import time
import pytest
from unittest.mock import call
from taskflow.decorators import timer, retry, validate_non_empty, log_call, deprecated
from taskflow.errors import ValidationError


class TestTimer:
    def test_returns_function_result(self):
        @timer(label="test")
        def add(a, b): return a + b
        assert add(2, 3) == 5

    def test_preserves_function_name(self):
        @timer(label="test")
        def my_function(): pass
        assert my_function.__name__ == "my_function"

    def test_prints_output(self, capsys):
        @timer(label="TestOp")
        def noop(): pass
        noop()
        assert "TestOp" in capsys.readouterr().out

    def test_uses_function_name_when_no_label(self, capsys):
        @timer()
        def my_operation(): pass
        my_operation()
        assert "my_operation" in capsys.readouterr().out

    def test_passes_args_correctly(self):
        @timer()
        def concat(a, b): return a + b
        assert concat("hello", " world") == "hello world"


class TestRetry:
    def test_succeeds_first_attempt(self):
        calls = []

        @retry(times=3, delay=0)
        def succeed():
            calls.append(1)
            return "ok"

        assert succeed() == "ok"
        assert len(calls) == 1

    def test_retries_on_failure_then_succeeds(self):
        attempts = []

        @retry(times=3, delay=0, exceptions=(ValueError,))
        def fail_twice():
            attempts.append(1)
            if len(attempts) < 3:
                raise ValueError("Not yet")
            return "success"

        assert fail_twice() == "success"
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

        assert call_count == 1

    def test_exponential_backoff(self, mocker):
        mock_sleep = mocker.patch("time.sleep")

        @retry(times=3, delay=1.0, backoff=2.0, exceptions=(ValueError,))
        def always_fail():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            always_fail()

        assert mock_sleep.call_count == 2
        assert mock_sleep.call_args_list[0] == call(1.0)
        assert mock_sleep.call_args_list[1] == call(2.0)


class TestValidateNonEmpty:
    def test_passes_with_tasks(self, one_task):
        @validate_non_empty
        def cmd(tasks): return "executed"
        assert cmd(one_task) == "executed"

    def test_returns_none_when_empty(self, empty_tasks, capsys):
        @validate_non_empty
        def cmd(tasks): return "executed"
        result = cmd(empty_tasks)
        assert result is None
        assert "No tasks" in capsys.readouterr().out

    def test_preserves_function_name(self):
        @validate_non_empty
        def my_command(tasks): pass
        assert my_command.__name__ == "my_command"

    def test_passes_extra_args(self, one_task):
        @validate_non_empty
        def cmd(tasks, extra): return extra
        assert cmd(one_task, "hello") == "hello"


class TestLogCall:
    def test_returns_function_result(self):
        @log_call(level="debug")
        def add(a, b): return a + b
        assert add(2, 3) == 5

    def test_logs_call_and_return(self, caplog):
        import logging

        @log_call(level="debug")
        def multiply(a, b): return a * b

        with caplog.at_level(logging.DEBUG):
            result = multiply(3, 4)

        assert result == 12
        messages = [r.message for r in caplog.records]
        assert any("[call]"   in m for m in messages)
        assert any("[return]" in m for m in messages)

    def test_preserves_function_name(self):
        @log_call()
        def named_function(): pass
        assert named_function.__name__ == "named_function"


class TestDeprecated:
    def test_still_executes(self):
        @deprecated("Use new_func() instead.")
        def old_func(): return 42
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            assert old_func() == 42

    def test_emits_deprecation_warning(self):
        @deprecated("Use new_func() instead.")
        def old_func(): pass
        with pytest.warns(DeprecationWarning, match="deprecated"):
            old_func()

    def test_message_in_warning(self):
        @deprecated("Use new_func() instead.")
        def old_func(): pass
        with pytest.warns(DeprecationWarning) as record:
            old_func()
        assert "Use new_func()" in str(record[0].message)