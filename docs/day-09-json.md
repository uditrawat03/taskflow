# Day 09 — JSON: The Language of APIs

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Upgrading storage to JSON, consuming a real API

---

## Learning Objective

By the end of today, you will understand JSON deeply — how it maps to Python data structures, how to read and write it to files, and how to consume it from a real web API. TaskFlow AI's storage format upgrades from pipe-separated text to JSON, and the app fetches live weather data to display alongside tasks — your first real API integration.

---

## What We Build Today

Two things: a JSON-powered `storage.py` upgrade, and a `weather.py` module that fetches live weather from a public API and displays it in the TaskFlow dashboard.

```
$ python tasks.py

  Loading tasks... ✓ 4 tasks loaded from taskflow_tasks.json

========================================
   TaskFlow AI — Task Manager v0.6
   📍 Delhi, IN  |  🌡 38°C  |  ☀ Clear
========================================
   Hello, Udit! Plan: Free (10 tasks max)

Commands: add | view | done | remove | filter | search | stats | weather | quit

> weather

  ── Current Weather ─────────────────────
  Location    : Delhi, India
  Temperature : 38°C (feels like 41°C)
  Condition   : Clear sky
  Humidity    : 22%
  Wind        : 14 km/h NW
  ────────────────────────────────────────
```

---

## Concepts Covered

- What JSON is and why it matters
- JSON data types and how they map to Python
- `json.dumps()` — Python → JSON string
- `json.loads()` — JSON string → Python
- `json.dump()` — Python → JSON file
- `json.load()` — JSON file → Python
- Pretty-printing JSON
- The `requests` library — making HTTP GET requests
- Reading API responses as JSON
- API keys and query parameters
- Error handling for network requests
- Upgrading storage from `.txt` to `.json`

---

## Full Tutorial

### What Is JSON?

JSON (JavaScript Object Notation) is a text format for representing structured data. It was designed to be human-readable and machine-parseable. Today it is the universal language of web APIs — every major API returns JSON, every modern app sends JSON.

Here is what a TaskFlow task looks like in JSON:

```json
{
  "id": 1,
  "title": "Review pull request",
  "priority": "high",
  "category": "work",
  "status": "pending",
  "done": false,
  "created_at": "2025-05-19 14:32"
}
```

And a list of tasks:

```json
[
  {
    "id": 1,
    "title": "Review pull request",
    "priority": "high",
    "category": "work",
    "status": "pending",
    "done": false,
    "created_at": "2025-05-19 14:32"
  },
  {
    "id": 2,
    "title": "Buy groceries",
    "priority": "low",
    "category": "personal",
    "status": "pending",
    "done": false,
    "created_at": "2025-05-19 14:33"
  }
]
```

Notice how this maps directly to Python dictionaries and lists. JSON is essentially Python's `dict` and `list` notation with minor differences.

---

### JSON vs Python — The Differences

| JSON | Python | Notes |
|------|--------|-------|
| `{}` | `dict` | Identical structure |
| `[]` | `list` | Identical structure |
| `"string"` | `str` | JSON always uses double quotes |
| `123` | `int` | Same |
| `3.14` | `float` | Same |
| `true` | `True` | Lowercase in JSON |
| `false` | `False` | Lowercase in JSON |
| `null` | `None` | Different keyword |

Python's `json` module handles all these conversions automatically.

---

### `json.dumps()` and `json.loads()` — Working with Strings

```python
import json

# Python dict → JSON string
task = {
    "id": 1,
    "title": "Review PR",
    "priority": "high",
    "done": False,
    "created_at": None
}

json_string = json.dumps(task)
print(json_string)
# {"id": 1, "title": "Review PR", "priority": "high", "done": false, "created_at": null}

# Pretty-print with indentation
pretty = json.dumps(task, indent=2)
print(pretty)
# {
#   "id": 1,
#   "title": "Review PR",
#   "priority": "high",
#   "done": false,
#   "created_at": null
# }

# JSON string → Python dict
json_str = '{"id": 1, "title": "Review PR", "done": false}'
task = json.loads(json_str)
print(task)          # {"id": 1, "title": "Review PR", "done": False}
print(task["title"]) # "Review PR"
print(type(task))    # <class 'dict'>
```

`json.dumps()` — **d**ump to **s**tring (Python → JSON text)
`json.loads()` — **lo**ad from **s**tring (JSON text → Python)

---

### `json.dump()` and `json.load()` — Working with Files

```python
import json
from pathlib import Path

tasks = [
    {"id": 1, "title": "Review PR",      "priority": "high", "done": False},
    {"id": 2, "title": "Buy groceries",  "priority": "low",  "done": False},
    {"id": 3, "title": "Write tests",    "priority": "high", "done": True},
]

# Write list to JSON file
filepath = Path("taskflow_tasks.json")
with open(filepath, "w", encoding="utf-8") as f:
    json.dump(tasks, f, indent=2, ensure_ascii=False)

# Read list back from JSON file
with open(filepath, "r", encoding="utf-8") as f:
    loaded_tasks = json.load(f)

print(loaded_tasks[0]["title"])   # "Review PR"
print(type(loaded_tasks))         # <class 'list'>
print(type(loaded_tasks[0]))      # <class 'dict'>
```

`json.dump()` — dump to file (Python → JSON file)
`json.load()` — load from file (JSON file → Python)

**`ensure_ascii=False`** — allows non-ASCII characters (Hindi, emoji, accented letters) to be stored as-is instead of being escaped. Always include this for international support.

**`indent=2`** — pretty-prints the JSON with 2-space indentation. Makes the file human-readable in VS Code. Omit for production where file size matters.

---

### Why JSON Beats the Pipe-Separated Format

Compare the Day 08 format to JSON:

```
# Day 08 — pipe separated (fragile)
1|Review PR|high|work|pending|False|2025-05-19 14:32

# Day 09 — JSON (robust)
{"id": 1, "title": "Review PR", "priority": "high", "category": "work",
 "status": "pending", "done": false, "created_at": "2025-05-19 14:32"}
```

With JSON:
- No custom `task_to_line()` or `line_to_task()` functions needed
- Booleans stored as `false`/`true` — no `"True" == "True"` string comparison bugs
- `None` stored as `null` — no ambiguity
- Adding a new field requires zero changes to the storage code
- Any JSON viewer (VS Code, browser devtools, online tools) can read the file
- Same format used by every web API you will ever consume

---

### Upgrading `storage.py` to JSON

Replace `storage.py` entirely:

```python
# storage.py
# TaskFlow AI — Day 09
# JSON-based task persistence.
# Replaces the pipe-separated text format from Day 08.

import json
import datetime
import shutil
from pathlib import Path

# ─── Configuration ────────────────────────────────────────
BASE_DIR  = Path(__file__).parent
DATA_FILE = BASE_DIR / "taskflow_tasks.json"
DATE_FMT  = "%Y-%m-%d %H:%M"


def save_tasks(tasks: list, filepath: Path = DATA_FILE) -> bool:
    """
    Save all tasks to a JSON file.

    Uses an atomic write pattern — writes to a temp file first,
    then renames, so the data file is never left half-written.

    Args:
        tasks    (list): List of task dictionaries.
        filepath (Path): Destination JSON file path.

    Returns:
        bool: True if save succeeded, False otherwise.
    """
    tmp_path = filepath.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        tmp_path.rename(filepath)   # atomic replace
        return True
    except (OSError, TypeError) as e:
        print(f"  ✗ Save failed: {e}")
        if tmp_path.exists():
            tmp_path.unlink()       # clean up temp file on failure
        return False


def load_tasks(filepath: Path = DATA_FILE) -> list:
    """
    Load tasks from a JSON file.

    Returns an empty list if the file does not exist or is corrupted.

    Args:
        filepath (Path): Source JSON file path.

    Returns:
        list: List of task dictionaries, or [] on failure.
    """
    if not filepath.exists():
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print("  ✗ Storage file is corrupted — expected a list.")
            return []
        return data
    except json.JSONDecodeError as e:
        print(f"  ✗ Storage file is invalid JSON: {e}")
        return []
    except OSError as e:
        print(f"  ✗ Could not read storage file: {e}")
        return []


def get_next_id(tasks: list) -> int:
    """Return the next available task ID."""
    return max((t["id"] for t in tasks), default=0) + 1


def backup_tasks(filepath: Path = DATA_FILE) -> bool:
    """
    Create a timestamped backup of the JSON storage file.

    Args:
        filepath (Path): Path to the storage file to back up.

    Returns:
        bool: True if backup succeeded.
    """
    if not filepath.exists():
        print("  ✗ No storage file to back up.")
        return False

    timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.parent / f"taskflow_backup_{timestamp}.json"

    try:
        shutil.copy2(filepath, backup_path)
        print(f"  ✓ Backup saved: {backup_path.name}")
        return True
    except OSError as e:
        print(f"  ✗ Backup failed: {e}")
        return False


def get_storage_info(filepath: Path = DATA_FILE) -> dict:
    """Return metadata about the storage file."""
    if not filepath.exists():
        return {"exists": False}

    stat = filepath.stat()
    return {
        "exists":        True,
        "filepath":      str(filepath),
        "size_bytes":    stat.st_size,
        "last_modified": datetime.datetime.fromtimestamp(
                             stat.st_mtime).strftime(DATE_FMT),
    }
```

Notice what disappeared: `task_to_line()`, `line_to_task()`, the pipe separator, the boolean string conversion. JSON handles all of it. The module is half the size and twice as robust.

---

### Installing `requests`

Now we add real internet connectivity. The `requests` library is the standard Python tool for making HTTP requests:

```bash
pip install requests
```

Verify:

```python
import requests
print(requests.__version__)
```

---

### Making Your First API Call

We will use the **Open-Meteo** API — it is completely free, requires no API key, and returns weather data as JSON:

```python
import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude":  28.6139,    # Delhi
    "longitude": 77.2090,
    "current":   "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
    "wind_speed_unit": "kmh",
}

response = requests.get(url, params=params, timeout=10)

print(response.status_code)   # 200 = success
print(type(response.json()))  # <class 'dict'>
print(response.json())        # full JSON response
```

**Anatomy of an API call:**

- `url` — the endpoint (address of the API resource)
- `params` — query parameters appended to the URL: `?latitude=28.6&longitude=77.2&...`
- `timeout=10` — wait maximum 10 seconds before giving up
- `response.status_code` — `200` means success, `404` means not found, `500` means server error
- `response.json()` — parses the response body as JSON and returns a Python dict

---

### Building `weather.py`

```python
# weather.py
# TaskFlow AI — Day 09
# Fetches and displays current weather using the Open-Meteo API.
# No API key required.

import requests
from datetime import datetime

# ─── Configuration ────────────────────────────────────────
API_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10   # seconds

# Weather condition codes → human-readable descriptions
# Full list: https://open-meteo.com/en/docs#weathervariables
WMO_CODES = {
    0:  "Clear sky",
    1:  "Mainly clear",  2: "Partly cloudy",  3: "Overcast",
    45: "Foggy",         48: "Icy fog",
    51: "Light drizzle", 53: "Drizzle",        55: "Heavy drizzle",
    61: "Light rain",    63: "Rain",            65: "Heavy rain",
    71: "Light snow",    73: "Snow",            75: "Heavy snow",
    80: "Rain showers",  81: "Rain showers",    82: "Violent showers",
    95: "Thunderstorm",  96: "Thunderstorm + hail",
}

WMO_EMOJI = {
    0: "☀",  1: "🌤",  2: "⛅",  3: "☁",
    45: "🌫", 48: "🌫",
    51: "🌦", 53: "🌦", 55: "🌧",
    61: "🌧", 63: "🌧", 65: "🌧",
    71: "🌨", 73: "❄",  75: "❄",
    80: "🌦", 81: "🌧", 82: "⛈",
    95: "⛈", 96: "⛈",
}


def fetch_weather(latitude: float, longitude: float,
                  location_name: str = "Your Location") -> dict | None:
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
        "latitude":        latitude,
        "longitude":       longitude,
        "current":         ",".join([
                               "temperature_2m",
                               "apparent_temperature",
                               "relative_humidity_2m",
                               "wind_speed_10m",
                               "wind_direction_10m",
                               "weather_code",
                           ]),
        "wind_speed_unit": "kmh",
        "timezone":        "auto",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()   # raises HTTPError for 4xx/5xx responses
        data     = response.json()
        current  = data.get("current", {})

        code = current.get("weather_code", 0)

        return {
            "location":    location_name,
            "temperature": current.get("temperature_2m"),
            "feels_like":  current.get("apparent_temperature"),
            "humidity":    current.get("relative_humidity_2m"),
            "wind_speed":  current.get("wind_speed_10m"),
            "condition":   WMO_CODES.get(code, "Unknown"),
            "emoji":       WMO_EMOJI.get(code, "🌡"),
            "fetched_at":  datetime.now().strftime("%H:%M"),
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
    print(f"  Temperature : {weather['temperature']}°C "
          f"(feels like {weather['feels_like']}°C)")
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
    return (f"{weather['temperature']}°C "
            f"{weather['emoji']} "
            f"{weather['condition']}")


# ─── Quick test ───────────────────────────────────────────
if __name__ == "__main__":
    print("Fetching weather for Delhi...")
    weather = fetch_weather(
        latitude=28.6139,
        longitude=77.2090,
        location_name="Delhi, IN"
    )
    display_weather(weather)
```

Test it standalone:

```bash
python weather.py
```

---

### Integrating Weather into `tasks.py`

Add to the top of `tasks.py`:

```python
from weather import fetch_weather, display_weather, get_weather_summary

# User location — in Phase 3 this will come from user settings
USER_LATITUDE  = 28.6139
USER_LONGITUDE = 77.2090
USER_LOCATION  = "Delhi, IN"
```

Update `display_header()`:

```python
def display_header(weather: dict | None = None) -> None:
    """Print the application header with optional weather summary."""
    print("=" * 44)
    print(f"   {APP_NAME} — Task Manager v{VERSION}")
    if weather:
        summary = get_weather_summary(weather)
        print(f"   📍 {USER_LOCATION}  |  🌡 {summary}")
    print("=" * 44)
    print(f"   Hello, {USER_NAME}! Plan: {USER_PLAN.title()} ({MAX_TASKS} tasks max)")
    print()
```

Update `main()` to fetch weather at startup and add `"weather"` command:

```python
def main() -> None:
    tasks   = load_tasks()
    next_id = [get_next_id(tasks)]

    # Fetch weather at startup (non-blocking feel — shown after header)
    print("\n  Loading tasks...", end=" ")
    print(f"✓ {len(tasks)} task{'s' if len(tasks) != 1 else ''} loaded.\n")

    weather = fetch_weather(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)

    display_header(weather)
    display_help()

    while True:
        command = input("> ").strip().lower()

        if   command == "add":     cmd_add(tasks, next_id)
        elif command == "view":    display_tasks(tasks)
        elif command == "done":    cmd_done(tasks)
        elif command == "remove":  cmd_remove(tasks)
        elif command == "filter":  cmd_filter(tasks)
        elif command == "search":  cmd_search(tasks)
        elif command == "stats":   display_stats(tasks)
        elif command == "weather":
            # Re-fetch live weather on demand
            weather = fetch_weather(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
            display_weather(weather)
        elif command == "backup":  backup_tasks()
        elif command == "help":    display_help()
        elif command == "quit":
            save_tasks(tasks)
            cmd_quit(tasks)
            break
        elif command == "":
            continue
        else:
            print(f"\n  ✗ Unknown command '{command}'. Type 'help' for options.\n")
```

---

### Understanding `response.raise_for_status()`

```python
response = requests.get(url, params=params, timeout=10)
response.raise_for_status()
```

`raise_for_status()` raises an `HTTPError` exception if the status code indicates failure (4xx or 5xx). Without it, a `404 Not Found` or `500 Server Error` response would appear to succeed — `response.status_code` would be non-200, but no exception would be raised and you would try to parse an error response as if it were real data.

Always call `raise_for_status()` immediately after `requests.get()`. Always.

---

### Reading a Real API Response

Open the Open-Meteo URL in your browser to see the raw JSON:

```
https://api.open-meteo.com/v1/forecast?latitude=28.6139&longitude=77.2090&current=temperature_2m,weather_code&wind_speed_unit=kmh&timezone=auto
```

Practice navigating the response:

```python
import requests, json

response = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": 28.6139, "longitude": 77.2090,
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    },
    timeout=10
)

data = response.json()

# Pretty print the full response to understand its structure
print(json.dumps(data, indent=2))

# Navigate the structure
print(data.keys())                          # dict_keys(['latitude', 'longitude', 'current', ...])
print(data["current"].keys())               # dict_keys(['time', 'temperature_2m', 'weather_code'])
print(data["current"]["temperature_2m"])    # 38.2
print(data["current"]["weather_code"])      # 0
```

This skill — fetching JSON, pretty-printing it, understanding its structure, extracting values — is the skill you use every time you integrate a new API. Practice it here.

---

## Exercises

**Exercise 1 — JSON round-trip test.**
Write a `test_json_roundtrip()` function that:
1. Creates a list of 3 tasks
2. Saves them to `test_tasks.json`
3. Loads them back
4. Compares each field of each task to the original
5. Prints `"✓ Round-trip test passed"` or lists any differences

This is your first informal test — a preview of Day 25.

**Exercise 2 — Pretty-print the storage file.**
Add a `"raw"` command that opens `taskflow_tasks.json` and prints its contents with `indent=2`. This lets you inspect the raw storage from inside the app. Compare what you see to what `display_tasks()` shows.

**Exercise 3 — Fetch weather for multiple cities.**
Write a `compare_weather(cities)` function that takes a list of `(name, lat, lon)` tuples and fetches weather for each. Display a comparison table:

```
City         Temp   Condition
──────────────────────────────
Delhi, IN    38°C   ☀ Clear
Mumbai, IN   31°C   ⛅ Partly cloudy
Bengaluru    27°C   🌧 Rain
```

**Exercise 4 — Cache the weather response.**
Re-fetching weather on every `"weather"` command wastes API calls. Add a simple cache: store the last fetched weather and its timestamp. Only re-fetch if the data is older than 10 minutes:

```python
import time

_weather_cache    = None
_weather_fetched  = 0
CACHE_TTL_SECONDS = 600   # 10 minutes

def get_cached_weather(lat, lon, location):
    global _weather_cache, _weather_fetched
    if _weather_cache is None or (time.time() - _weather_fetched) > CACHE_TTL_SECONDS:
        _weather_cache   = fetch_weather(lat, lon, location)
        _weather_fetched = time.time()
    return _weather_cache
```

**Exercise 5 — Parse a JSON string manually.**
Without using `json.load()`, write a function that reads the raw text of `taskflow_tasks.json`, passes it through `json.loads()`, and returns the task list. Verify the result is identical to calling `load_tasks()`. When would you use `json.loads()` vs `json.load()`?

**Exercise 6 (stretch) — Error resilience.**
Manually corrupt `taskflow_tasks.json` — delete a closing brace, add a stray character. Run the app and verify it handles the `JSONDecodeError` gracefully (no crash, clear error message, starts with empty list). Then add a `"repair"` command that tries to load the file, and if it fails, renames the corrupt file to `taskflow_tasks_corrupt_<timestamp>.json` and starts fresh. Never silently delete corrupted data — always preserve it.

---

## Checkpoint

Before moving to Day 10:

- [ ] I understand JSON's six data types and how they map to Python
- [ ] I use `json.dump()` / `json.load()` for files
- [ ] I use `json.dumps()` / `json.loads()` for strings
- [ ] I always pass `indent=2, ensure_ascii=False` when writing JSON files
- [ ] I understand `response.status_code` and always call `raise_for_status()`
- [ ] I always pass `timeout=` to `requests.get()`
- [ ] I handle `ConnectionError`, `Timeout`, and `HTTPError` separately
- [ ] `storage.py` uses JSON — no custom serialization code
- [ ] `weather.py` fetches and displays live weather
- [ ] TaskFlow AI shows weather in its header and responds to the `"weather"` command

---

## Common Errors on Day 09

**`json.JSONDecodeError` — invalid JSON string:**

```python
json.loads("{'key': 'value'}")   # ❌ single quotes are not valid JSON
json.loads('{"key": "value"}')   # ✅ double quotes required
```

JSON requires double quotes for strings. Python accepts both — JSON does not.

**`requests.exceptions.ConnectionError` — no internet:**

Always catch this separately. It means the DNS lookup or TCP connection failed — usually no internet, wrong URL, or a firewall blocking the request.

**Forgetting `timeout` — hanging forever:**

```python
requests.get(url)                      # ❌ hangs indefinitely if server is slow
requests.get(url, timeout=10)          # ✅ raises Timeout after 10 seconds
```

Never make a network request without a timeout in production code.

**`KeyError` parsing API response — field missing:**

```python
temp = data["current"]["temperature_2m"]   # ❌ crashes if key is absent
temp = data.get("current", {}).get("temperature_2m")  # ✅ safe
```

API responses change. Fields get renamed or removed. Always use `.get()` when parsing JSON from external sources.

**`TypeError: Object of type datetime is not JSON serializable`:**

```python
import datetime, json
task = {"created_at": datetime.datetime.now()}
json.dumps(task)   # ❌ TypeError — datetime objects are not JSON-serializable
```

Fix: convert to string before storing.

```python
task = {"created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
json.dumps(task)   # ✅ strings are JSON-serializable
```

---

## What's Coming

On **Day 10** we tackle error handling properly — `try`, `except`, `finally`, `raise`, and custom exceptions. Right now the app uses `if` checks and `.get()` defensively, but real production code needs structured exception handling. We will wrap every risky operation — file I/O, network calls, user input conversion — in proper `try/except` blocks, and write our first custom exception class. TaskFlow AI becomes genuinely crash-proof.