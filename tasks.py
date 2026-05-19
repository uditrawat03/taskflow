import datetime
from storage import (
    backup_tasks,
    load_tasks_safe,
    save_tasks,
    get_next_id,
    get_storage_info,
    DATA_FILE,
)
from errors import StorageError, ValidationError, TaskFlowError
from weather import fetch_weather, display_weather, get_weather_summary


# ─── Constants ───────────────────────────────────────────
APP_NAME = "TaskFlow AI"
VERSION = "0.3"
USER_NAME = "Udit"
USER_PLAN = "free"
MAX_TASKS = 10
VALID_PRIORITIES = {"high", "medium", "low"}
VALID_CATEGORIES = {"work", "personal", "health", "learning", "other"}
USER_LATITUDE = 28.6139
USER_LONGITUDE = 77.2090
USER_LOCATION = "Delhi, IN"


# ─── Pure Helper Functions ────────────────────────────────


def make_task(task_id: int, title: str, priority: str, category: str) -> dict:
    """
    Create and return a new task dictionary.

    Args:
        task_id  (int): Unique identifier for the task.
        title    (str): Task title.
        priority (str): One of 'high', 'medium', 'low'.
        category (str): One of the valid categories.

    Returns:
        dict: A fully populated task dictionary.
    """
    return {
        "id": task_id,
        "title": title,
        "priority": priority,
        "category": category,
        "status": "pending",
        "done": False,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def calculate_stats(tasks: list) -> dict:
    """
    Calculate summary statistics for a list of tasks.

    Args:
        tasks (list): List of task dictionaries.

    Returns:
        dict: Stats including total, done, pending, and completion_rate.
    """
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    pending = total - done
    rate = round(done / total * 100, 1) if total > 0 else 0.0
    return {"total": total, "done": done, "pending": pending, "rate": rate}


def get_tasks_by_priority(tasks: list, priority: str) -> list:
    """Return a filtered list of tasks matching the given priority."""
    return [t for t in tasks if t["priority"] == priority]


def get_pending_tasks(tasks: list) -> list:
    """Return only tasks that are not yet done."""
    return [t for t in tasks if not t["done"]]


def is_at_limit(tasks: list, limit: int) -> bool:
    """Return True if the task list has reached its limit."""
    return len(tasks) >= limit


def format_status(task: dict) -> str:
    """Return a formatted status string for display."""
    return "✓ done" if task["done"] else "pending"


# ─── Display Functions (side effects) ────────────────────


def display_header(weather: dict | None = None) -> None:
    """Print the application header with optional weather summary."""
    print("=" * 44)
    print(f"   {APP_NAME} — Task Manager v{VERSION}")
    if weather:
        summary = get_weather_summary(weather)
        print(f"   📍 {USER_LOCATION}  |  🌡 {summary}")
    print("=" * 44)
    print(f"   Hello, {USER_NAME}! Plan: {USER_PLAN.title()} ({MAX_TASKS} tasks max)")
    print()


def display_tasks(tasks: list) -> None:
    """
    Display all tasks in a formatted table.

    Args:
        tasks (list): List of task dictionaries to display.
    """
    if not tasks:
        print("\n  No tasks yet. Type 'add' to create your first task.\n")
        return

    col = {"num": 4, "title": 26, "priority": 10, "category": 12, "status": 10}
    width = sum(col.values()) + 4

    print()
    print("  " + "-" * width)
    print(
        f"  {'#':<{col['num']}}"
        f"{'Title':<{col['title']}}"
        f"{'Priority':<{col['priority']}}"
        f"{'Category':<{col['category']}}"
        f"Status"
    )
    print("  " + "-" * width)

    for i, task in enumerate(tasks, start=1):
        title = (
            (task["title"][: col["title"] - 2] + "..")
            if len(task["title"]) >= col["title"]
            else task["title"]
        )
        print(
            f"  {i:<{col['num']}}"
            f"{title:<{col['title']}}"
            f"{task['priority'].upper():<{col['priority']}}"
            f"{task['category']:<{col['category']}}"
            f"{format_status(task)}"
        )

    print("  " + "-" * width)
    stats = calculate_stats(tasks)
    print(
        f"  {stats['total']} tasks · {stats['pending']} pending · "
        f"{stats['done']} done · {stats['rate']}% complete\n"
    )


def display_stats(tasks: list) -> None:
    """Display a detailed statistics dashboard."""
    stats = calculate_stats(tasks)

    print("\n  ── Task Statistics ──────────────────")
    print(f"  Total      : {stats['total']}")
    print(f"  Done       : {stats['done']}  ({stats['rate']}%)")
    print(f"  Pending    : {stats['pending']}")

    if tasks:
        print("\n  By Priority:")
        for p in ["high", "medium", "low"]:
            count = len(get_tasks_by_priority(tasks, p))
            bar = "█" * count
            print(f"    {p.upper():<8}: {count:>2}  {bar}")

        print("\n  By Category:")
        categories = {t["category"] for t in tasks}
        for cat in sorted(categories):
            count = sum(1 for t in tasks if t["category"] == cat)
            print(f"    {cat:<12}: {count}")
    print()


# ─── Input Collection Functions ───────────────────────────


def prompt_valid(prompt: str, valid_options: set, label: str = "option") -> str:
    """
    Prompt the user until they enter a value from valid_options.

    Args:
        prompt        (str): The input prompt to display.
        valid_options (set): Set of accepted values.
        label         (str): Human-readable name used in error messages.

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
    Prompt the user for a task number and return a 0-based index.

    Args:
        tasks  (list): Current task list (used for range validation).
        action (str) : Verb to use in the prompt (e.g., 'remove', 'mark done').

    Returns:
        int | None: 0-based index if valid, None if invalid.
    """
    raw = input(f"  Task number to {action}: ").strip()
    if not raw.isdigit():
        print("  ✗ Please enter a number.\n")
        return None
    index = int(raw) - 1
    if not (0 <= index < len(tasks)):
        print(f"  ✗ Choose a number between 1 and {len(tasks)}.\n")
        return None
    return index


# ─── Command Functions ────────────────────────────────────


def cmd_add(tasks: list, next_id: list) -> None:
    """
    Prompt for task details and add a new task to the list.

    Args:
        tasks   (list): The current task list (mutated in place).
        next_id (list): Single-element list holding the next task ID.
                        Using a list avoids the 'global' keyword.
    """
    if is_at_limit(tasks, MAX_TASKS):
        print(
            f"\n  ✗ Task limit reached ({MAX_TASKS} tasks on {USER_PLAN} plan). "
            f"Upgrade to premium.\n"
        )
        return

    title = input("  Title    : ").strip()
    if not title:
        print("  ✗ Title cannot be empty.\n")
        return

    priority = prompt_valid("  Priority : ", VALID_PRIORITIES, "priority")
    category = prompt_valid("  Category : ", VALID_CATEGORIES, "category")

    task = make_task(next_id[0], title, priority, category)
    tasks.append(task)
    next_id[0] += 1

    count = len(tasks)
    print(f"\n  ✓ Task added! ({count} task{'s' if count != 1 else ''} total)\n")

    remaining = MAX_TASKS - count
    if remaining <= 2:
        print(
            f"  ⚠  Only {remaining} task slot{'s' if remaining != 1 else ''} remaining "
            f"on your {USER_PLAN} plan.\n"
        )


def cmd_done(tasks: list) -> None:
    """Mark a selected task as done."""
    pending = get_pending_tasks(tasks)
    if not pending:
        print("\n  ✓ All tasks are already done! Great work.\n")
        return

    display_tasks(tasks)
    index = prompt_task_number(tasks, action="mark done")
    if index is None:
        return

    if tasks[index]["done"]:
        print("  ✗ Task is already marked as done.\n")
    else:
        tasks[index]["done"] = True
        tasks[index]["status"] = "done"
        print(f'\n  ✓ "{tasks[index]["title"]}" marked as done!\n')


def cmd_remove(tasks: list) -> None:
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


def cmd_filter(tasks: list) -> None:
    """Display tasks filtered by priority."""
    priority = prompt_valid(
        "  Show priority (high/medium/low): ", VALID_PRIORITIES, "priority"
    )
    filtered = get_tasks_by_priority(tasks, priority)
    if not filtered:
        print(f"\n  No {priority}-priority tasks found.\n")
    else:
        print(f"\n  {priority.upper()} priority tasks ({len(filtered)}):")
        display_tasks(filtered)


def cmd_search(tasks: list) -> None:
    """Search tasks by keyword in title."""
    keyword = input("  Search keyword: ").strip().lower()
    if not keyword:
        print("  ✗ Please enter a search term.\n")
        return
    matches = [t for t in tasks if keyword in t["title"].lower()]
    if not matches:
        print(f"\n  No tasks matching '{keyword}'.\n")
    else:
        print(f"\n  Results for '{keyword}' ({len(matches)} found):")
        display_tasks(matches)


def cmd_quit(tasks: list) -> None:
    """Display a goodbye message and exit."""
    stats = calculate_stats(tasks)
    print(f"\n  Goodbye, {USER_NAME}!")
    if stats["total"] == 0:
        print("  No tasks — clean slate. See you tomorrow.")
    else:
        print(
            f"  {stats['done']}/{stats['total']} tasks completed "
            f"({stats['rate']}%). Keep going!"
        )
    print()


# ─── Command Registry ─────────────────────────────────────
# Maps command strings to functions — no giant if/elif chain needed.
# We will expand this pattern into a full CLI framework on Day 11.

COMMANDS = {
    "add": "Add a new task",
    "view": "View all tasks",
    "done": "Mark a task as done",
    "remove": "Remove a task",
    "filter": "Filter by priority",
    "search": "Search tasks by keyword",
    "stats": "View statistics dashboard",
    "quit": "Exit TaskFlow AI",
}


def display_help() -> None:
    """Display available commands."""
    print("\n  Available commands:")
    for cmd, description in COMMANDS.items():
        print(f"    {cmd:<10} — {description}")
    print()


def show_storage_info() -> None:
    """Display file storage metadata."""

    info = get_storage_info(DATA_FILE)
    print("\n  ── Storage Info ──────────────────────")
    if info["exists"]:
        print(f"  File      : {info['filepath']}")
        print(f"  Size      : {info['size_bytes']} bytes")
        print(f"  Modified  : {info['last_modified']}")
    else:
        print("  No storage file found yet.")
    print()


# ─── Main ─────────────────────────────────────────────────


def main() -> None:
    """Entry point with full exception handling."""

    # ── Load tasks ────────────────────────────────────────
    print("\n  Loading tasks...", end=" ", flush=True)
    tasks, load_error = load_tasks_safe()

    if load_error:
        print(f"\n  ✗ {load_error}")
        print("  ℹ  Creating a backup and starting with an empty task list.")
        try:
            backup_tasks()
        except Exception:
            pass  # backup failure is not critical — continue regardless
        tasks = []
    else:
        count = len(tasks)
        print(f"✓ {count} task{'s' if count != 1 else ''} loaded.")

    next_id = [get_next_id(tasks)]

    # ── Fetch weather ─────────────────────────────────────
    try:
        weather = fetch_weather(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
    except Exception:
        weather = None  # weather is non-critical — never crash for it

    display_header(weather)
    display_help()

    # ── Command loop ──────────────────────────────────────
    while True:
        try:
            command = input("> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C and Ctrl+D gracefully
            print("\n\n  Interrupted. Saving tasks before exit...")
            command = "quit"

        try:
            if command == "add":
                cmd_add(tasks, next_id)
            elif command == "view":
                display_tasks(tasks)
            elif command == "done":
                cmd_done(tasks)
            elif command == "remove":
                cmd_remove(tasks)
            elif command == "filter":
                cmd_filter(tasks)
            elif command == "search":
                cmd_search(tasks)
            elif command == "stats":
                display_stats(tasks)
            elif command == "weather":
                weather = fetch_weather(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
                display_weather(weather)
            elif command == "backup":
                backup_tasks()
            elif command == "help":
                display_help()
            elif command == "quit":
                try:
                    save_tasks(tasks)
                    print(f"  ✓ {len(tasks)} tasks saved.")
                except StorageError as e:
                    print(f"  ✗ Could not save tasks: {e}")
                    print("  ⚠  Your tasks may not have been saved.")
                cmd_quit(tasks)
                break
            elif command == "":
                continue
            else:
                print(f"\n  ✗ Unknown command '{command}'. Type 'help'.\n")

        except ValidationError as e:
            print(f"\n  ✗ Validation error: {e}\n")
        except TaskFlowError as e:
            print(f"\n  ✗ Error: {e}\n")
        except Exception as e:
            # Catch-all for truly unexpected errors — log and continue
            print(f"\n  ✗ Unexpected error: {type(e).__name__}: {e}")
            print("  ℹ  The app will continue. Please report this bug.\n")


if __name__ == "__main__":
    main()
