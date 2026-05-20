# taskflow/main.py
# TaskFlow AI — Day 11
# Application entry point.
# Orchestrates startup: load tasks, fetch weather, launch shell or CLI.

from .config  import USER_LATITUDE, USER_LONGITUDE, USER_LOCATION
from .errors  import StorageError
from .storage.json_store import load_tasks_safe, backup_tasks
from .display.renderer   import display_header


def main() -> None:
    """
    TaskFlow AI entry point.

    Responsibilities:
    1. Parse command-line arguments (if any)
    2. Load persisted tasks from JSON storage
    3. Handle storage errors gracefully (backup + fresh start)
    4. Fetch weather data for the header
    5. Dispatch to CLI one-shot mode OR interactive shell

    This function is kept intentionally thin — each concern is
    delegated to the appropriate module.
    """

    # ── Parse arguments ───────────────────────────────────
    # Full argparse integration arrives on Day 15.
    # For Day 11, we use a minimal argument check.
    import sys
    args       = sys.argv[1:]
    no_weather = "--no-weather" in args

    # ── Load tasks ────────────────────────────────────────
    print()
    print("  Loading tasks...", end=" ", flush=True)
    tasks, load_error = load_tasks_safe()

    if load_error:
        print(f"\n  ⚠  {load_error}")
        print("  Creating a backup and starting with an empty task list.")
        try:
            backup_tasks()
        except Exception:
            pass   # backup failure is never critical — continue
        tasks = []
    else:
        count = len(tasks)
        print(f"✓ {count} task{'s' if count != 1 else ''} loaded.")

    # ── Fetch weather ─────────────────────────────────────
    weather = None
    if not no_weather:
        try:
            from .integrations.weather import fetch_weather
            weather = fetch_weather(
                USER_LATITUDE, USER_LONGITUDE, USER_LOCATION
            )
        except Exception:
            weather = None   # weather is non-critical — never crash for it

    # ── Display header ────────────────────────────────────
    display_header(weather)

    # ── Launch shell or CLI ───────────────────────────────
    # Day 15 replaces this block with full argparse + dual-mode dispatch.
    # For now, always launch the interactive shell.
    from .shell import run_interactive_shell
    run_interactive_shell(tasks)


if __name__ == "__main__":
    main()