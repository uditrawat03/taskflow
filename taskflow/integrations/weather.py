import json
import time
import datetime
import requests
from pathlib import Path

from ..config import (
    WEATHER_API_URL,
    WEATHER_TIMEOUT,
    WEATHER_CACHE_TTL,
    DATA_DIR,
    DATE_FMT,
)

import logging
logger = logging.getLogger(__name__)

# Caching config
_CACHE_FILE = DATA_DIR / "weather_cache.json"

# WMO weather code mappings
WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Icy fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Rain showers",
    82: "Violent showers",
    95: "Thunderstorm",
    96: "Thunderstorm + hail",
}

WMO_EMOJI: dict[int, str] = {
    0: "☀",
    1: "🌤",
    2: "⛅",
    3: "☁",
    45: "🌫",
    48: "🌫",
    51: "🌦",
    53: "🌦",
    55: "🌧",
    61: "🌧",
    63: "🌧",
    65: "🌧",
    71: "🌨",
    73: "❄",
    75: "❄",
    80: "🌦",
    81: "🌧",
    82: "⛈",
    95: "⛈",
    96: "⛈",
}

HEADERS = {
    "User-Agent": "TaskFlowAI/1.1 (github.com/udit/taskflow)",
    "Accept": "application/json",
}


# Cache helpers
def _load_cache() -> dict | None:
    """Return cached weather dict if still within TTL, else None."""
    if not _CACHE_FILE.exists():
        return None
    try:
        raw = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
        age = time.time() - raw.get("fetched_at", 0)
        if age < WEATHER_CACHE_TTL:
            return raw.get("weather")
    except Exception:
        pass
    return None


def _save_cache(weather: dict) -> None:
    """Persist weather data to the cache file."""
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(
            json.dumps({"fetched_at": time.time(), "weather": weather}, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass  # cache failure is never critical


# Current weather
def _do_fetch_weather(
    latitude: float, longitude: float, location_name: str
) -> dict | None:
    """Make the actual API request for current weather."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(
            [
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "wind_speed_10m",
                "wind_direction_10m",
                "weather_code",
            ]
        ),
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }
    try:
        resp = requests.get(
            WEATHER_API_URL,
            params=params,
            headers=HEADERS,
            timeout=WEATHER_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current", {})
        code = current.get("weather_code", 0)
        return {
            "location": location_name,
            "temperature": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "condition": WMO_CODES.get(code, "Unknown"),
            "emoji": WMO_EMOJI.get(code, "🌡"),
            "fetched_at": datetime.datetime.now().strftime("%H:%M"),
        }
    except requests.exceptions.ConnectionError:
        print("  ✗ No internet connection — weather unavailable.")
    except requests.exceptions.Timeout:
        print("  ✗ Weather request timed out.")
    except requests.exceptions.HTTPError as e:
        print(f"  ✗ Weather API error: {e}")
    except Exception as e:
        print(f"  ✗ Could not parse weather response: {e}")
    return None


def fetch_weather(latitude, longitude, location_name="", use_cache=True):
    if use_cache:
        cached = _load_cache()
        if cached:
            logger.debug("Weather cache hit — returning cached data")
            return cached

    logger.info("Fetching weather", extra={"location": location_name})
    weather = _do_fetch_weather(latitude, longitude, location_name)
    if weather:
        _save_cache(weather)
        logger.debug("Weather cached successfully")
    else:
        logger.warning("Weather fetch returned None")
    return weather

def display_weather(weather: dict | None) -> None:
    """Pretty-print current weather to the terminal."""
    if not weather:
        print("\n  Weather data not available.\n")
        return

    print()
    print("   Current Weather ")
    print(f"  Location    : {weather.get('location', 'Unknown')}")
    print(
        f"  Temperature : {weather.get('temperature')}°C "
        f"(feels like {weather.get('feels_like')}°C)"
    )
    print(f"  Condition   : {weather.get('emoji')}  {weather.get('condition')}")
    print(f"  Humidity    : {weather.get('humidity')}%")
    print(f"  Wind        : {weather.get('wind_speed')} km/h")
    print(f"  Updated     : {weather.get('fetched_at')}")
    print("  ─")
    print()


def get_weather_summary(weather: dict | None) -> str:
    """Return a compact one-line weather string for the app header."""
    if not weather:
        return "Weather unavailable"
    return (
        f"{weather.get('temperature')}°C "
        f"{weather.get('emoji', '')} "
        f"{weather.get('condition', '')}"
    )


# ─ Forecast ─


def fetch_forecast(
    latitude: float,
    longitude: float,
    location_name: str = "Your Location",
    days: int = 3,
) -> list[dict] | None:
    """
    Fetch a multi-day weather forecast.

    Args:
        latitude      (float): Location latitude.
        longitude     (float): Location longitude.
        location_name (str)  : Display name.
        days          (int)  : Number of forecast days (1–7).

    Returns:
        list[dict] | None: Daily forecast dicts, or None on failure.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "weather_code",
                "precipitation_probability_max",
            ]
        ),
        "forecast_days": days,
        "timezone": "auto",
    }
    try:
        resp = requests.get(
            WEATHER_API_URL,
            params=params,
            headers=HEADERS,
            timeout=WEATHER_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        daily = data.get("daily", {})

        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        codes = daily.get("weather_code", [])
        rain_prob = daily.get("precipitation_probability_max", [])

        forecast = []
        for i in range(len(dates)):
            code = codes[i] if i < len(codes) else 0
            forecast.append(
                {
                    "date": dates[i],
                    "max_temp": max_temps[i] if i < len(max_temps) else None,
                    "min_temp": min_temps[i] if i < len(min_temps) else None,
                    "condition": WMO_CODES.get(code, "Unknown"),
                    "emoji": WMO_EMOJI.get(code, "🌡"),
                    "rain_prob": rain_prob[i] if i < len(rain_prob) else None,
                }
            )
        return forecast

    except requests.exceptions.ConnectionError:
        print("  ✗ No internet connection — forecast unavailable.")
    except requests.exceptions.Timeout:
        print("  ✗ Forecast request timed out.")
    except Exception as e:
        print(f"  ✗ Could not fetch forecast: {e}")
    return None


def display_forecast(forecast: list[dict] | None, location_name: str = "") -> None:
    """Display a formatted multi-day forecast table."""
    if not forecast:
        print("\n  Forecast not available.\n")
        return

    header = f"   {len(forecast)}-Day Forecast"
    if location_name:
        header += f" — {location_name}"
    print()
    print(header + " " + "─" * max(0, 50 - len(header)))

    for i, day in enumerate(forecast):
        try:
            dt = datetime.datetime.strptime(day["date"], "%Y-%m-%d")
            if i == 0:
                label = "Today     "
            elif i == 1:
                label = "Tomorrow  "
            else:
                label = dt.strftime("%a %d %b ")
        except ValueError:
            label = day.get("date", "")

        max_t = f"{day['max_temp']}°" if day.get("max_temp") is not None else "N/A"
        min_t = f"{day['min_temp']}°" if day.get("min_temp") is not None else "N/A"
        rain = f"💧{day['rain_prob']}%" if day.get("rain_prob") is not None else ""

        print(
            f"  {label:<12} {max_t:>4}/{min_t:<5}  "
            f"{day.get('emoji', '')}  "
            f"{day.get('condition', ''):<22} {rain}"
        )

    print("  " + "─" * 52)
    print()
