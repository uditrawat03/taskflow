# taskflow/cli.py
# TaskFlow AI — Argument parser and one-shot CLI dispatcher.
#
# Supports dual-mode operation:
#   Interactive: python run.py
#   One-shot:    python run.py add "Review PR #high @work"
#                python run.py view --priority high --pending
#                python run.py done 3
#
# Version history:
#   Day 15 — initial implementation with argparse + subcommands

import argparse
import sys
from pathlib import Path

from .config import APP_NAME, VERSION, USER_LATITUDE, USER_LONGITUDE, USER_LOCATION
from .errors import ValidationError, StorageError
from .storage.json_store import save_tasks, backup_tasks
from .core.task import Task
from .core.stats import calculate_stats
from .display.commands import (
    cmd_add, cmd_view, cmd_done, cmd_remove,
    cmd_filter, cmd_search, cmd_stats,
    cmd_weather, cmd_forecast, cmd_backup, cmd_storage, cmd_quit,
)
from .display.renderer import display_tasks

__all__ = ["build_parser", "run_one_shot"]


def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the full argument parser for TaskFlow AI.

    Returns:
        argparse.ArgumentParser: Configured parser with all subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="taskflow",
        description=(
            f"{APP_NAME} — Intelligent task management from the terminal.\n"
            "Run without arguments to launch the interactive shell."
        ),
        epilog="Shorthand: !!  ~daily/weekly/monthly  #priority  @category  !YYYY-MM-DD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{APP_NAME} {VERSION}",
    )
    parser.add_argument(
        "--no-weather",
        action="store_true",
        dest="no_weather",
        help="Skip weather fetch at startup (faster cold start)",
    )
    parser.add_argument(
        "--data",
        metavar="PATH",
        type=Path,
        default=None,
        help="Use a custom JSON data file path",
    )

    subs = parser.add_subparsers(dest="command", metavar="command")

    # ── add ───────────────────────────────────────────────
    p_add = subs.add_parser("add", help="Add a task (shorthand supported)")
    p_add.add_argument(
        "input",
        nargs="?",
        default="",
        help='Task input, e.g. "Review PR #high @work !2025-06-01"',
    )

    # ── view ──────────────────────────────────────────────
    p_view = subs.add_parser("view", help="View all tasks")
    p_view.add_argument("--priority", choices=["high", "medium", "low"],
                        help="Filter by priority")
    p_view.add_argument("--category", help="Filter by category")
    p_view.add_argument("--done",    action="store_true",
                        help="Show only completed tasks")
    p_view.add_argument("--pending", action="store_true",
                        help="Show only pending tasks")
    p_view.add_argument("--overdue", action="store_true",
                        help="Show only overdue tasks")
    p_view.add_argument("--limit",   type=int, default=None,
                        help="Show at most N tasks")

    # ── done ──────────────────────────────────────────────
    p_done = subs.add_parser("done", help="Mark a task as done by ID")
    p_done.add_argument("id", type=int, help="Task ID")

    # ── remove ────────────────────────────────────────────
    p_remove = subs.add_parser("remove", help="Remove a task by ID")
    p_remove.add_argument("id", type=int, help="Task ID")

    # ── search ────────────────────────────────────────────
    p_search = subs.add_parser("search", help="Search tasks by keyword or regex")
    p_search.add_argument("keyword", help="Keyword or re:pattern")

    # ── stats ─────────────────────────────────────────────
    subs.add_parser("stats",    help="Show statistics dashboard")

    # ── weather / forecast ────────────────────────────────
    subs.add_parser("weather",  help="Show current weather")
    subs.add_parser("forecast", help="Show 3-day weather forecast")

    # ── backup / storage ──────────────────────────────────
    subs.add_parser("backup",   help="Create a timestamped backup")
    subs.add_parser("storage",  help="Show storage file information")

    return parser


def run_one_shot(args: argparse.Namespace, tasks: list) -> bool:
    """
    Execute a single non-interactive command.

    Args:
        args  (Namespace): Parsed CLI arguments.
        tasks (list)     : Loaded task list.

    Returns:
        bool: True if a command was executed (caller should exit);
              False if no subcommand was given (caller should launch shell).
    """
    if not args.command:
        return False   # no subcommand — launch interactive shell

    custom_filepath = getattr(args, "data", None)

    try:
        if args.command == "add":
            raw = args.input or ""
            cmd_add(tasks, raw_input=raw)
            _auto_save(tasks, custom_filepath)

        elif args.command == "view":
            cmd_view(
                tasks,
                priority=getattr(args, "priority", None),
                category=getattr(args, "category", None),
                show_done=getattr(args, "done", False),
                show_pending=getattr(args, "pending", False),
                show_overdue=getattr(args, "overdue", False),
                limit=getattr(args, "limit", None),
            )

        elif args.command == "done":
            cmd_done(tasks, task_id=args.id)
            _auto_save(tasks, custom_filepath)

        elif args.command == "remove":
            cmd_remove(tasks, task_id=args.id)
            _auto_save(tasks, custom_filepath)

        elif args.command == "search":
            cmd_search(tasks, keyword=args.keyword)

        elif args.command == "stats":
            cmd_stats(tasks)

        elif args.command == "weather":
            cmd_weather()

        elif args.command == "forecast":
            cmd_forecast()

        elif args.command == "backup":
            cmd_backup()

        elif args.command == "storage":
            cmd_storage()

    except ValidationError as e:
        print(f"\n  ✗ {e}\n")
    except StorageError as e:
        print(f"\n  ✗ Storage error: {e}\n")
    except Exception as e:
        print(f"\n  ✗ Unexpected error [{type(e).__name__}]: {e}\n")

    return True   # command was executed


def _auto_save(tasks: list, filepath: Path | None = None) -> None:
    """Save tasks after a mutating one-shot command."""
    try:
        kwargs = {"filepath": filepath} if filepath else {}
        save_tasks(tasks, **kwargs)
    except StorageError as e:
        print(f"\n  ⚠  Could not save tasks: {e}\n")