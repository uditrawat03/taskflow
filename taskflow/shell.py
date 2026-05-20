# taskflow/shell.py
# TaskFlow AI — Day 11
# Interactive command loop (the "shell" mode of the application).
# Launched when the user runs `python run.py` with no subcommand.

import re

from .config import (
    APP_NAME,
    USER_PLAN,
    MAX_TASKS_FREE,
    MAX_TASKS_PREMIUM,
    PLAN_LIMITS,
    VALID_PRIORITIES,
    VALID_CATEGORIES,
    USER_LATITUDE,
    USER_LONGITUDE,
    USER_LOCATION,
)
from .errors import ValidationError, StorageError, TaskFlowError
from .storage.json_store import save_tasks, backup_tasks, get_storage_info
from .integrations.weather import (
    fetch_weather,
    display_weather,
    fetch_forecast,
    display_forecast,
)
from .display.renderer import (
    display_tasks,
    display_task_detail,
    display_stats_dashboard,
    display_help,
    display_storage_info,
    display_help,
    prompt_valid,
    prompt_task_number,
    COMMANDS,
)

__all__ = ["run_interactive_shell"]


def run_interactive_shell(tasks: list) -> None:
    """
    Run the interactive TaskFlow AI command loop.

    Continues until the user types 'quit'. Saves tasks on exit.
    Handles KeyboardInterrupt (Ctrl+C) and EOFError (Ctrl+D) gracefully.

    Args:
        tasks (list): The loaded task list. Modified in place by commands.
    """
    max_tasks = PLAN_LIMITS.get(USER_PLAN, MAX_TASKS_FREE)
    weather = None  # fetched on demand or at startup by main()

    display_help()

    while True:
        # ── Get command ───────────────────────────────────
        try:
            command = input("> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Interrupted — saving tasks before exit...")
            _safe_save(tasks)
            print("  Goodbye!\n")
            break

        if not command:
            continue

        # ── Dispatch ──────────────────────────────────────
        try:
            if command == "add":
                _cmd_add(tasks, max_tasks)

            elif command == "view":
                display_tasks(tasks)

            elif command == "done":
                _cmd_done(tasks)

            elif command == "remove":
                _cmd_remove(tasks)

            elif command == "filter":
                _cmd_filter(tasks)

            elif command == "search":
                _cmd_search(tasks)

            elif command == "stats":
                display_stats_dashboard(tasks)

            elif command == "detail":
                _cmd_detail(tasks)

            elif command == "weather":
                weather = fetch_weather(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
                display_weather(weather)

            elif command == "forecast":
                forecast = fetch_forecast(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
                display_forecast(forecast, USER_LOCATION)

            elif command == "backup":
                backup_tasks()

            elif command == "storage":
                info = get_storage_info()
                display_storage_info(info)

            elif command == "help":
                display_help()

            elif command == "quit":
                _safe_save(tasks)
                stats = _quick_stats(tasks)
                print(
                    f"\n  Goodbye, Udit! "
                    f"{stats['done']}/{stats['total']} tasks complete."
                )
                print()
                break

            else:
                print(
                    f"\n  ✗ Unknown command '{command}'. "
                    f"Type 'help' to see available commands.\n"
                )

        except ValidationError as e:
            print(f"\n  ✗ Validation error: {e}\n")
        except StorageError as e:
            print(f"\n  ✗ Storage error: {e}\n")
        except TaskFlowError as e:
            print(f"\n  ✗ Error: {e}\n")
        except Exception as e:
            print(f"\n  ✗ Unexpected error: {type(e).__name__}: {e}")
            print("  ℹ  The app will continue. Please report this bug.\n")


# ─── Command Implementations ──────────────────────────────


def _cmd_add(tasks: list, max_tasks: int) -> None:
    """Prompt for task details and add a new task dictionary."""
    import datetime
    from .config import DATE_FMT

    if len(tasks) >= max_tasks:
        print(
            f"\n  ✗ Task limit reached ({max_tasks} tasks on "
            f"{USER_PLAN} plan). Upgrade to premium for more.\n"
        )
        return

    print()
    print(
        "  Shorthand: !! urgent | ~daily/weekly/monthly recurring "
        "| #priority | @category | !YYYY-MM-DD deadline"
    )
    print()

    raw = input("  Input: ").strip()
    if not raw:
        print("  ✗ Input cannot be empty.\n")
        return

    # Try smart parser if available; fall back to prompted input
    try:
        from .parser import parse_task_input, create_task_from_parse

        result = parse_task_input(raw)
        task = create_task_from_parse(result)
        task_dict = task.to_dict()
        tasks.append(task_dict)
        _print_add_confirmation(task_dict, len(tasks), max_tasks)
        return
    except ImportError:
        pass  # parser not available yet — use prompted input below
    except Exception as e:
        print(f"  ✗ Parser error: {e}")
        print("  Falling back to prompted input.\n")

    # Prompted input (fallback / Day 11 version)
    title = raw  # treat the whole input as the title

    priority = prompt_valid(
        "  Priority (high/medium/low): ", VALID_PRIORITIES, "priority"
    )
    category = prompt_valid(
        "  Category (work/personal/health/learning/other): ",
        VALID_CATEGORIES,
        "category",
    )

    task_dict = {
        "id": _next_id(tasks),
        "title": title,
        "priority": priority,
        "category": category,
        "status": "pending",
        "done": False,
        "created_at": datetime.datetime.now().strftime(DATE_FMT),
        "type": "standard",
    }
    tasks.append(task_dict)
    _print_add_confirmation(task_dict, len(tasks), max_tasks)


def _cmd_done(tasks: list) -> None:
    """Mark a selected task as done."""
    pending = [t for t in tasks if not t.get("done", False)]

    if not pending:
        print("\n  ✓ All tasks are already done! Great work.\n")
        return

    display_tasks(tasks)
    index = prompt_task_number(tasks, action="mark done")
    if index is None:
        return

    if tasks[index].get("done", False):
        print("  ✗ Task is already marked as done.\n")
        return

    tasks[index]["done"] = True
    tasks[index]["status"] = "done"

    # Handle RecurringTask reset behaviour
    if tasks[index].get("type") == "recurring":
        tasks[index]["done"] = False
        tasks[index]["status"] = "pending"
        tasks[index]["completion_count"] = tasks[index].get("completion_count", 0) + 1
        print(
            f'\n  ✓ "{tasks[index]["title"]}" completed '
            f"(×{tasks[index]['completion_count']}) — reset to pending.\n"
        )
    else:
        print(f'\n  ✓ "{tasks[index]["title"]}" marked as done!\n')


def _cmd_remove(tasks: list) -> None:
    """Remove a selected task from the list."""
    if not tasks:
        print("\n  ✗ No tasks to remove.\n")
        return

    display_tasks(tasks)
    index = prompt_task_number(tasks, action="remove")
    if index is None:
        return

    removed = tasks.pop(index)
    remaining = len(tasks)
    print(
        f'\n  ✓ "{removed["title"]}" removed. '
        f"({remaining} task{'s' if remaining != 1 else ''} remaining)\n"
    )


def _cmd_filter(tasks: list) -> None:
    """Filter and display tasks by priority or category."""
    print()
    print("  Filter by:")
    print("    1. Priority")
    print("    2. Category")
    print()

    choice = input("  Enter 1 or 2: ").strip()

    if choice == "1":
        priority = prompt_valid(
            "  Priority (high/medium/low): ", VALID_PRIORITIES, "priority"
        )
        filtered = [t for t in tasks if t.get("priority") == priority]
        if filtered:
            print(f"\n  {priority.upper()} priority tasks ({len(filtered)}):")
            display_tasks(filtered)
        else:
            print(f"\n  No {priority}-priority tasks found.\n")

    elif choice == "2":
        category = prompt_valid("  Category: ", VALID_CATEGORIES, "category")
        filtered = [t for t in tasks if t.get("category") == category]
        if filtered:
            print(f"\n  {category.title()} tasks ({len(filtered)}):")
            display_tasks(filtered)
        else:
            print(f"\n  No tasks in category '{category}'.\n")

    else:
        print("  ✗ Invalid choice. Enter 1 or 2.\n")


def _cmd_search(tasks: list) -> None:
    """Search tasks by keyword or regex pattern."""
    print()
    keyword = input("  Keyword (or re:pattern): ").strip()
    if not keyword:
        print("  ✗ Please enter a search term.\n")
        return

    use_regex = keyword.startswith("re:")
    matches = []

    if use_regex:
        pattern_str = keyword[3:]
        try:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matches = [t for t in tasks if pattern.search(t.get("title", ""))]
        except re.error as e:
            print(f"  ✗ Invalid regex '{pattern_str}': {e}\n")
            return
    else:
        kw = keyword.lower()
        matches = [t for t in tasks if kw in t.get("title", "").lower()]

    if matches:
        print(
            f"\n  Found {len(matches)} task{'s' if len(matches) != 1 else ''} "
            f"matching '{keyword}':"
        )
        display_tasks(matches)
    else:
        print(f"\n  No tasks matching '{keyword}'.\n")


def _cmd_detail(tasks: list) -> None:
    """Show full detail for a single task."""
    if not tasks:
        print("\n  ✗ No tasks to inspect.\n")
        return

    display_tasks(tasks)
    index = prompt_task_number(tasks, action="inspect")
    if index is None:
        return

    display_task_detail(tasks[index], index + 1)


# ─── Internal Helpers ─────────────────────────────────────


def _next_id(tasks: list) -> int:
    """Return the next available task ID."""
    return max((t.get("id", 0) for t in tasks), default=0) + 1


def _quick_stats(tasks: list) -> dict:
    """Return a minimal stats dict for the quit message."""
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("done", False))
    return {"total": total, "done": done}


def _safe_save(tasks: list) -> None:
    """Save tasks, printing a status message. Never raises."""
    from .storage.json_store import save_tasks

    try:
        save_tasks(tasks)
        print(f"  ✓ {len(tasks)} task{'s' if len(tasks) != 1 else ''} saved.")
    except StorageError as e:
        print(f"  ✗ Could not save tasks: {e}")
        print("  ⚠  Your changes may not have been persisted.")


def _print_add_confirmation(task: dict, total: int, max_tasks: int) -> None:
    """Print a confirmation message after adding a task."""
    print(f"\n  ✓ Task added! ({total} task{'s' if total != 1 else ''} total)")
    remaining = max_tasks - total
    if remaining <= 2:
        print(
            f"  ⚠  Only {remaining} task slot{'s' if remaining != 1 else ''} "
            f"remaining on your {USER_PLAN} plan."
        )
    print()
