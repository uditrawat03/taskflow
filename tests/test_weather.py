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
        "temperature_2m": 38.0,
        "apparent_temperature": 41.0,
        "relative_humidity_2m": 22,
        "wind_speed_10m": 14.0,
        "wind_direction_10m": 315,
        "weather_code": 0,
    }
}

MOCK_FORECAST_RESPONSE = {
    "daily": {
        "time": ["2025-05-19", "2025-05-20", "2025-05-21"],
        "temperature_2m_max": [38.0, 36.0, 33.0],
        "temperature_2m_min": [28.0, 26.0, 24.0],
        "weather_code": [0, 2, 61],
        "precipitation_probability_max": [0, 10, 70],
    }
}


def _make_mock_response(mocker, json_data: dict, status_code: int = 200):
    """Helper: create a mock requests.Response."""
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status = mocker.MagicMock()
    return mock_resp


class TestFetchWeather:
    def test_returns_weather_dict_on_success(self, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, MOCK_CURRENT_RESPONSE),
        )
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        assert result is not None
        assert result["temperature"] == 38.0
        assert result["condition"] == "Clear sky"
        assert result["emoji"] == "☀"
        assert result["location"] == "Delhi"

    def test_returns_none_on_connection_error(self, mocker):
        mocker.patch("requests.get", side_effect=requests.exceptions.ConnectionError())
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        assert result is None

    def test_returns_none_on_timeout(self, mocker):
        mocker.patch("requests.get", side_effect=requests.exceptions.Timeout())
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
            return_value=_make_mock_response(mocker, MOCK_CURRENT_RESPONSE),
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

        mocker.patch("taskflow.integrations.weather._CACHE_FILE", cache_file)
        mock_get = mocker.patch("requests.get")

        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=True)
        assert result["temperature"] == 25.0
        mock_get.assert_not_called()  # network was NOT hit

    def test_bypasses_cache_when_expired(self, mocker, tmp_path):
        # Cache timestamp in the past (epoch 0)
        cache_data = {"fetched_at": 0, "weather": {"temperature": 99.0}}
        cache_file = tmp_path / "weather_cache.json"
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")

        mocker.patch("taskflow.integrations.weather._CACHE_FILE", cache_file)
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, MOCK_CURRENT_RESPONSE),
        )

        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=True)
        assert result["temperature"] == 38.0  # fresh data, not cached 99.0


class TestFetchForecast:
    def test_returns_list_of_dicts(self, mocker):
        mocker.patch(
            "requests.get",
            return_value=_make_mock_response(mocker, MOCK_FORECAST_RESPONSE),
        )
        result = fetch_forecast(28.6, 77.2, "Delhi", days=3)
        assert result is not None
        assert len(result) == 3
        assert result[0]["max_temp"] == 38.0
        assert result[0]["condition"] == "Clear sky"

    def test_returns_none_on_error(self, mocker):
        mocker.patch("requests.get", side_effect=requests.exceptions.ConnectionError())
        result = fetch_forecast(28.6, 77.2, "Delhi")
        assert result is None


class TestDisplayWeather:
    def test_prints_weather_data(self, capsys):
        weather = {
            "location": "Delhi",
            "temperature": 38,
            "feels_like": 41,
            "condition": "Clear sky",
            "emoji": "☀",
            "humidity": 22,
            "wind_speed": 14,
            "fetched_at": "14:32",
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
