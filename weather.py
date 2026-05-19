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
