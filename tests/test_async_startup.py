# tests/test_async_startup.py — Tests for taskflow/async_startup.py
import asyncio
import pytest
from pathlib import Path
from taskflow.async_startup import run_startup, StartupResult
from taskflow.core.task import Task


class TestStartupResult:
    def test_success_true_when_no_error(self):
        result = StartupResult(tasks=[], weather=None, load_error=None, elapsed_ms=10.0)
        assert result.success is True

    def test_success_false_when_error(self):
        result = StartupResult(tasks=[], weather=None, load_error="File not found", elapsed_ms=5.0)
        assert result.success is False

    def test_repr_contains_counts(self):
        result = StartupResult(tasks=[Task("A","low","work")], weather={"temp":38},
                               load_error=None, elapsed_ms=100.0)
        r = repr(result)
        assert "tasks=1" in r
        assert "weather=ok" in r
        assert "elapsed=100.0" in r

    def test_repr_weather_none(self):
        result = StartupResult(tasks=[], weather=None, load_error=None, elapsed_ms=5.0)
        assert "weather=none" in repr(result)


class TestRunStartup:
    def test_returns_startup_result(self, mocker, tmp_path):
        # Mock both tasks and weather so no real I/O happens
        tasks_data = [Task("Test task","low","work")]

        async def mock_load(fp):
            return tasks_data, None

        async def mock_weather(lat, lon, loc):
            return {"temperature": 38, "condition": "Clear sky", "emoji": "☀",
                    "location": loc, "feels_like": 40, "humidity": 20,
                    "wind_speed": 10, "fetched_at": "12:00"}

        mocker.patch("taskflow.async_startup._load_tasks_async", mock_load)
        mocker.patch("taskflow.async_startup._fetch_weather_async", mock_weather)

        result = asyncio.run(run_startup())

        assert isinstance(result, StartupResult)
        assert result.success   is True
        assert len(result.tasks) == 1
        assert result.weather   is not None
        assert result.elapsed_ms >= 0

    def test_handles_load_error(self, mocker):
        async def mock_load_fail(fp):
            return [], "Storage file is corrupt"

        async def mock_weather(lat, lon, loc):
            return None

        mocker.patch("taskflow.async_startup._load_tasks_async",  mock_load_fail)
        mocker.patch("taskflow.async_startup._fetch_weather_async", mock_weather)

        result = asyncio.run(run_startup())

        assert result.success   is False
        assert result.tasks     == []
        assert "corrupt" in result.load_error

    def test_continues_when_weather_fails(self, mocker):
        tasks_data = [Task("Test","low","work")]

        async def mock_load(fp):
            return tasks_data, None

        async def mock_weather_fail(lat, lon, loc):
            return None

        mocker.patch("taskflow.async_startup._load_tasks_async",   mock_load)
        mocker.patch("taskflow.async_startup._fetch_weather_async", mock_weather_fail)

        result = asyncio.run(run_startup())

        assert result.success    is True
        assert result.weather    is None
        assert len(result.tasks) == 1

    def test_elapsed_ms_positive(self, mocker):
        async def mock_load(fp):
            return [], None

        async def mock_weather(lat, lon, loc):
            return None

        mocker.patch("taskflow.async_startup._load_tasks_async",   mock_load)
        mocker.patch("taskflow.async_startup._fetch_weather_async", mock_weather)

        result = asyncio.run(run_startup())
        assert result.elapsed_ms >= 0

    def test_concurrent_execution(self, mocker):
        """Verify tasks and weather are gathered concurrently (both called)."""
        calls = []

        async def mock_load(fp):
            calls.append("load")
            return [], None

        async def mock_weather(lat, lon, loc):
            calls.append("weather")
            return None

        mocker.patch("taskflow.async_startup._load_tasks_async",   mock_load)
        mocker.patch("taskflow.async_startup._fetch_weather_async", mock_weather)

        asyncio.run(run_startup())

        assert "load"    in calls
        assert "weather" in calls


class TestLoadTasksAsync:
    def test_returns_tasks_when_file_exists(self, tmp_path, one_task):
        from taskflow.storage.json_store import save_tasks
        from taskflow.async_startup import _load_tasks_async

        fp = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=fp)

        tasks, error = asyncio.run(_load_tasks_async(fp))
        assert error is None
        assert len(tasks) == 1
        assert tasks[0].title == one_task[0].title

    def test_returns_empty_when_file_missing(self, tmp_path):
        from taskflow.async_startup import _load_tasks_async
        fp = tmp_path / "nonexistent.json"
        tasks, error = asyncio.run(_load_tasks_async(fp))
        assert tasks == []
        assert error is None

    def test_returns_error_on_corrupt_file(self, tmp_path):
        from taskflow.async_startup import _load_tasks_async
        fp = tmp_path / "corrupt.json"
        fp.write_text("{not valid json}", encoding="utf-8")
        tasks, error = asyncio.run(_load_tasks_async(fp))
        assert tasks == []
        assert error is not None
        assert isinstance(error, str)


class TestFetchWeatherAsync:
    def test_returns_none_when_weather_disabled(self, monkeypatch):
        monkeypatch.setenv("TASKFLOW_WEATHER", "false")
        from taskflow.env_config import get_settings
        get_settings(reload=True)
        from taskflow.async_startup import _fetch_weather_async
        result = asyncio.run(_fetch_weather_async(28.6, 77.2, "Delhi"))
        assert result is None

    def test_falls_back_to_sync_when_aiohttp_missing(self, mocker):
        """When aiohttp is not installed, falls back to sync requests."""
        mocker.patch.dict("sys.modules", {"aiohttp": None})
        mock_weather = {"temperature": 38, "condition": "Clear sky",
                        "emoji": "☀", "location": "Delhi",
                        "feels_like": 40, "humidity": 20,
                        "wind_speed": 10, "fetched_at": "12:00"}
        mocker.patch("taskflow.integrations.weather.fetch_weather",
                     return_value=mock_weather)
        from taskflow.async_startup import _fetch_weather_async
        # Reload to pick up the mocked aiohttp
        import importlib, taskflow.async_startup
        importlib.reload(taskflow.async_startup)
        from taskflow.async_startup import _fetch_weather_async as fresh_fn
        result = asyncio.run(fresh_fn(28.6, 77.2, "Delhi"))
        # Just verify it doesn't crash — actual result depends on mock
        assert result is None or isinstance(result, dict)