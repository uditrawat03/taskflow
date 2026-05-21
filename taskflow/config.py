# taskflow/config.py
# TaskFlow AI — Central configuration.
# All constants live here. Import from this module everywhere.
# Never hardcode values in other modules.
#
# Version history:
#   Day 04 — inline constants in tasks.py
#   Day 06 — extracted to top of tasks.py
#   Day 11 — moved to dedicated config.py module
#   Day 14 — weather API constants added
#   Day 15 — VERSION bumped to 1.0.0
#   Day 18 — pyproject.toml created alongside; config.py remains for runtime use

from pathlib import Path

# ── Application ───────────────────────────────────────────
APP_NAME = "TaskFlow AI"
VERSION = "1.1.0"

# ── User profile ──────────────────────────────────────────
USER_NAME = "Udit"
USER_PLAN = "free"  # "free" | "premium" | "enterprise"
USER_LATITUDE = 28.6139  # Delhi, India
USER_LONGITUDE = 77.2090
USER_LOCATION = "Delhi, IN"

# ── Plan limits ───────────────────────────────────────────
MAX_TASKS_FREE = 10
MAX_TASKS_PREMIUM = 100
MAX_TASKS_ENTERPRISE = 10_000

PLAN_LIMITS: dict[str, int] = {
    "free": MAX_TASKS_FREE,
    "premium": MAX_TASKS_PREMIUM,
    "enterprise": MAX_TASKS_ENTERPRISE,
}

# ── Validation sets ───────────────────────────────────────
VALID_PRIORITIES: set[str] = {"high", "medium", "low"}
VALID_CATEGORIES: set[str] = {"work", "personal", "health", "learning", "other"}
VALID_PLANS: set[str] = set(PLAN_LIMITS.keys())

# ── Storage paths ─────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent  # project root
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "taskflow_tasks.json"
DATE_FMT = "%Y-%m-%d %H:%M"

# ── Weather API (Open-Meteo — no key required) ────────────
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_TIMEOUT = 10  # seconds before giving up
WEATHER_CACHE_TTL = 600  # seconds — 10-minute cache

# ── App behaviour ─────────────────────────────────────────
OVERDUE_THRESHOLD_DAYS = 7  # days before a pending task is flagged overdue
MAX_TITLE_LENGTH = 200  # characters
