import sys
from .config import USER_LATITUDE, USER_LONGITUDE, USER_LOCATION, VERSION
from .errors import StorageError
from .storage.json_store import load_tasks_safe, backup_tasks
from .display.renderer import display_header
from .logging_config import setup_logging

__all__ = ["main"]


def main() -> None:
    """
    TaskFlow AI entry point.

    Supports two modes:
        Interactive: python run.py
        One-shot:    python run.py add "Review PR #high @work"
                     python run.py view --priority high
    """

    args       = sys.argv[1:]
    no_weather = "--no-weather" in args
    debug_mode = "--debug" in args

    # Configure logging FIRST — before anything else runs
    setup_logging(
        level   = "DEBUG" if debug_mode else "INFO",
        console = True,
        json_file = True,
    )

    import logging
    logger = logging.getLogger(__name__)
    logger.info("TaskFlow AI starting", extra={"version": VERSION})

    # Load tasks
    print()
    print("  Loading tasks...", end=" ", flush=True)
    tasks, load_error = load_tasks_safe()

    if load_error:
        print(f"\n  ⚠  {load_error}")
        print("  Creating backup and starting fresh.\n")
        try:
            backup_tasks()
        except Exception:
            pass  # backup failure is never critical
        tasks = []
    else:
        count = len(tasks)
        print(f"✓ {count} task{'s' if count != 1 else ''} loaded.")

    #  Fetch weather ─
    weather = None
    if not no_weather:
        try:
            from .integrations.weather import fetch_weather

            weather = fetch_weather(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
        except Exception:
            weather = None  # weather is never critical

    #  Render header ─
    display_header(weather)

    # Dispatch
    # Full argparse + dual-mode dispatch lives in cli.py (Day 15).
    # Check if any non-flag arguments were passed — if so, try CLI dispatch.
    non_flag_args = [a for a in args if not a.startswith("--")]

    if non_flag_args:
        # One-shot CLI mode
        try:
            from .cli import build_parser, run_one_shot

            parser = build_parser()
            parsed = parser.parse_args(args)
            if run_one_shot(parsed, tasks):
                return
        except ImportError:
            pass  # cli.py not available yet — fall through to shell

    # Interactive shell mode
    from .shell import run_interactive_shell

    run_interactive_shell(tasks)


if __name__ == "__main__":
    main()
