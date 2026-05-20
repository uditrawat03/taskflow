"""
TaskFlow AI — Central configuration.
All constants live here. Import from this module, never hardcode.
"""

from pathlib import Path

# ── App ───────────────────────────────────────────────────
APP_NAME = "TaskFlow AI"
VERSION = "1.0.0"

# ── User ──────────────────────────────────────────────────
USER_NAME = "Udit"
USER_PLAN = "free"
USER_LATITUDE = 28.6139
USER_LONGITUDE = 77.2090
USER_LOCATION = "Delhi, IN"

# ── Limits ────────────────────────────────────────────────
MAX_TASKS_FREE = 10
MAX_TASKS_PREMIUM = 100

PLAN_LIMITS = {
    "free": MAX_TASKS_FREE,
    "premium": MAX_TASKS_PREMIUM,
    "enterprise": 10_000,
}

# ── Validation ────────────────────────────────────────────
VALID_PRIORITIES = {"high", "medium", "low"}
VALID_CATEGORIES = {"work", "personal", "health", "learning", "other"}
VALID_PLANS = set(PLAN_LIMITS.keys())

# ── Storage ───────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent  # project root
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "taskflow_tasks.json"
DATE_FMT = "%Y-%m-%d %H:%M"

# ── Weather ───────────────────────────────────────────────
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_TIMEOUT = 10
WEATHER_CACHE_TTL = 600  # seconds
