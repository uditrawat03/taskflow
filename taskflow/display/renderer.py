from ..config import APP_NAME, VERSION, USER_NAME, USER_PLAN, PLAN_LIMITS
from ..core.task import Task
from ..utils import truncate
from ..core.task_types import DeadlineTask, RecurringTask, UrgentTask

__all__ = [
    "display_header",
    "display_tasks",
    "display_task_detail",
    "display_stats_dashboard",
    "display_help",
    "display_storage_info",
    "prompt_valid",
    "prompt_task_number",
    "COMMANDS",
]

# ── Command registry ──────────────────────────────────────
# Maps command name → description.
# Update this dict when commands are added or removed.
# display_help() loops over it automatically.
COMMANDS: dict[str, str] = {
    "add": "Add a new task (shorthand syntax supported)",
    "view": "View all tasks",
    "done": "Mark a task as done",
    "remove": "Remove a task permanently",
    "rename": "Rename a task",
    "filter": "Filter by priority / category / status",
    "search": "Search by keyword or re:pattern",
    "stats": "Statistics dashboard",
    "detail": "Full detail for one task",
    "weather": "Show current weather",
    "forecast": "Show 3-day weather forecast",
    "backup": "Create a timestamped backup",
    "storage": "Show storage file information",
    "help": "Show this command reference",
    "quit": "Save and exit",
}


# ─── Header ───────────────────────────────────────────────


def display_header(weather: dict | None = None) -> None:
    """
    Print the application banner.

    Args:
        weather (dict | None): Weather data from fetch_weather().
                               If provided, shows a one-line summary.
    """
    max_tasks = PLAN_LIMITS.get(USER_PLAN, 10)

    print("=" * 46)
    print(f"   {APP_NAME} — Task Manager v{VERSION}")
    if weather:
        emoji = weather.get("emoji", "🌡")
        temp = weather.get("temperature", "?")
        cond = weather.get("condition", "")
        location = weather.get("location", "")
        print(f"   📍 {location}  |  {emoji} {temp}°C  {cond}")
    print("=" * 46)
    print(f"   Hello, {USER_NAME}!  Plan: {USER_PLAN.title()} ({max_tasks} tasks max)")
    print()


# ─── Task table ───────────────────────────────────────────


def display_tasks(tasks: list[Task]) -> None:
    """
    Display a list of Task objects as a formatted table.

    Args:
        tasks (list[Task]): Task objects to display.
                            Plain dicts are no longer accepted.
    """
    if not tasks:
        print("\n  No tasks to display. Type 'add' to create one.\n")
        return

    col = {"num": 4, "title": 26, "priority": 10, "category": 13}
    width = sum(col.values()) + 10
    div   = "  " + "─" * width

    print()
    print(div)
    print(
        f"  {'#':<{col['num']}}"
        f"{'Title':<{col['title']}}"
        f"{'Priority':<{col['priority']}}"
        f"{'Category':<{col['category']}}"
        f"Status"
    )
    print(div)

    for i, task in enumerate(tasks, start=1):
        title  = truncate(task.title, col["title"] - 1)
        status = "✓ done" if task.done else "pending"
        extra  = ""

        if isinstance(task, DeadlineTask):
            extra = f" {task.urgency_label}"
        elif isinstance(task, RecurringTask):
            extra = f" {task.recurrence_label}"
        elif isinstance(task, UrgentTask):
            extra = " 🚨"

        print(
            f"  {i:<{col['num']}}"
            f"{title:<{col['title']}}"
            f"{task.priority.upper():<{col['priority']}}"
            f"{task.category:<{col['category']}}"
            f"{status}{extra}"
        )

    print(div)

    total   = len(tasks)
    done    = sum(1 for t in tasks if t.done)
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0
    print(
        f"  {total} task{'s' if total != 1 else ''} · "
        f"{pending} pending · {done} done · {rate}% complete"
    )
    print()


# ─── Task detail ──────────────────────────────────────────


def display_task_detail(task, index: int) -> None:
    """
    Display every field of a single task.

    Args:
        task  (Task | dict): The task to display.
        index (int)        : 1-based display number.
    """
    done = _done(task)
    status = "✓ done" if done else "○ pending"

    print()
    print(f"  ── Task Detail — #{index} {'─' * 30}")
    print(f"  {'ID':<16}: {_attr(task, 'id', '?')}")
    print(f"  {'Title':<16}: {_attr(task, 'title', '')}")
    print(f"  {'Priority':<16}: {_attr(task, 'priority', '').upper()}")
    print(f"  {'Category':<16}: {_attr(task, 'category', '')}")
    print(f"  {'Status':<16}: {status}")
    print(f"  {'Created':<16}: {_attr(task, 'created_at', 'unknown')}")

    # Type-specific fields
    if isinstance(task, Task):
        from ..core.task_types import DeadlineTask, RecurringTask, UrgentTask

        if isinstance(task, DeadlineTask):
            print(f"  {'Due date':<16}: {task.due_date}")
            print(f"  {'Urgency':<16}: {task.urgency_label}")
        elif isinstance(task, RecurringTask):
            print(f"  {'Recurrence':<16}: {task.recurrence}")
            print(f"  {'Completions':<16}: {task.completion_count}×")
        elif isinstance(task, UrgentTask):
            print(f"  {'Escalation':<16}: {task.escalation_note}")
        print(f"  {'Age':<16}: {task.age_days()} days")
    elif isinstance(task, dict):
        task_type = task.get("type", "standard")
        if task_type == "deadline" and "due_date" in task:
            print(f"  {'Due date':<16}: {task['due_date']}")
        elif task_type == "recurring":
            print(f"  {'Recurrence':<16}: {task.get('recurrence', '')}")
            print(f"  {'Completions':<16}: {task.get('completion_count', 0)}×")
        elif task_type == "urgent":
            print(f"  {'Type':<16}: 🚨 Urgent")

    print()


# ─── Statistics dashboard ─────────────────────────────────


def display_stats_dashboard(tasks: list) -> None:
    """
    Display a statistics summary dashboard.

    Args:
        tasks (list): Task objects or dicts.
    """
    total = len(tasks)
    done = sum(1 for t in tasks if _done(t))
    pending = total - done
    rate = round(done / total * 100, 1) if total > 0 else 0.0

    print()
    print("  ── Task Statistics ──────────────────────────")
    print(f"  {'Total':<16}: {total}")
    print(f"  {'Done':<16}: {done}  ({rate}%)")
    print(f"  {'Pending':<16}: {pending}")

    if tasks:
        # Priority breakdown
        print()
        print("  By Priority:")
        for priority in ["high", "medium", "low"]:
            count = sum(1 for t in tasks if _attr(t, "priority") == priority)
            bar = "█" * count + "░" * max(0, 8 - count)
            print(f"    {priority.upper():<8} {count:>3}  {bar}")

        # Category breakdown
        categories = sorted({_attr(t, "category", "other") for t in tasks})
        if categories:
            print()
            print("  By Category:")
            for cat in categories:
                count = sum(1 for t in tasks if _attr(t, "category") == cat)
                done_cat = sum(
                    1 for t in tasks if _attr(t, "category") == cat and _done(t)
                )
                print(f"    {cat:<16} {count:>2} tasks  ({done_cat} done)")

        # Type breakdown (if multiple types present)
        types = {_attr(t, "type", "standard") for t in tasks}
        if len(types) > 1:
            print()
            print("  By Type:")
            for ttype in sorted(types):
                count = sum(1 for t in tasks if _attr(t, "type", "standard") == ttype)
                print(f"    {ttype:<16} {count:>2}")

    print()


# ─── Help ─────────────────────────────────────────────────


def display_help() -> None:
    """Print the command reference table from the COMMANDS registry."""
    print()
    print("  ── Commands ─────────────────────────────────")
    for cmd, desc in COMMANDS.items():
        print(f"    {cmd:<12} — {desc}")
    print()


# ─── Storage info ─────────────────────────────────────────


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
        size_kb = round(info.get("size_bytes", 0) / 1024, 2)
        print(f"  {'File':<16}: {info.get('filepath', 'unknown')}")
        print(f"  {'Size':<16}: {info.get('size_bytes', 0)} bytes ({size_kb} KB)")
        print(f"  {'Last saved':<16}: {info.get('last_modified', 'unknown')}")
    print()


# ─── Input helpers ────────────────────────────────────────


def prompt_valid(prompt: str, valid_options: set, label: str = "option") -> str:
    """
    Prompt the user until they enter a value from valid_options.

    Strips whitespace and lowercases the input before comparison.

    Args:
        prompt        (str): The prompt string shown to the user.
        valid_options (set): Accepted lowercase string values.
        label         (str): Human-readable field name for error messages.

    Returns:
        str: The validated, lowercased user input.
    """
    while True:
        value = input(prompt).strip().lower()
        if value in valid_options:
            return value
        print(f"  ✗ Invalid {label}. Choose from: {', '.join(sorted(valid_options))}")


def prompt_task_number(tasks: list, action: str = "select") -> int | None:
    """
    Prompt the user for a task number and return the 0-based index.

    Args:
        tasks  (list): Current task list (used for range validation).
        action (str) : Verb used in the prompt, e.g. 'remove'.

    Returns:
        int | None: 0-based list index if valid; None if invalid input.
    """
    raw = input(f"  Task number to {action}: ").strip()

    if not raw.isdigit():
        print("  ✗ Please enter a number.\n")
        return None

    index = int(raw) - 1  # convert 1-based display → 0-based index

    if not (0 <= index < len(tasks)):
        print(f"  ✗ Choose a number between 1 and {len(tasks)}.\n")
        return None

    return index


# ─── Private helpers ──────────────────────────────────────


def _attr(task, key: str, default=""):
    """Get an attribute from a Task object or a dict."""
    if isinstance(task, Task):
        return getattr(task, key, default)
    return task.get(key, default)


def _done(task) -> bool:
    """Return done status from a Task object or a dict."""
    if isinstance(task, Task):
        return task.done
    return task.get("done", False)
