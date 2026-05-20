import requests
from datetime import datetime

# ─── Configuration ────────────────────────────────────────
API_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10  # seconds

# Weather condition codes → human-readable descriptions
# Full list: https://open-meteo.com/en/docs#weathervariables
WMO_CODES = {
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

WMO_EMOJI = {
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


def fetch_weather(
    latitude: float, longitude: float, location_name: str = "Your Location"
) -> dict | None:
    """
    Fetch current weather from the Open-Meteo API.

    Args:
        latitude      (float): Location latitude.
        longitude     (float): Location longitude.
        location_name (str)  : Display name for the location.

    Returns:
        dict | None: Parsed weather data, or None if the request failed.
    """
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
        response = requests.get(API_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()  # raises HTTPError for 4xx/5xx responses
        data = response.json()
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
            "fetched_at": datetime.now().strftime("%H:%M"),
        }

    except requests.exceptions.ConnectionError:
        print("  ✗ No internet connection — weather unavailable.")
        return None
    except requests.exceptions.Timeout:
        print("  ✗ Weather request timed out.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"  ✗ Weather API error: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"  ✗ Could not parse weather response: {e}")
        return None


def display_weather(weather: dict) -> None:
    """
    Pretty-print weather data to the terminal.

    Args:
        weather (dict): Weather data from fetch_weather().
    """
    if weather is None:
        print("\n  Weather data not available.\n")
        return

    print()
    print("  ── Current Weather ──────────────────────")
    print(f"  Location    : {weather['location']}")
    print(
        f"  Temperature : {weather['temperature']}°C "
        f"(feels like {weather['feels_like']}°C)"
    )
    print(f"  Condition   : {weather['emoji']}  {weather['condition']}")
    print(f"  Humidity    : {weather['humidity']}%")
    print(f"  Wind        : {weather['wind_speed']} km/h")
    print(f"  Updated     : {weather['fetched_at']}")
    print("  ────────────────────────────────────────")
    print()


def get_weather_summary(weather: dict) -> str:
    """
    Return a one-line weather summary for the app header.

    Args:
        weather (dict): Weather data from fetch_weather().

    Returns:
        str: Compact weather string, e.g. "38°C ☀ Clear sky"
    """
    if weather is None:
        return "Weather unavailable"
    return f"{weather['temperature']}°C {weather['emoji']} {weather['condition']}"


# ─── Quick test ───────────────────────────────────────────
if __name__ == "__main__":
    print("Fetching weather for Delhi...")
    weather = fetch_weather(
        latitude=28.6139, longitude=77.2090, location_name="Delhi, IN"
    )
    display_weather(weather)


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
        days          (int)  : Number of forecast days (1-7).

    Returns:
        list[dict] | None: List of daily forecast dicts, or None on failure.
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
        response = requests.get(API_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        daily = data.get("daily", {})

        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        codes = daily.get("weather_code", [])
        rain_probs = daily.get("precipitation_probability_max", [])

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
                    "rain_prob": rain_probs[i] if i < len(rain_probs) else None,
                }
            )

        return forecast

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Forecast fetch failed: {e}")
        return None


def display_forecast(forecast: list[dict], location_name: str) -> None:
    """Display a formatted multi-day forecast table."""
    if not forecast:
        print("\n  Forecast not available.\n")
        return

    print(f"\n  ── {len(forecast)}-Day Forecast — {location_name} ─────────")

    for i, day in enumerate(forecast):
        # Parse and format the date
        try:
            dt = datetime.datetime.strptime(day["date"], "%Y-%m-%d")
            if i == 0:
                label = "Today     "
            elif i == 1:
                label = "Tomorrow  "
            else:
                label = dt.strftime("%a %d %b ")
        except ValueError:
            label = day["date"]

        max_t = f"{day['max_temp']}°" if day["max_temp"] is not None else "N/A"
        min_t = f"{day['min_temp']}°" if day["min_temp"] is not None else "N/A"
        rain = f"💧{day['rain_prob']}%" if day["rain_prob"] is not None else ""

        print(
            f"  {label:<12} {max_t:>4}/{min_t:<4}  "
            f"{day['emoji']}  {day['condition']:<20} {rain}"
        )

    print("  " + "─" * 52)
    print()


import time

def get_with_rate_limit_handling(url: str, params: dict,
                                  headers: dict, timeout: int = 10,
                                  max_retries: int = 3) -> dict | None:
    """
    Make a GET request, automatically retrying on 429 (Too Many Requests).
    """
    for attempt in range(1, max_retries + 1):
        response = requests.get(url, params=params,
                                headers=headers, timeout=timeout)

        if response.status_code == 429:
            # Server told us to slow down
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"  ⚠ Rate limited. Waiting {retry_after}s "
                  f"(attempt {attempt}/{max_retries})...")
            time.sleep(retry_after)
            continue

        response.raise_for_status()
        return response.json()

    print("  ✗ Max retries exceeded.")
    return None