# tests/test_weather.py — Tests for taskflow/integrations/weather.py
# All network calls are mocked — no real HTTP requests made.
import json
import time
import pytest
import requests
from pathlib import Path

from taskflow.integrations.weather import (
    fetch_weather, fetch_forecast,
    display_weather, display_forecast,
    get_weather_summary,
)

# ── Shared mock data ──────────────────────────────────────

MOCK_CURRENT = {
    "current": {
        "temperature_2m":       38.0,
        "apparent_temperature": 41.0,
        "relative_humidity_2m": 22,
        "wind_speed_10m":       14.0,
        "wind_direction_10m":   315,
        "weather_code":         0,
    }
}

MOCK_FORECAST = {
    "daily": {
        "time":                          ["2025-05-19","2025-05-20","2025-05-21"],
        "temperature_2m_max":            [38.0, 36.0, 33.0],
        "temperature_2m_min":            [28.0, 26.0, 24.0],
        "weather_code":                  [0, 2, 61],
        "precipitation_probability_max": [0, 10, 70],
    }
}


def _mock_response(mocker, json_data: dict, status_code: int = 200):
    mock_resp = mocker.MagicMock()
    mock_resp.status_code    = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status = mocker.MagicMock()
    return mock_resp


class TestFetchWeather:
    def test_returns_weather_dict(self, mocker):
        mocker.patch("requests.get",
                     return_value=_mock_response(mocker, MOCK_CURRENT))
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        assert result is not None
        assert result["temperature"] == 38.0
        assert result["condition"]   == "Clear sky"
        assert result["emoji"]       == "☀"
        assert result["location"]    == "Delhi"

    def test_returns_none_on_connection_error(self, mocker):
        mocker.patch("requests.get",
                     side_effect=requests.exceptions.ConnectionError())
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        assert result is None

    def test_returns_none_on_timeout(self, mocker):
        mocker.patch("requests.get",
                     side_effect=requests.exceptions.Timeout())
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        assert result is None

    def test_returns_none_on_http_error(self, mocker):
        mock_resp = _mock_response(mocker, {}, status_code=500)
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mocker.patch("requests.get", return_value=mock_resp)
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        assert result is None

    def test_sends_user_agent_header(self, mocker):
        mock_get = mocker.patch("requests.get",
                                return_value=_mock_response(mocker, MOCK_CURRENT))
        fetch_weather(28.6, 77.2, "Delhi", use_cache=False)
        call_kwargs = mock_get.call_args[1]
        assert "headers" in call_kwargs
        assert "User-Agent" in call_kwargs["headers"]

    def test_uses_fresh_cache(self, mocker, tmp_path):
        """When cache is fresh, requests.get should NOT be called."""
        cache_data = {"fetched_at": time.time() + 9999,
                      "weather": {"temperature": 25.0, "location": "cached"}}
        cache_file = tmp_path / "weather_cache.json"
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")
        mocker.patch("taskflow.integrations.weather._CACHE_FILE", cache_file)
        mock_get = mocker.patch("requests.get")
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=True)
        assert result["temperature"] == 25.0
        mock_get.assert_not_called()

    def test_bypasses_expired_cache(self, mocker, tmp_path):
        """When cache is stale, fresh data should be fetched."""
        cache_data = {"fetched_at": 0,
                      "weather": {"temperature": 99.0}}
        cache_file = tmp_path / "weather_cache.json"
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")
        mocker.patch("taskflow.integrations.weather._CACHE_FILE", cache_file)
        mocker.patch("requests.get",
                     return_value=_mock_response(mocker, MOCK_CURRENT))
        result = fetch_weather(28.6, 77.2, "Delhi", use_cache=True)
        assert result["temperature"] == 38.0

    @pytest.mark.parametrize("code,expected_condition", [
        (0,  "Clear sky"),
        (1,  "Mainly clear"),
        (3,  "Overcast"),
        (45, "Foggy"),
        (61, "Light rain"),
        (95, "Thunderstorm"),
    ])
    def test_weather_code_mapping(self, mocker, code, expected_condition):
        mock_data = {"current": {
            "temperature_2m": 25.0, "apparent_temperature": 25.0,
            "relative_humidity_2m": 50, "wind_speed_10m": 10.0,
            "wind_direction_10m": 0, "weather_code": code,
        }}
        mocker.patch("requests.get",
                     return_value=_mock_response(mocker, mock_data))
        result = fetch_weather(0, 0, "Test", use_cache=False)
        assert result is not None
        assert result["condition"] == expected_condition


class TestFetchForecast:
    def test_returns_list_of_dicts(self, mocker):
        mocker.patch("requests.get",
                     return_value=_mock_response(mocker, MOCK_FORECAST))
        result = fetch_forecast(28.6, 77.2, "Delhi", days=3)
        assert result is not None
        assert len(result) == 3
        assert result[0]["max_temp"]  == 38.0
        assert result[0]["condition"] == "Clear sky"
        assert result[2]["condition"] == "Light rain"

    def test_returns_none_on_error(self, mocker):
        mocker.patch("requests.get",
                     side_effect=requests.exceptions.ConnectionError())
        result = fetch_forecast(28.6, 77.2, "Delhi")
        assert result is None

    def test_rain_prob_in_result(self, mocker):
        mocker.patch("requests.get",
                     return_value=_mock_response(mocker, MOCK_FORECAST))
        result = fetch_forecast(28.6, 77.2, "Delhi")
        assert result[2]["rain_prob"] == 70


class TestDisplayWeather:
    def test_prints_weather_data(self, capsys):
        weather = {
            "location": "Delhi", "temperature": 38, "feels_like": 41,
            "condition": "Clear sky", "emoji": "☀",
            "humidity": 22, "wind_speed": 14, "fetched_at": "14:32",
        }
        display_weather(weather)
        out = capsys.readouterr().out
        assert "Delhi" in out
        assert "38" in out
        assert "Clear sky" in out

    def test_prints_unavailable_when_none(self, capsys):
        display_weather(None)
        out = capsys.readouterr().out
        assert "not available" in out.lower()


class TestDisplayForecast:
    def test_prints_location(self, capsys):
        forecast = [
            {"date": "2025-05-19", "max_temp": 38.0, "min_temp": 28.0,
             "condition": "Clear sky", "emoji": "☀", "rain_prob": 0},
        ]
        display_forecast(forecast, "Delhi")
        out = capsys.readouterr().out
        assert "Delhi" in out

    def test_prints_unavailable_when_none(self, capsys):
        display_forecast(None, "Delhi")
        out = capsys.readouterr().out
        assert "not available" in out.lower()


class TestGetWeatherSummary:
    def test_returns_summary_string(self):
        weather = {"temperature": 38, "emoji": "☀", "condition": "Clear sky"}
        summary = get_weather_summary(weather)
        assert "38" in summary
        assert "Clear sky" in summary
        assert "☀" in summary

    def test_returns_unavailable_when_none(self):
        assert get_weather_summary(None) == "Weather unavailable"

    def test_format(self):
        weather = {"temperature": 25, "emoji": "⛅", "condition": "Partly cloudy"}
        summary = get_weather_summary(weather)
        assert isinstance(summary, str)
        assert len(summary) > 0