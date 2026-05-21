# taskflow/shell.py
# TaskFlow AI — Interactive command loop.
#
# Launched when the user runs `python run.py` with no subcommand.
# Delegates all command logic to display/commands.py.
# Handles Ctrl+C (KeyboardInterrupt) and Ctrl+D (EOFError) gracefully.
#
# Version history:
#   Day 04 — basic while loop in tasks.py
#   Day 06 — command functions extracted
#   Day 11 — moved to shell.py (Day 11 supplement)
#   Day 15 — Ctrl+C / Ctrl+D handling
#   Day 17 — exception handling tightened

from .errors import ValidationError, StorageError, TaskFlowError
from .display.commands import (
    cmd_add,
    cmd_view,
    cmd_done,
    cmd_remove,
    cmd_filter,
    cmd_search,
    cmd_stats,
    cmd_detail,
    cmd_rename,
    cmd_weather,
    cmd_forecast,
    cmd_backup,
    cmd_storage,
    cmd_quit,
)
from .display.renderer import display_help

__all__ = ["run_interactive_shell"]


def run_interactive_shell(tasks: list) -> None:
    """
    Run the interactive TaskFlow AI command loop.

    Reads commands from stdin until the user types 'quit'.
    Saves tasks on exit — including on Ctrl+C and Ctrl+D.

    Args:
        tasks (list): Loaded task list. Modified in place by commands.
    """
    display_help()

    while True:
        # ── Get command ───────────────────────────────────
        try:
            command = input("> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Interrupted — saving and exiting...")
            cmd_quit(tasks, save=True)
            break

        if not command:
            continue

        # ── Dispatch ──────────────────────────────────────
        try:
            if command == "add":
                cmd_add(tasks)
            elif command == "view":
                cmd_view(tasks)
            elif command == "done":
                cmd_done(tasks)
            elif command == "remove":
                cmd_remove(tasks)
            elif command == "filter":
                cmd_filter(tasks)
            elif command == "search":
                cmd_search(tasks)
            elif command == "stats":
                cmd_stats(tasks)
            elif command == "detail":
                cmd_detail(tasks)
            elif command == "rename":
                cmd_rename(tasks)
            elif command == "weather":
                cmd_weather()
            elif command == "forecast":
                cmd_forecast()
            elif command == "backup":
                cmd_backup()
            elif command == "storage":
                cmd_storage()
            elif command == "help":
                display_help()
            elif command == "quit":
                cmd_quit(tasks, save=True)
                break
            else:
                print(
                    f"\n  ✗ Unknown command '{command}'. "
                    f"Type 'help' to see all commands.\n"
                )

        except ValidationError as e:
            print(f"\n  ✗ Validation error: {e}\n")
        except StorageError as e:
            print(f"\n  ✗ Storage error: {e}\n")
        except TaskFlowError as e:
            print(f"\n  ✗ Error: {e}\n")
        except Exception as e:
            print(f"\n  ✗ Unexpected error [{type(e).__name__}]: {e}")
            print("  ℹ  The app will continue. Please report this bug.\n")
