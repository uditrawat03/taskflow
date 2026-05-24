# taskflow/cli.py — argparse CLI and one-shot dispatcher. Day 15.
from __future__ import annotations
import argparse
from pathlib import Path
from .config import APP_NAME, VERSION
from .errors import ValidationError, StorageError
from .storage.json_store import save_tasks
from .display.commands import (
    cmd_add, cmd_view, cmd_done, cmd_remove,
    cmd_search, cmd_stats, cmd_weather, cmd_forecast,
    cmd_backup, cmd_storage,
)
from .display.renderer import display_tasks

__all__ = ["build_parser", "run_one_shot"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taskflow",
        description=f"{APP_NAME} — Intelligent task management from the terminal.",
        epilog="Run without arguments to launch the interactive shell.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {VERSION}")
    parser.add_argument("--no-weather", action="store_true", dest="no_weather",
                        help="Skip weather fetch at startup")
    parser.add_argument("--debug", action="store_true", help="Enable DEBUG logging")
    parser.add_argument("--data", metavar="PATH", type=Path, default=None,
                        help="Use a custom JSON data file path")

    subs = parser.add_subparsers(dest="command", metavar="command")

    p_add = subs.add_parser("add", help="Add a task")
    p_add.add_argument("input", nargs="?", default="",
                       help='Task input e.g. "Review PR #high @work !2025-06-01"')

    p_view = subs.add_parser("view", help="View tasks")
    p_view.add_argument("--priority", choices=["high","medium","low"])
    p_view.add_argument("--category")
    p_view.add_argument("--done",    action="store_true")
    p_view.add_argument("--pending", action="store_true")
    p_view.add_argument("--overdue", action="store_true")
    p_view.add_argument("--limit",   type=int, default=None)

    p_done = subs.add_parser("done", help="Mark a task done by ID")
    p_done.add_argument("id", type=int)

    p_remove = subs.add_parser("remove", help="Remove a task by ID")
    p_remove.add_argument("id", type=int)

    p_search = subs.add_parser("search", help="Search tasks")
    p_search.add_argument("keyword")

    subs.add_parser("stats",    help="Statistics dashboard")
    subs.add_parser("weather",  help="Current weather")
    subs.add_parser("forecast", help="3-day forecast")
    subs.add_parser("backup",   help="Backup task data")
    subs.add_parser("storage",  help="Storage file info")

    return parser


def run_one_shot(args: argparse.Namespace, tasks: list) -> bool:
    """Execute a single command. Returns True if handled, False for interactive mode."""
    if not args.command:
        return False

    custom_filepath = getattr(args, "data", None)

    def _auto_save():
        try:
            kw = {"filepath": custom_filepath} if custom_filepath else {}
            save_tasks(tasks, **kw)
        except StorageError as e:
            print(f"\n  ⚠  Could not save tasks: {e}\n")

    try:
        if args.command == "add":
            cmd_add(tasks, raw_input=getattr(args, "input", ""))
            _auto_save()

        elif args.command == "view":
            cmd_view(tasks,
                     priority    = getattr(args, "priority", None),
                     category    = getattr(args, "category", None),
                     show_done   = getattr(args, "done",    False),
                     show_pending = getattr(args, "pending", False),
                     show_overdue = getattr(args, "overdue", False),
                     limit       = getattr(args, "limit",   None))

        elif args.command == "done":
            cmd_done(tasks, task_id=args.id)
            _auto_save()

        elif args.command == "remove":
            cmd_remove(tasks, task_id=args.id)
            _auto_save()

        elif args.command == "search":
            cmd_search(tasks, keyword=args.keyword)

        elif args.command == "stats":    cmd_stats(tasks)
        elif args.command == "weather":  cmd_weather()
        elif args.command == "forecast": cmd_forecast()
        elif args.command == "backup":   cmd_backup()
        elif args.command == "storage":  cmd_storage()

    except ValidationError as e:
        print(f"\n  ✗ {e}\n")
    except StorageError as e:
        print(f"\n  ✗ Storage error: {e}\n")
    except Exception as e:
        print(f"\n  ✗ Unexpected error [{type(e).__name__}]: {e}\n")

    return True
