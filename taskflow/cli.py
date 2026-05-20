import argparse
import sys
from pathlib import Path

from .config import APP_NAME, VERSION, USER_LATITUDE, USER_LONGITUDE, USER_LOCATION
from .errors import TaskFlowError, ValidationError, StorageError
from .storage.json_store import load_tasks, save_tasks, backup_tasks
from .core.task import Task
from .core.stats import calculate_stats, priority_breakdown, category_breakdown
from .parser import parse_task_input, create_task_from_parse
from .integrations.weather import (
    fetch_weather,
    display_weather,
    fetch_forecast,
    display_forecast,
)
from .display.renderer import display_tasks, display_stats_dashboard, display_header


def build_parser() -> argparse.ArgumentParser:
    """Build and return the full argument parser."""

    parser = argparse.ArgumentParser(
        prog="taskflow",
        description=f"{APP_NAME} — Intelligent task management from the terminal.",
        epilog="Run without arguments to launch the interactive shell.",
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
        help="Skip weather fetch at startup (faster cold start)",
    )
    parser.add_argument(
        "--data",
        metavar="PATH",
        type=Path,
        help="Use a custom JSON data file",
    )

    subs = parser.add_subparsers(dest="command", metavar="command")

    # add
    p_add = subs.add_parser("add", help="Add a task (shorthand supported)")
    p_add.add_argument(
        "input",
        nargs="?",
        default="",
        help='Task input, e.g. "Review PR #high @work !2025-06-01"',
    )

    # view
    p_view = subs.add_parser("view", help="View tasks")
    p_view.add_argument("--priority", choices=["high", "medium", "low"])
    p_view.add_argument("--category")
    p_view.add_argument("--done", action="store_true")
    p_view.add_argument("--pending", action="store_true")
    p_view.add_argument("--overdue", action="store_true")

    # done
    p_done = subs.add_parser("done", help="Mark a task done by ID")
    p_done.add_argument("id", type=int, help="Task ID")

    # remove
    p_remove = subs.add_parser("remove", help="Remove a task by ID")
    p_remove.add_argument("id", type=int, help="Task ID")

    # search
    p_search = subs.add_parser("search", help="Search tasks")
    p_search.add_argument("keyword", help="Keyword or re:pattern")

    # stats
    subs.add_parser("stats", help="Statistics dashboard")
    subs.add_parser("forecast", help="3-day weather forecast")
    subs.add_parser("backup", help="Backup task data")

    return parser


def run_one_shot(args: argparse.Namespace, tasks: list[Task]) -> bool:
    """
    Execute a single non-interactive command and return True,
    or return False if no command was given (caller should launch shell).

    Args:
        args  (Namespace): Parsed arguments.
        tasks (list)     : Loaded task list.

    Returns:
        bool: True if a command was executed, False if interactive mode needed.
    """
    if not args.command:
        return False  # no subcommand — launch interactive shell

    if args.command == "add":
        raw = args.input or input("  Input: ").strip()
        try:
            result = parse_task_input(raw)
            task = create_task_from_parse(result)
            tasks.append(task)
            save_tasks(tasks, args.data or None)
            print(f"\n  ✓ {type(task).__name__} created: {task.title}")
            _print_task_meta(task)
        except (ValidationError, StorageError) as e:
            print(f"\n  ✗ {e}")

    elif args.command == "view":
        filtered = tasks[:]
        if args.priority:
            filtered = [t for t in filtered if t.priority == args.priority]
        if args.category:
            filtered = [t for t in filtered if t.category == args.category]
        if args.done:
            filtered = [t for t in filtered if t.done]
        if args.pending:
            filtered = [t for t in filtered if not t.done]
        if args.overdue:
            filtered = [t for t in filtered if t.is_overdue()]
        display_tasks(filtered)

    elif args.command == "done":
        task = _find_by_id(tasks, args.id)
        if task:
            task.mark_done()
            save_tasks(tasks, args.data or None)
            print(f'\n  ✓ "{task.title}" marked as done.\n')

    elif args.command == "remove":
        task = _find_by_id(tasks, args.id)
        if task:
            tasks.remove(task)
            save_tasks(tasks, args.data or None)
            print(f'\n  ✓ "{task.title}" removed.\n')

    elif args.command == "search":
        kw = args.keyword
        import re

        use_regex = kw.startswith("re:")
        pattern = kw[3:] if use_regex else None
        results = []
        for t in tasks:
            if use_regex:
                try:
                    if re.search(pattern, t.title, re.IGNORECASE):
                        results.append(t)
                except re.error as e:
                    print(f"  ✗ Invalid regex: {e}")
                    return True
            else:
                if kw.lower() in t.title.lower():
                    results.append(t)
        if results:
            print(f"\n  Found {len(results)} task(s):")
            display_tasks(results)
        else:
            print(f"\n  No tasks matching '{kw}'.\n")

    elif args.command == "stats":
        display_stats_dashboard(tasks)

    elif args.command == "forecast":
        forecast = fetch_forecast(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
        display_forecast(forecast, USER_LOCATION)

    elif args.command == "backup":
        backup_tasks()

    return True


def _find_by_id(tasks: list[Task], task_id: int) -> Task | None:
    """Find a task by ID. Prints error and returns None if not found."""
    for task in tasks:
        if task.id == task_id:
            return task
    print(f"\n  ✗ No task found with ID {task_id}.\n")
    return None


def _print_task_meta(task: Task) -> None:
    """Print type-specific metadata after task creation."""
    print(f"    Priority : {task.priority}")
    print(f"    Category : {task.category}")
    if hasattr(task, "due_date"):
        print(f"    Due      : {task.due_date} ({task.urgency_label})")
    if hasattr(task, "recurrence"):
        print(f"    Recurs   : {task.recurrence}")
    print()
