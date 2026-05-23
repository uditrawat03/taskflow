# Day 26 — Test Coverage & Mocking

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Mocking external dependencies, reaching 85% coverage

---

## Learning Objective

By the end of today, you will mock network calls, file I/O failures, and environment variables in tests — making your suite fast, reliable, and independent of external systems. You will also reach 85% test coverage across the entire `taskflow/` package and understand which uncovered lines are acceptable and which are genuine gaps.

---

## What We Build Today

Full test coverage for `integrations/weather.py`, `display/commands.py`, `filters.py`, and `decorators.py` — all of which require mocking to test properly. Plus `tests/test_coverage_report.py`, a meta-test that enforces the coverage gate.

```bash
$ pytest tests/ -v --cov=taskflow --cov-report=term-missing

Name                                    Stmts  Miss  Cover
----------------------------------------------------------
taskflow/core/task.py                      87     4    95%
taskflow/core/task_types.py                92     8    91%
taskflow/core/stats.py                     32     0   100%
taskflow/services.py                       74     6    92%
taskflow/parser.py                         58     5    91%
taskflow/storage/json_store.py             61     8    87%
taskflow/filters.py                        89     9    90%
taskflow/decorators.py                     52     4    92%
taskflow/integrations/weather.py           78    11    86%
taskflow/display/commands.py               94    16    83%
taskflow/logging_config.py                 41     5    88%
taskflow/env_config.py                     55     6    89%
----------------------------------------------------------
TOTAL                                     813    82    90%

====== 78 passed in 1.23s ======
```

---

## Concepts Covered

- `unittest.mock` — `MagicMock`, `patch`, `patch.object`
- `pytest-mock` — `mocker` fixture
- Mocking network requests — `requests.get`
- Mocking file I/O failures — `OSError`
- Mocking `datetime.datetime.now()`
- `monkeypatch` — patching env vars and module attributes
- `caplog` — asserting on log output
- `capsys` — capturing stdout/stderr
- Coverage analysis — understanding missed lines
- Branch coverage vs statement coverage
- Acceptable vs unacceptable coverage gaps
- `# pragma: no cover` — intentional exclusions

---

## Full Tutorial

### What Is Mocking?

Mocking is replacing a real dependency with a fake version that you control during tests. You mock when the real thing:
- Makes a network call (slow, unreliable, costs money)
- Reads or writes files (side effects, requires setup)
- Reads the current time (non-deterministic)
- Is hard to put into a specific error state
- Has a side effect you don't want in tests

The goal is **isolation** — the unit under test should be tested alone, with all its dependencies replaced by mocks that behave exactly as you specify.

---

### `unittest.mock` — The Standard Library Approach

```python
from unittest.mock import MagicMock, patch, call

# MagicMock — a flexible fake object
mock_response = MagicMock()
mock_response.status_code = 200
mock_response.json.return_value = {"current": {"temperature_2m": 38.0}}

# patch — temporarily replace something
with patch("requests.get", return_value=mock_response):
    from taskflow.integrations.weather import _do_fetch_weather
    result = _do_fetch_weather(28.6, 77.2, "Delhi")
    assert result["temperature"] == 38.0

# patch as a decorator
@patch("requests.get")
def test_fetch_weather(mock_get):
    mock_get.return_value = mock_response
    ...

# patch.object — patch a method on a specific object
with patch.object(Path, "exists", return_value=False):
    tasks = load_tasks()
    assert tasks == []
```

---

### `pytest-mock` — The `mocker` Fixture

`pytest-mock` wraps `unittest.mock` in a cleaner fixture-based API:

```bash
pip install pytest-mock
```

```python
def test_weather_fetch(mocker):
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "current": {
            "temperature_2m":      38.0,
            "apparent_temperature": 41.0,
            "relative_humidity_2m": 22,
            "wind_speed_10m":       14.0,
            "weather_code":         0,
        }
    }
    mock_response.raise_for_status = mocker.MagicMock()

    mocker.patch("requests.get", return_value=mock_response)

    from taskflow.integrations.weather import fetch_weather
    result = fetch_weather(28.6, 77.2, "Delhi, IN", use_cache=False)

    assert result is not None
    assert result["temperature"] == 38.0
    assert result["condition"]   == "Clear sky"
    assert result["location"]    == "Delhi, IN"
```

The `mocker` fixture automatically cleans up all patches after each test — no `with` blocks or `@patch` decorators needed.

---

### Building `tests/test_weather.py`

```python
# tests/test_weather.py
# Tests for taskflow/integrations/weather.py
# All network calls are mocked — no real HTTP requests.

import json
import pytest
import requests
from pathlib import Path

from taskflow.integrations.weather import (
    fetch_weather,
    fetch_forecast,
    display_weather,
    get_weather_summary,
    _load_cache,
    _save_cache,
)


# ── Shared mock data ──────────────────────────────────────

MOCK_CURRENT_RESPONSE = {
    "current": {
        "temperature_2m":       38.0,
        "apparent_temperature": 41.0,
        "relative_humidity_2m": 22,
        "wind_speed_10m":       14.0,
        "wind_direction_10m":   315,
        "weather_code":         0,
    }
}

MOCK_FORECAST_RESPONSE = {
    "daily": {
        "time":                         ["2025-05-19", "2025-05-20", "2025-05-21"],
        "temperature_2m_max":           [38.0, 36.0, 33.0],
        "temperature_2m_min":           [28.0, 26.0, 24.0],
        "weather_code":                 [0, 2, 61],
        "precipitation_probability_max": [0, 10, 70],
    }
}


def _make_mock_response(mocker, json_data: dict, status_code: int = 200):
    """Helper: create a mock requests.Response."""
    mock_resp = mocker.MagicMock()
    mock_resp.status_code    = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status = mocker.MagicMock()
    return mock_resp


class TestFetchWeather:

    def test_returns_weather_dict_on_success(self, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, MOCK_CURRENT_RESPONSE)
        )
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        assert result is not None
        assert result["temperature"] == 38.0
        assert result["condition"]   == "Clear sky"
        assert result["emoji"]       == "☀"
        assert result["location"]    == "Delhi"

    def test_returns_none_on_connection_error(self, mocker):
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.ConnectionError()
        )
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        assert result is None

    def test_returns_none_on_timeout(self, mocker):
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.Timeout()
        )
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        assert result is None

    def test_returns_none_on_http_error(self, mocker):
        mock_resp = _make_mock_response(mocker, {}, status_code=429)
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mocker.patch("requests.get", return_value=mock_resp)
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        assert result is None

    def test_sends_user_agent_header(self, mocker):
        mock_get = mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, MOCK_CURRENT_RESPONSE)
        )
        fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        call_kwargs = mock_get.call_args[1]
        assert "headers" in call_kwargs
        assert "User-Agent" in call_kwargs["headers"]

    def test_uses_cache_when_fresh(self, mocker, tmp_path):
        # Patch the cache file location
        cache_data = {"fetched_at": 9_999_999_999, "weather": {"temperature": 25.0}}
        cache_file = tmp_path / "weather_cache.json"
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")

        mocker.patch(
            "taskflow.integrations.weather._CACHE_FILE",
            cache_file
        )
        mock_get = mocker.patch("requests.get")

        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=True)
        assert result["temperature"] == 25.0
        mock_get.assert_not_called()   # network was NOT hit

    def test_bypasses_cache_when_expired(self, mocker, tmp_path):
        # Cache timestamp in the past (epoch 0)
        cache_data = {"fetched_at": 0, "weather": {"temperature": 99.0}}
        cache_file = tmp_path / "weather_cache.json"
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")

        mocker.patch("taskflow.integrations.weather._CACHE_FILE", cache_file)
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, MOCK_CURRENT_RESPONSE)
        )

        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=True)
        assert result["temperature"] == 38.0   # fresh data, not cached 99.0


class TestFetchForecast:

    def test_returns_list_of_dicts(self, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, MOCK_FORECAST_RESPONSE)
        )
        result = fetch_forecast(28.6, 77.2, "Delhi", days=3)
        assert result is not None
        assert len(result) == 3
        assert result[0]["max_temp"] == 38.0
        assert result[0]["condition"] == "Clear sky"

    def test_returns_none_on_error(self, mocker):
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.ConnectionError()
        )
        result = fetch_forecast(28.6, 77.2, "Delhi")
        assert result is None


class TestDisplayWeather:

    def test_prints_weather_data(self, capsys):
        weather = {
            "location":    "Delhi",
            "temperature": 38,
            "feels_like":  41,
            "condition":   "Clear sky",
            "emoji":       "☀",
            "humidity":    22,
            "wind_speed":  14,
            "fetched_at":  "14:32",
        }
        display_weather(weather)
        captured = capsys.readouterr()
        assert "Delhi" in captured.out
        assert "38" in captured.out
        assert "Clear sky" in captured.out

    def test_prints_unavailable_when_none(self, capsys):
        display_weather(None)
        captured = capsys.readouterr()
        assert "not available" in captured.out.lower()


class TestGetWeatherSummary:

    def test_returns_summary_string(self):
        weather = {"temperature": 38, "emoji": "☀", "condition": "Clear sky"}
        summary = get_weather_summary(weather)
        assert "38" in summary
        assert "Clear sky" in summary

    def test_returns_unavailable_when_none(self):
        assert get_weather_summary(None) == "Weather unavailable"
```

---

### Building `tests/test_filters.py`

```python
# tests/test_filters.py
import pytest
from taskflow.filters import TaskFilter
from taskflow.core.task import Task
from taskflow.core.task_types import DeadlineTask, UrgentTask


class TestTaskFilterBasic:

    def test_get_returns_all_tasks(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).get()
        assert len(result) == len(mixed_tasks)

    def test_does_not_mutate_original(self, mixed_tasks):
        original_len = len(mixed_tasks)
        TaskFilter(mixed_tasks).pending().limit(1).get()
        assert len(mixed_tasks) == original_len

    def test_empty_filter_returns_empty(self, empty_tasks):
        result = TaskFilter(empty_tasks).get()
        assert result == []


class TestStatusFilters:

    def test_pending(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).pending().get()
        assert all(not t.done for t in result)

    def test_done(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).done().get()
        assert all(t.done for t in result)

    def test_pending_and_done_are_complementary(self, mixed_tasks):
        pending = TaskFilter(mixed_tasks).pending().count()
        done    = TaskFilter(mixed_tasks).done().count()
        assert pending + done == len(mixed_tasks)


class TestAttributeFilters:

    def test_by_priority_high(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).by_priority("high").get()
        assert all(t.priority == "high" for t in result)

    def test_by_category_work(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).by_category("work").get()
        assert all(t.category == "work" for t in result)

    def test_by_type_urgent(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).by_type(UrgentTask).get()
        assert all(isinstance(t, UrgentTask) for t in result)


class TestTextFilters:

    def test_search_case_insensitive(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).search("REVIEW").get()
        assert len(result) > 0
        assert all("review" in t.title.lower() for t in result)

    def test_search_no_match(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).search("xyzzy_no_match").get()
        assert result == []

    def test_search_regex(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).search_regex(r"^Review").get()
        assert all(t.title.startswith("Review") for t in result)

    def test_search_regex_invalid_raises(self, mixed_tasks):
        with pytest.raises(ValueError):
            TaskFilter(mixed_tasks).search_regex("[unclosed")


class TestSortingAndPaging:

    def test_sort_by_priority(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).sort_by("priority").get()
        scores = [t.priority_score for t in result]
        assert scores == sorted(scores, reverse=True)

    def test_sort_by_title(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).sort_by("title").get()
        titles = [t.title.lower() for t in result]
        assert titles == sorted(titles)

    def test_sort_unknown_key_raises(self, mixed_tasks):
        with pytest.raises(ValueError):
            TaskFilter(mixed_tasks).sort_by("nonexistent_key")

    def test_limit(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).limit(2).get()
        assert len(result) == 2

    def test_offset(self, mixed_tasks):
        all_tasks   = TaskFilter(mixed_tasks).get()
        after_offset = TaskFilter(mixed_tasks).offset(2).get()
        assert after_offset == all_tasks[2:]


class TestTerminalOperations:

    def test_count(self, mixed_tasks):
        assert TaskFilter(mixed_tasks).count() == len(mixed_tasks)

    def test_first(self, mixed_tasks):
        first = TaskFilter(mixed_tasks).first()
        assert first is mixed_tasks[0]

    def test_first_on_empty(self, empty_tasks):
        assert TaskFilter(empty_tasks).first() is None

    def test_titles(self, mixed_tasks):
        titles = TaskFilter(mixed_tasks).titles()
        assert len(titles) == len(mixed_tasks)
        assert all(isinstance(t, str) for t in titles)

    def test_ids(self, mixed_tasks):
        ids = TaskFilter(mixed_tasks).ids()
        assert all(isinstance(i, int) for i in ids)

    def test_id_map(self, mixed_tasks):
        id_map = TaskFilter(mixed_tasks).id_map()
        for task in mixed_tasks:
            assert task.id in id_map
            assert id_map[task.id] is task

    def test_bool_true_when_has_tasks(self, mixed_tasks):
        assert bool(TaskFilter(mixed_tasks)) is True

    def test_bool_false_when_empty(self, empty_tasks):
        assert bool(TaskFilter(empty_tasks)) is False

    def test_all_done_false_for_mixed(self, mixed_tasks):
        assert TaskFilter(mixed_tasks).all_done() is False

    def test_all_done_true_when_all_complete(self):
        tasks = [Task("A", "low", "work"), Task("B", "low", "work")]
        for t in tasks:
            t.mark_done()
        assert TaskFilter(tasks).all_done() is True


class TestChaining:

    def test_multiple_filters_chained(self, mixed_tasks):
        result = (
            TaskFilter(mixed_tasks)
            .pending()
            .by_priority("high")
            .sort_by("title")
            .limit(3)
            .get()
        )
        assert all(not t.done for t in result)
        assert all(t.priority == "high" for t in result)
        assert len(result) <= 3
```

---

### Building `tests/test_decorators.py`

```python
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
        assert result    == "ok"
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
        assert result      == "success"
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

        assert call_count == 1   # no retries for TypeError


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
```

---

### Mocking `datetime.now()` — Deterministic Time-Based Tests

```python
# In tests/test_task.py — add to TestTaskMethods

def test_is_overdue_uses_age_correctly(self, mocker):
    """Verify is_overdue() uses the current time from datetime.now()."""
    import datetime

    # Task created "10 days ago"
    fake_now = datetime.datetime(2025, 5, 19, 12, 0, 0)
    mocker.patch(
        "taskflow.core.task.datetime.datetime",
        wraps=datetime.datetime
    )
    # Set created_at to 10 days before fake_now
    task = Task("Old task", "high", "work")
    task.created_at = "2025-05-09 12:00"   # 10 days ago

    assert task.is_overdue(threshold_days=7)  is True
    assert task.is_overdue(threshold_days=14) is False
```

---

### Understanding Coverage Gaps

After running `--cov-report=term-missing`, some lines will be red. Not all gaps are equal:

**Acceptable gaps — mark with `# pragma: no cover`:**

```python
# Error handlers that can only trigger in truly exceptional OS conditions
except OSError as e:   # pragma: no cover
    logger.critical("Unexpected OS error: %s", e)
    raise

# __repr__ and __str__ are tested indirectly — rarely need direct coverage
def __repr__(self) -> str:  # pragma: no cover
    return f"Task(id={self.id!r}...)"

# Type guard branches for backward compatibility
if isinstance(task, Task):   # pragma: no cover
    ...
```

**Unacceptable gaps — must be covered:**
- Business logic branches (`if`, `elif`, `else`)
- Exception handlers for anticipated errors (`ValidationError`, `StorageError`)
- All public function bodies
- Serialisation and deserialisation paths

---

### Enforcing Coverage in CI

Add to `pyproject.toml`:

```toml
[tool.coverage.run]
source      = ["taskflow"]
omit        = ["tests/*", "run.py", "*/logging_config.py"]
branch      = true   # measure branch coverage, not just line coverage

[tool.coverage.report]
fail_under  = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
```

With `branch = true`, coverage checks both that a line was executed AND that each branch (`if`/`else`) was taken. Branch coverage is more meaningful than line coverage.

---

## Exercises

**Exercise 1 — Mock the backup function.**
Write a test that verifies `load_tasks_safe()` calls `backup_tasks()` when the storage file is corrupted, without actually creating a backup file:

```python
def test_load_tasks_safe_logs_corruption(mocker, tmp_path):
    corrupt_file = tmp_path / "tasks.json"
    corrupt_file.write_text("{not json}", encoding="utf-8")
    tasks, error = load_tasks_safe(filepath=corrupt_file)
    assert tasks == []
    assert error is not None
```

**Exercise 2 — `capsys` for renderer tests.**
Write tests for `display_tasks()` using `capsys`. Assert that:
- The task title appears in output
- The priority appears in uppercase
- `"No tasks"` appears when given an empty list
- The completion rate is shown in the footer

**Exercise 3 — `caplog` assertion.**
Write tests for `json_store.save_tasks()` that verify:
- `"Tasks saved"` log message appears on success
- `task_count` extra field is correct
- An `ERROR` log appears when an `OSError` is raised (use `mocker.patch` to inject the error)

**Exercise 4 — Parametrized integration test.**
Write a parametrized test that covers all weather code → condition mappings for codes 0, 1, 2, 3, 45, 61, 95:

```python
@pytest.mark.parametrize("code,expected_condition", [
    (0,  "Clear sky"),
    (1,  "Mainly clear"),
    (3,  "Overcast"),
    (61, "Light rain"),
    (95, "Thunderstorm"),
])
def test_weather_code_mapping(mocker, code, expected_condition):
    response_data = {"current": {
        "temperature_2m": 25.0, "apparent_temperature": 25.0,
        "relative_humidity_2m": 50, "wind_speed_10m": 10.0,
        "wind_direction_10m": 0, "weather_code": code,
    }}
    mocker.patch("requests.get",
                 return_value=_make_mock_response(mocker, response_data))
    result = fetch_weather(0, 0, "Test", use_cache=False)
    assert result["condition"] == expected_condition
```

**Exercise 5 — Test the `@retry` backoff timing.**
Use `mocker.patch("time.sleep")` to test that `@retry` sleeps the correct amount between retries without actually waiting:

```python
def test_retry_exponential_backoff(mocker):
    mock_sleep = mocker.patch("time.sleep")

    @retry(times=3, delay=1.0, backoff=2.0, exceptions=(ValueError,))
    def always_fail():
        raise ValueError("fail")

    with pytest.raises(ValueError):
        always_fail()

    # sleep called twice (between attempts 1-2 and 2-3)
    assert mock_sleep.call_count == 2
    assert mock_sleep.call_args_list[0] == call(1.0)  # delay
    assert mock_sleep.call_args_list[1] == call(2.0)  # delay * backoff
```

**Exercise 6 (stretch) — Full command test.**
Test `cmd_add()` end-to-end without hitting the network, file system, or real terminal input. Use `mocker` to patch `input()`, verify the task was appended to the list, and verify the confirmation was printed to stdout:

```python
def test_cmd_add_standard_task(mocker, empty_tasks, capsys):
    mocker.patch("builtins.input", return_value="Review PR #high @work")
    from taskflow.display.commands import cmd_add
    cmd_add(empty_tasks)
    assert len(empty_tasks) == 1
    assert empty_tasks[0].title    == "Review PR"
    assert empty_tasks[0].priority == "high"
    captured = capsys.readouterr()
    assert "added" in captured.out.lower()
```

---

## Checkpoint

Before moving to Day 27:

- [ ] `tests/test_weather.py` — all network calls mocked, all tests pass
- [ ] `tests/test_filters.py` — all filter paths covered
- [ ] `tests/test_decorators.py` — timer, retry, validate_non_empty tested
- [ ] Overall coverage ≥ 85% (`pytest --cov=taskflow`)
- [ ] Branch coverage enabled in `pyproject.toml`
- [ ] `pragma: no cover` used sparingly and only for genuinely untestable code
- [ ] No test makes a real network call — all HTTP mocked
- [ ] No test writes to the real `data/` directory — all use `tmp_path`

---

## Common Errors on Day 26

**Patching the wrong import path:**

```python
# ❌ Patches requests.get in the requests module — does not affect weather.py
@patch("requests.get")

# ✅ Patches the name as used in weather.py's namespace
@patch("taskflow.integrations.weather.requests.get")
```

Always patch where the name is **used**, not where it is **defined**. If `weather.py` does `import requests` and then calls `requests.get(...)`, patch `taskflow.integrations.weather.requests.get`.

**Mocks not being reset between tests:**

Using `@patch` as a class decorator applies the mock to every test in the class and resets it after each one automatically. Using `with patch(...)` resets after the `with` block. The `mocker` fixture resets after each test. All are safe — but do not mix approaches in confusing ways.

**Testing implementation details rather than behaviour:**

```python
# ❌ Tests that the internal _load_cache() was called — fragile
mocker.patch("taskflow.integrations.weather._load_cache")
fetch_weather(...)
assert mock_load_cache.called

# ✅ Tests the observable behaviour — cache is used (network not hit)
mock_get = mocker.patch("requests.get")
fetch_weather(..., use_cache=True)
mock_get.assert_not_called()
```

Test what the function does, not how it does it.

---

## What's Coming

On **Day 27** we add type hints throughout the codebase and run `mypy` in strict mode on the core modules. Type hints make bugs visible at edit time rather than runtime, improve IDE autocomplete, and serve as machine-checked documentation. We will also introduce `typing.Protocol` for structural typing — an elegant alternative to abstract base classes.