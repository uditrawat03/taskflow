from pathlib import Path

APP_NAME = "TaskFlow AI"
VERSION  = "1.1.0"

# Validation sets — never vary by environment
VALID_PRIORITIES: set[str] = {"high", "medium", "low"}
VALID_CATEGORIES: set[str] = {"work", "personal", "health", "learning", "other"}
VALID_PLANS:      set[str] = {"free", "premium", "enterprise"}

PLAN_LIMITS: dict[str, int] = {
    "free":       10,
    "premium":    100,
    "enterprise": 10_000,
}

# Format strings — never vary by environment
DATE_FMT     = "%Y-%m-%d %H:%M"
LOG_DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"

# API constants — not secrets, but unlikely to change
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_TIMEOUT = 10    # seconds

# Behaviour constants
OVERDUE_THRESHOLD_DAYS = 7
MAX_TITLE_LENGTH       = 200
WEATHER_CACHE_TTL      = 600   # seconds

# Project root — needed by env_config and storage
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "taskflow_tasks.json"
DATE_FMT = "%Y-%m-%d %H:%M"
