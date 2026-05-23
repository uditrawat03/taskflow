import sys
from .env_config import get_settings
from .config import VERSION
from .display.renderer import display_header
from .logging_config import setup_logging

__all__ = ["main"]


def main() -> None:
    """Application entry point."""

    args = sys.argv[1:]
    settings = get_settings()

    # Configure logging from settings
    setup_logging(
        level="DEBUG" if "--debug" in args else settings.log_level,
        log_dir=settings.log_dir if settings.log_to_file else None,
        json_file=settings.log_to_file,
        console=settings.log_to_console,
    )

    import logging

    logger = logging.getLogger(__name__)
    logger.info(
        "TaskFlow AI starting", extra={"version": VERSION, "user": settings.user_name}
    )

    # Load tasks using path from settings
    from .storage.json_store import load_tasks_safe, backup_tasks

    print()
    print("  Loading tasks...", end=" ", flush=True)
    tasks, load_error = load_tasks_safe(settings.data_file)

    if load_error:
        print(f"\n  ⚠  {load_error}")
        logger.error("Task load failed: %s", load_error)
        print("  Creating backup and starting fresh.\n")
        try:
            backup_tasks(settings.data_file)
        except Exception:
            pass
        tasks = []
    else:
        count = len(tasks)
        print(f"✓ {count} task{'s' if count != 1 else ''} loaded.")
        logger.info("Tasks loaded", extra={"count": count})

    # Weather
    weather = None
    if settings.weather_enabled and "--no-weather" not in args:
        try:
            from .integrations.weather import fetch_weather

            weather = fetch_weather(
                settings.user_latitude,
                settings.user_longitude,
                settings.user_location,
            )
        except Exception as e:
            logger.warning("Weather fetch failed: %s", e)

    display_header(weather)

    from .shell import run_interactive_shell

    run_interactive_shell(tasks)


if __name__ == "__main__":
    main()
