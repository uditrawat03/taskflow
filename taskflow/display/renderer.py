
from ..config import APP_NAME, VERSION, USER_NAME, USER_PLAN, PLAN_LIMITS


# ─── Header ───────────────────────────────────────────────

def display_header(weather: dict | None = None) -> None:
    """
    Print the application header banner.

    Args:
        weather (dict | None): Weather data from fetch_weather().
                               If provided, a one-line summary is shown.
    """
    max_tasks = PLAN_LIMITS.get(USER_PLAN, 10)

    print("=" * 44)
    print(f"   {APP_NAME} — Task Manager v{VERSION}")
    if weather:
        emoji    = weather.get("emoji", "🌡")
        temp     = weather.get("temperature", "?")
        cond     = weather.get("condition", "")
        location = weather.get("location", "")
        print(f"   📍 {location}  |  {emoji} {temp}°C  {cond}")
    print("=" * 44)
    print(f"   Hello, {USER_NAME}!  "
          f"Plan: {USER_PLAN.title()} ({max_tasks} tasks max)")
    print()


# ─── Task Table ───────────────────────────────────────────

def display_tasks(tasks: list) -> None:
    """
    Display a list of tasks as a formatted table.

    Shows task number, title (truncated if needed), priority,
    category, and status. Prints a summary line below the table.

    Args:
        tasks (list): List of task dictionaries to display.
    """
    if not tasks:
        print("\n  No tasks to display. Type 'add' to create one.\n")
        return

    # Column widths
    col = {
        "num":      4,
        "title":    26,
        "priority": 10,
        "category": 13,
        "status":   10,
    }
    width = sum(col.values()) + 4   # +4 for leading spaces

    divider = "  " + "─" * width

    print()
    print(divider)
    print(
        f"  {'#':<{col['num']}}"
        f"{'Title':<{col['title']}}"
        f"{'Priority':<{col['priority']}}"
        f"{'Category':<{col['category']}}"
        f"Status"
    )
    print(divider)

    for i, task in enumerate(tasks, start=1):
        title  = task.get("title", "")
        # Truncate long titles
        if len(title) >= col["title"]:
            title = title[: col["title"] - 2] + ".."

        done   = task.get("done", False)
        status = "✓ done" if done else "pending"

        print(
            f"  {i:<{col['num']}}"
            f"{title:<{col['title']}}"
            f"{task.get('priority', '').upper():<{col['priority']}}"
            f"{task.get('category', ''):<{col['category']}}"
            f"{status}"
        )

    print(divider)

    # Summary line
    total   = len(tasks)
    done    = sum(1 for t in tasks if t.get("done", False))
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0
    print(f"  {total} task{'s' if total != 1 else ''} · "
          f"{pending} pending · {done} done · {rate}% complete")
    print()


# ─── Task Detail ──────────────────────────────────────────

def display_task_detail(task: dict, index: int) -> None:
    """
    Display a single task in full detail — all fields shown.

    Args:
        task  (dict): The task dictionary.
        index (int) : 1-based display number.
    """
    done   = task.get("done", False)
    status = "✓ done" if done else "○ pending"

    print()
    print(f"  ── Task Detail — #{index} ─────────────────────")
    print(f"  {'ID':<14}: {task.get('id', '?')}")
    print(f"  {'Title':<14}: {task.get('title', '')}")
    print(f"  {'Priority':<14}: {task.get('priority', '').upper()}")
    print(f"  {'Category':<14}: {task.get('category', '')}")
    print(f"  {'Status':<14}: {status}")
    print(f"  {'Created':<14}: {task.get('created_at', 'unknown')}")

    # Show type-specific fields if present
    task_type = task.get("type", "standard")
    if task_type == "deadline" and "due_date" in task:
        print(f"  {'Due date':<14}: {task['due_date']}")
    elif task_type == "recurring" and "recurrence" in task:
        print(f"  {'Recurrence':<14}: {task['recurrence']}")
        print(f"  {'Completions':<14}: {task.get('completion_count', 0)}")
    elif task_type == "urgent":
        print(f"  {'Type':<14}: 🚨 Urgent")

    print()


# ─── Statistics Dashboard ─────────────────────────────────

def display_stats_dashboard(tasks: list) -> None:
    """
    Display a statistics summary dashboard for the task list.

    Shows totals, completion rate, and breakdowns by priority and category.

    Args:
        tasks (list): List of task dictionaries.
    """
    total   = len(tasks)
    done    = sum(1 for t in tasks if t.get("done", False))
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0

    print()
    print("  ── Task Statistics ──────────────────────────")
    print(f"  {'Total':<14}: {total}")
    print(f"  {'Done':<14}: {done}  ({rate}%)")
    print(f"  {'Pending':<14}: {pending}")

    if tasks:
        # Priority breakdown
        print()
        print("  By Priority:")
        for priority in ["high", "medium", "low"]:
            count = sum(1 for t in tasks if t.get("priority") == priority)
            bar   = "█" * count + "░" * (10 - min(count, 10))
            print(f"    {priority.upper():<8} {count:>3}  {bar}")

        # Category breakdown
        categories = sorted({t.get("category", "other") for t in tasks})
        if categories:
            print()
            print("  By Category:")
            for cat in categories:
                count = sum(1 for t in tasks if t.get("category") == cat)
                done_in_cat = sum(
                    1 for t in tasks
                    if t.get("category") == cat and t.get("done", False)
                )
                print(f"    {cat:<14} {count:>2} tasks  "
                      f"({done_in_cat} done)")

        # Type breakdown (if mixed types exist)
        types = {t.get("type", "standard") for t in tasks}
        if len(types) > 1:
            print()
            print("  By Type:")
            for task_type in sorted(types):
                count = sum(1 for t in tasks if t.get("type", "standard") == task_type)
                print(f"    {task_type:<14} {count:>2}")

    print()


# ─── Help ─────────────────────────────────────────────────

# Maps command name → description.
# Update this dict whenever commands are added or removed.
COMMANDS: dict[str, str] = {
    "add":     "Add a new task (shorthand syntax supported)",
    "view":    "View all tasks in a table",
    "done":    "Mark a task as done",
    "remove":  "Remove a task permanently",
    "filter":  "Filter tasks by priority or category",
    "search":  "Search tasks by keyword or regex (re:pattern)",
    "stats":   "Show statistics dashboard",
    "detail":  "Show full detail for one task",
    "weather": "Show current weather",
    "forecast":"Show 3-day weather forecast",
    "backup":  "Create a timestamped backup of task data",
    "storage": "Show storage file information",
    "help":    "Show this help reference",
    "quit":    "Save and exit",
}


def display_help() -> None:
    """Print the command reference table."""
    print()
    print("  ── Commands ─────────────────────────────────")
    for cmd, desc in COMMANDS.items():
        print(f"    {cmd:<12} — {desc}")
    print()


# ─── Storage Info ─────────────────────────────────────────

def display_storage_info(info: dict) -> None:
    """
    Display metadata about the storage file.

    Args:
        info (dict): Output from storage.json_store.get_storage_info().
    """
    print()
    print("  ── Storage Info ─────────────────────────────")
    if not info.get("exists"):
        print("  No storage file found yet.")
        print("  It will be created the first time you add a task.")
    else:
        print(f"  {'File':<14}: {info.get('filepath', 'unknown')}")
        size_kb = round(info.get("size_bytes", 0) / 1024, 2)
        print(f"  {'Size':<14}: {info.get('size_bytes', 0)} bytes ({size_kb} KB)")
        print(f"  {'Last saved':<14}: {info.get('last_modified', 'unknown')}")
    print()


# ─── Input Helpers ────────────────────────────────────────

def prompt_valid(prompt: str, valid_options: set,
                 label: str = "option") -> str:
    """
    Prompt the user until they enter a value from valid_options.

    Strips and lowercases input before comparison.

    Args:
        prompt        (str): The input prompt shown to the user.
        valid_options (set): Set of accepted lowercase values.
        label         (str): Human-readable field name for error messages.

    Returns:
        str: Validated, lowercased user input.
    """
    while True:
        value = input(prompt).strip().lower()
        if value in valid_options:
            return value
        print(f"  ✗ Invalid {label}. "
              f"Choose from: {', '.join(sorted(valid_options))}")


def prompt_task_number(tasks: list, action: str = "select") -> int | None:
    """
    Prompt the user for a task number and return the 0-based index.

    Validates that the number is a digit and within the valid range.

    Args:
        tasks  (list): Current task list (used for range validation).
        action (str) : Verb used in the prompt, e.g. 'remove', 'mark done'.

    Returns:
        int | None: 0-based index if valid, None if input was invalid.
    """
    raw = input(f"  Task number to {action}: ").strip()

    if not raw.isdigit():
        print("  ✗ Please enter a number.\n")
        return None

    index = int(raw) - 1   # convert 1-based display to 0-based index

    if not (0 <= index < len(tasks)):
        print(f"  ✗ Number out of range. "
              f"Choose between 1 and {len(tasks)}.\n")
        return None

    return index