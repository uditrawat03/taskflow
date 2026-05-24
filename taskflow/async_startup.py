# Async startup orchestration.
from __future__ import annotations
import asyncio, logging, time
from pathlib import Path
from .core.task  import Task
from .env_config import get_settings

logger = logging.getLogger(__name__)
__all__ = ["run_startup", "StartupResult"]


class StartupResult:
    """Container for all data gathered during async startup."""
    def __init__(self, tasks: list[Task], weather: dict | None,
                 load_error: str | None, elapsed_ms: float) -> None:
        self.tasks      = tasks
        self.weather    = weather
        self.load_error = load_error
        self.elapsed_ms = elapsed_ms

    @property
    def success(self) -> bool:
        return self.load_error is None

    def __repr__(self) -> str:
        return (f"StartupResult(tasks={len(self.tasks)}, "
                f"weather={'ok' if self.weather else 'none'}, "
                f"elapsed={self.elapsed_ms:.1f}ms)")


async def _load_tasks_async(filepath: Path) -> tuple[list[Task], str | None]:
    """Load tasks without blocking the event loop."""
    from .storage.json_store import load_tasks_safe
    tasks, error = await asyncio.to_thread(load_tasks_safe, filepath)
    if error:
        logger.error("Task load failed: %s", error)
    else:
        logger.info("Tasks loaded", extra={"count": len(tasks)})
    return tasks, error


async def _fetch_weather_async(lat: float, lon: float, location: str) -> dict | None:
    """Fetch weather without blocking. Falls back gracefully on any failure."""
    settings = get_settings()
    if not settings.weather_enabled:
        return None
    try:
        import aiohttp
        from .config import WEATHER_API_URL, WEATHER_TIMEOUT
        from .integrations.weather import WMO_CODES, WMO_EMOJI
        import datetime

        params  = {
            "latitude": lat, "longitude": lon,
            "current": ("temperature_2m,apparent_temperature,"
                        "relative_humidity_2m,wind_speed_10m,weather_code"),
            "wind_speed_unit": "kmh", "timezone": "auto",
        }
        headers = {"User-Agent": "TaskFlowAI/1.1", "Accept": "application/json"}

        async with aiohttp.ClientSession(headers=headers) as session:
            async with asyncio.timeout(WEATHER_TIMEOUT):
                async with session.get(WEATHER_API_URL, params=params) as resp:
                    resp.raise_for_status()
                    data    = await resp.json()
                    current = data.get("current", {})
                    code    = current.get("weather_code", 0)
                    return {
                        "location":    location,
                        "temperature": current.get("temperature_2m"),
                        "feels_like":  current.get("apparent_temperature"),
                        "humidity":    current.get("relative_humidity_2m"),
                        "wind_speed":  current.get("wind_speed_10m"),
                        "condition":   WMO_CODES.get(code, "Unknown"),
                        "emoji":       WMO_EMOJI.get(code, "🌡"),
                        "fetched_at":  datetime.datetime.now().strftime("%H:%M"),
                    }
    except ImportError:
        # aiohttp not installed — fall back to sync requests in a thread
        from .integrations.weather import fetch_weather
        return await asyncio.to_thread(fetch_weather, lat, lon, location)
    except (TimeoutError, Exception) as e:
        logger.warning("Async weather fetch failed: %s", e)
        return None


async def run_startup() -> StartupResult:
    """Run task loading and weather fetch concurrently."""
    settings   = get_settings()
    start_time = time.perf_counter()
    logger.info("Async startup beginning")

    (tasks, load_error), weather = await asyncio.gather(
        _load_tasks_async(settings.data_file),
        _fetch_weather_async(settings.user_latitude,
                             settings.user_longitude,
                             settings.user_location),
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    result     = StartupResult(tasks=tasks, weather=weather,
                                load_error=load_error, elapsed_ms=elapsed_ms)
    logger.info("Async startup complete",
                extra={"task_count": len(tasks), "weather_ok": weather is not None,
                       "elapsed_ms": round(elapsed_ms, 1)})
    return result