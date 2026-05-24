# Weather integration via Open-Meteo. Day 09/18.
from __future__ import annotations
import json, time, datetime, requests
from pathlib import Path
from ..config import WEATHER_API_URL, WEATHER_TIMEOUT, WEATHER_CACHE_TTL, DATE_FMT, BASE_DIR

__all__ = ["fetch_weather","display_weather","fetch_forecast","display_forecast","get_weather_summary"]

_CACHE_FILE = BASE_DIR / "data" / "weather_cache.json"

WMO_CODES: dict[int, str] = {
    0:"Clear sky", 1:"Mainly clear", 2:"Partly cloudy", 3:"Overcast",
    45:"Foggy", 48:"Icy fog", 51:"Light drizzle", 53:"Drizzle", 55:"Heavy drizzle",
    61:"Light rain", 63:"Rain", 65:"Heavy rain", 71:"Light snow", 73:"Snow",
    75:"Heavy snow", 80:"Rain showers", 81:"Rain showers", 82:"Violent showers",
    95:"Thunderstorm", 96:"Thunderstorm + hail",
}
WMO_EMOJI: dict[int, str] = {
    0:"☀", 1:"🌤", 2:"⛅", 3:"☁", 45:"🌫", 48:"🌫",
    51:"🌦", 53:"🌦", 55:"🌧", 61:"🌧", 63:"🌧", 65:"🌧",
    71:"🌨", 73:"❄", 75:"❄", 80:"🌦", 81:"🌧", 82:"⛈",
    95:"⛈", 96:"⛈",
}
HEADERS = {"User-Agent": "TaskFlowAI/1.1 (github.com/udit/taskflow)", "Accept": "application/json"}


def _load_cache() -> dict | None:
    if not _CACHE_FILE.exists():
        return None
    try:
        raw = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
        if time.time() - raw.get("fetched_at", 0) < WEATHER_CACHE_TTL:
            return raw.get("weather")
    except Exception:
        pass
    return None


def _save_cache(weather: dict) -> None:
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(
            json.dumps({"fetched_at": time.time(), "weather": weather}, indent=2),
            encoding="utf-8")
    except Exception:
        pass


def _do_fetch_weather(latitude: float, longitude: float, location_name: str) -> dict | None:
    params = {
        "latitude": latitude, "longitude": longitude,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
        "wind_speed_unit": "kmh", "timezone": "auto",
    }
    try:
        resp    = requests.get(WEATHER_API_URL, params=params, headers=HEADERS, timeout=WEATHER_TIMEOUT)
        resp.raise_for_status()
        data    = resp.json()
        current = data.get("current", {})
        code    = current.get("weather_code", 0)
        return {
            "location":    location_name,
            "temperature": current.get("temperature_2m"),
            "feels_like":  current.get("apparent_temperature"),
            "humidity":    current.get("relative_humidity_2m"),
            "wind_speed":  current.get("wind_speed_10m"),
            "condition":   WMO_CODES.get(code, "Unknown"),
            "emoji":       WMO_EMOJI.get(code, "🌡"),
            "fetched_at":  datetime.datetime.now().strftime("%H:%M"),
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


def fetch_weather(latitude: float, longitude: float,
                  location_name: str = "Your Location",
                  use_cache: bool = True) -> dict | None:
    if use_cache:
        cached = _load_cache()
        if cached:
            return cached
    weather = _do_fetch_weather(latitude, longitude, location_name)
    if weather:
        _save_cache(weather)
    return weather


def display_weather(weather: dict | None) -> None:
    if not weather:
        print("\n  Weather data not available.\n")
        return
    print()
    print("  ── Current Weather ──────────────────────")
    print(f"  Location    : {weather.get('location','Unknown')}")
    print(f"  Temperature : {weather.get('temperature')}°C (feels like {weather.get('feels_like')}°C)")
    print(f"  Condition   : {weather.get('emoji')}  {weather.get('condition')}")
    print(f"  Humidity    : {weather.get('humidity')}%")
    print(f"  Wind        : {weather.get('wind_speed')} km/h")
    print(f"  Updated     : {weather.get('fetched_at')}")
    print("  ─────────────────────────────────────────")
    print()


def get_weather_summary(weather: dict | None) -> str:
    if not weather:
        return "Weather unavailable"
    return f"{weather.get('temperature')}°C {weather.get('emoji','')} {weather.get('condition','')}"


def fetch_forecast(latitude: float, longitude: float,
                   location_name: str = "Your Location", days: int = 3) -> list[dict] | None:
    params = {
        "latitude": latitude, "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max",
        "forecast_days": days, "timezone": "auto",
    }
    try:
        resp  = requests.get(WEATHER_API_URL, params=params, headers=HEADERS, timeout=WEATHER_TIMEOUT)
        resp.raise_for_status()
        data  = resp.json()
        daily = data.get("daily", {})
        dates     = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        codes     = daily.get("weather_code", [])
        rain_prob = daily.get("precipitation_probability_max", [])
        forecast = []
        for i in range(len(dates)):
            code = codes[i] if i < len(codes) else 0
            forecast.append({
                "date": dates[i],
                "max_temp": max_temps[i] if i < len(max_temps) else None,
                "min_temp": min_temps[i] if i < len(min_temps) else None,
                "condition": WMO_CODES.get(code, "Unknown"),
                "emoji":     WMO_EMOJI.get(code, "🌡"),
                "rain_prob": rain_prob[i] if i < len(rain_prob) else None,
            })
        return forecast
    except Exception as e:
        print(f"  ✗ Could not fetch forecast: {e}")
        return None


def display_forecast(forecast: list[dict] | None, location_name: str = "") -> None:
    if not forecast:
        print("\n  Forecast not available.\n")
        return
    print(f"\n  ── {len(forecast)}-Day Forecast — {location_name} {'─'*20}")
    for i, day in enumerate(forecast):
        try:
            import datetime as dt
            d = dt.datetime.strptime(day["date"], "%Y-%m-%d")
            label = "Today     " if i == 0 else "Tomorrow  " if i == 1 else d.strftime("%a %d %b ")
        except ValueError:
            label = day.get("date", "")
        max_t = f"{day['max_temp']}°" if day.get("max_temp") is not None else "N/A"
        min_t = f"{day['min_temp']}°" if day.get("min_temp") is not None else "N/A"
        rain  = f"💧{day['rain_prob']}%" if day.get("rain_prob") is not None else ""
        print(f"  {label:<12} {max_t:>4}/{min_t:<5}  {day.get('emoji','')}  {day.get('condition',''):<22} {rain}")
    print("  " + "─"*52)
    print()
