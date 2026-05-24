# Application entry point. Day 11/23/24/30.
from __future__ import annotations
import asyncio, sys

__all__ = ["main"]


def main() -> None:
    """
    TaskFlow AI entry point.

    Flow:
      1. Load settings from environment / .env
      2. Configure logging
      3. Run async startup (load tasks + fetch weather concurrently)
      4. Handle startup errors gracefully
      5. Dispatch to one-shot CLI or interactive shell
    """
    from .env_config      import get_settings
    from .logging_config  import setup_logging

    args     = sys.argv[1:]
    settings = get_settings()

    # ── Logging ───────────────────────────────────────────
    setup_logging(
        level     = "DEBUG" if "--debug" in args else settings.log_level,
        log_dir   = settings.log_dir if settings.log_to_file else None,
        json_file = settings.log_to_file,
        console   = settings.log_to_console,
    )

    import logging
    logger = logging.getLogger(__name__)
    logger.info("TaskFlow AI starting", extra={"version": "1.1.0",
                                               "user": settings.user_name})

    # ── Async startup ─────────────────────────────────────
    print()
    print("  Starting up...", end=" ", flush=True)

    no_weather  = "--no-weather" in args or not settings.weather_enabled
    if no_weather:
        # Skip async startup; load tasks synchronously only
        from .storage.json_store import load_tasks_safe, backup_tasks
        tasks, load_error = load_tasks_safe()
        weather           = None
        elapsed_ms        = 0.0
    else:
        from .async_startup import run_startup
        result     = asyncio.run(run_startup())
        tasks      = result.tasks
        weather    = result.weather
        load_error = result.load_error
        elapsed_ms = result.elapsed_ms

    # ── Handle load errors ────────────────────────────────
    if load_error:
        print(f"\n  ⚠  {load_error}")
        logger.error("Startup load error: %s", load_error)
        print("  Starting with an empty task list.\n")
        tasks = []
        try:
            from .storage.json_store import backup_tasks
            backup_tasks()
        except Exception:
            pass
    else:
        count = len(tasks)
        suffix = f", startup in {elapsed_ms:.0f}ms" if elapsed_ms else ""
        print(f"✓ {count} task{'s' if count != 1 else ''} loaded{suffix}")

    # ── Header ────────────────────────────────────────────
    from .display.renderer import display_header
    display_header(weather)

    # ── Register event handlers ───────────────────────────
    _register_event_handlers()

    # ── Dispatch to CLI or shell ──────────────────────────
    non_flag_args = [a for a in args if not a.startswith("--")]
    if non_flag_args:
        try:
            from .cli import build_parser, run_one_shot
            parsed = build_parser().parse_args(args)
            if run_one_shot(parsed, tasks):
                return
        except ImportError:
            pass

    from .shell import run_interactive_shell
    run_interactive_shell(tasks)


def _register_event_handlers() -> None:
    """Register built-in application event handlers on the global event bus."""
    import logging
    _log = logging.getLogger("taskflow.events")

    try:
        from .events import event_bus, Events
        from .core.task import Task

        @event_bus.on(Events.TASK_ADDED)
        def _log_task_added(task: Task) -> None:
            _log.info("Task added: '%s' [%s]", task.title, task.priority)

        @event_bus.on(Events.TASK_DONE)
        def _log_task_done(task: Task) -> None:
            _log.info("Task completed: '%s'", task.title)

        @event_bus.on(Events.LIMIT_REACHED)
        def _warn_limit(current: int, limit: int) -> None:
            _log.warning("Task limit reached: %d/%d", current, limit)

        @event_bus.on(Events.STORAGE_ERROR)
        def _alert_storage(error: Exception) -> None:
            _log.critical("STORAGE ERROR: %s", error)

    except Exception:
        pass   # events are non-critical — never crash startup


if __name__ == "__main__":
    main()
