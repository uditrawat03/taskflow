# taskflow/main.py
# TaskFlow AI — Application entry point.
#
# Thin orchestration layer:
#   1. Parse command-line arguments
#   2. Load tasks from JSON storage
#   3. Handle storage errors gracefully
#   4. Fetch weather (non-critical)
#   5. Render header
#   6. Dispatch to CLI (one-shot) or shell (interactive)
#
# Version history:
#   Day 04 — inline in tasks.py
#   Day 11 — extracted to main.py (Day 11 supplement)
#   Day 15 — argparse + dual-mode dispatch added (cli.py)

from .config import USER_LATITUDE, USER_LONGITUDE, USER_LOCATION
from .errors import StorageError
from .storage.json_store import load_tasks_safe, backup_tasks
from .display.renderer import display_header

__all__ = ["main"]


def main() -> None:
    """
    TaskFlow AI entry point.

    Supports two modes:
        Interactive: python run.py
        One-shot:    python run.py add "Review PR #high @work"
                     python run.py view --priority high
    """
    import sys

    args = sys.argv[1:]
    no_weather = "--no-weather" in args

    # ── Load tasks ────────────────────────────────────────
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

    # ── Fetch weather ─────────────────────────────────────
    weather = None
    if not no_weather:
        try:
            from .integrations.weather import fetch_weather

            weather = fetch_weather(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
        except Exception:
            weather = None  # weather is never critical

    # ── Render header ─────────────────────────────────────
    display_header(weather)

    # ── Dispatch ──────────────────────────────────────────
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
