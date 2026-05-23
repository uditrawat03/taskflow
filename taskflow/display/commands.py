import re as re_module
import datetime

from ..config import (
    PLAN_LIMITS,
    VALID_PRIORITIES,
    VALID_CATEGORIES,
    DATE_FMT,
)
from ..errors import ValidationError, StorageError
from ..core.task import Task
from ..core.task_types import RecurringTask
from ..parser import parse_task_input, create_task_from_parse
from ..integrations.weather import (
    fetch_forecast,
    display_forecast,
    fetch_weather,
    display_weather,
)
from ..core.stats import (
    calculate_stats,
    average_title_length,
    most_productive_category,
)
from ..storage.json_store import (
    save_tasks,
    backup_tasks,
    get_storage_info,
)
from ..decorators import validate_non_empty
from .renderer import (
    display_tasks,
    display_task_detail,
    display_stats_dashboard,
    display_storage_info,
    prompt_valid,
    prompt_task_number,
)

from ..env_config import get_settings

settings = get_settings()

from ..services import add_task_to_list, is_at_limit, get_task_limit
from ..utils import pluralise

import logging

logger = logging.getLogger(__name__)

# Internal helpers


def _max_tasks() -> int:
    return PLAN_LIMITS.get(settings.user_plan, PLAN_LIMITS["free"])


def _get_attr(task: Task, key: str, default="") -> bool:
    if isinstance(task, Task):
        return getattr(task, key, default)
    return task.get(key, default)


def _is_done(task: Task) -> bool:
    if isinstance(task, Task):
        return task.done
    return task.get("done", False)


def _index_by_id(tasks: list[Task], task_id: int) -> int | None:
    for i, t in enumerate(tasks):
        tid = t.id if isinstance(t, Task) else t.get("id")
        if tid == task_id:
            return i
    return None


def _is_overdue(task: Task) -> bool:
    if isinstance(task, Task):
        return task.is_overdue()
    created = task.get("created_at", "")
    if not created or _is_done(task):
        return False
    try:
        age = (
            datetime.datetime.now() - datetime.datetime.strptime(created, DATE_FMT)
        ).days
        return age >= 7
    except ValueError:
        return False


def _print_add_confirmation(task: Task, total: int, max_tasks: int) -> None:
    typename = type(task).__name__ if isinstance(task, Task) else "Task"
    title = _get_attr(task, "title")
    print(f'\n  ✓ {typename} added: "{title}"')
    print(f"  Total: {total} task{'s' if total != 1 else ''}")
    remaining = max_tasks - total
    if 0 < remaining <= 2:
        print(
            f"  ⚠  Only {remaining} task slot{'s' if remaining != 1 else ''} "
            f"remaining on your {settings.user_plan} plan."
        )
    elif remaining <= 0:
        print(f"  ⚠  Task limit reached ({max_tasks}). Upgrade to premium for more.")
    print()


# add task
def cmd_add(tasks: list[Task], raw_input: str = "") -> None:
    """Collect task input and delegate creation to the service layer."""

    if is_at_limit(tasks):
        limit = get_task_limit()
        print(
            f"\n  ✗ {pluralise(limit, 'task')} limit reached "
            f"on {settings.user_plan} plan. Upgrade to premium.\n"
        )
        return

    raw = _collect_raw_input(raw_input)
    if raw is None:
        return

    try:
        task = _parse_to_task(raw)
    except ValidationError as e:
        logger.warning("Task add failed validation: %s", e)
        print(f"\n  ✗ {e}\n")
        return

    try:
        add_task_to_list(tasks, task)
        logger.info(
            "Task added",
            extra={
                "task_id": task.id,
                "task_type": type(task).__name__,
                "priority": task.priority,
                "category": task.category,
            },
        )
    except ValidationError as e:
        logger.warning("Task add rejected (limit): %s", e)
        print(f"\n  ✗ {e}\n")
        return

    _print_add_success(task, len(tasks))


def _collect_raw_input(raw_input: str) -> str | None:
    """Prompt for input if not pre-supplied. Returns None on empty input."""
    if not raw_input:
        print()
        print(
            "  Shorthand: !!  ~daily/weekly/monthly  #priority  @category  !YYYY-MM-DD"
        )
        print()
        raw_input = input("  Input: ").strip()
    if not raw_input:
        print("  ✗ Input cannot be empty.\n")
        return None
    return raw_input


def _parse_to_task(raw: str) -> Task:
    """Parse raw input into a Task. Raises ValidationError on failure."""
    result = parse_task_input(raw)
    return create_task_from_parse(result)


def _print_add_success(task: Task, total: int) -> None:
    """Print the post-add confirmation message."""
    typename = type(task).__name__
    print(f'\n  ✓ {typename} added: "{task.title}"')
    print(f"  Total: {pluralise(total, 'task')}")
    limit = get_task_limit()
    remaining = limit - total
    if 0 < remaining <= 2:
        print(
            f"  ⚠  {pluralise(remaining, 'slot')} remaining on {settings.user_plan} plan."
        )
    print()


# view tasks
def cmd_view(
    tasks: list[Task],
    priority: str | None = None,
    category: str | None = None,
    show_done: bool = False,
    show_pending: bool = False,
    show_overdue: bool = False,
    limit: int | None = None,
) -> None:
    """
    Display tasks, with optional filtering.

    Args:
        tasks        (list)     : Full task list.
        priority     (str|None) : Keep only this priority.
        category     (str|None) : Keep only this category.
        show_done    (bool)     : Keep only completed tasks.
        show_pending (bool)     : Keep only pending tasks.
        show_overdue (bool)     : Keep only overdue tasks.
        limit        (int|None) : Show at most N tasks.
    """
    try:
        from ..filters import TaskFilter

        f = TaskFilter(tasks)
        if priority:
            f = f.by_priority(priority)
        if category:
            f = f.by_category(category)
        if show_done:
            f = f.done()
        if show_pending:
            f = f.pending()
        if show_overdue:
            f = f.overdue()
        if limit:
            f = f.limit(limit)
        filtered = f.get()
    except ImportError:
        filtered = list(tasks)
        if priority:
            filtered = [t for t in filtered if _get_attr(t, "priority") == priority]
        if category:
            filtered = [t for t in filtered if _get_attr(t, "category") == category]
        if show_done:
            filtered = [t for t in filtered if _is_done(t)]
        if show_pending:
            filtered = [t for t in filtered if not _is_done(t)]
        if limit:
            filtered = filtered[:limit]

    display_tasks(filtered)


# done task
@validate_non_empty
def cmd_done(tasks: list[Task], task_id: int | None = None) -> None:
    """
    Mark a task as done.

    RecurringTask: increments completion_count and resets to pending.
    All others: sets done=True and status='done'.

    Args:
        tasks   (list)     : Task list.
        task_id (int|None) : ID for one-shot CLI; None to prompt.
    """
    if task_id is not None:
        index = _index_by_id(tasks, task_id)
        if index is None:
            print(f"\n  ✗ No task found with ID {task_id}.\n")
            return
    else:
        pending = [t for t in tasks if not _is_done(t)]
        if not pending:
            print("\n  ✓ All tasks are already done! Great work.\n")
            return
        display_tasks(tasks)
        index = prompt_task_number(tasks, action="mark done")
        if index is None:
            return

    task = tasks[index]

    if _is_done(task):
        print("  ✗ This task is already marked as done.\n")
        return

    if isinstance(task, RecurringTask):
        task.mark_done()
        print(
            f'\n  ✓ "{task.title}" completed '
            f"(×{task.completion_count}) — reset to pending.\n"
        )
    elif isinstance(task, Task):
        task.mark_done()
        print(f'\n  ✓ "{task.title}" marked as done!\n')
    else:
        # dict-based fallback
        task["done"] = True
        task["status"] = "done"
        print(f'\n  ✓ "{task.get("title", "")}" marked as done!\n')


# remove task
@validate_non_empty
def cmd_remove(tasks: list[Task], task_id: int | None = None) -> None:
    """
    Remove a task permanently.

    Args:
        tasks   (list)     : Task list — modified in place.
        task_id (int|None) : ID for one-shot CLI; None to prompt.
    """
    if task_id is not None:
        index = _index_by_id(tasks, task_id)
        if index is None:
            print(f"\n  ✗ No task found with ID {task_id}.\n")
            return
    else:
        display_tasks(tasks)
        index = prompt_task_number(tasks, action="remove")
        if index is None:
            return

    removed = tasks.pop(index)
    title = _get_attr(removed, "title")
    remaining = len(tasks)
    print(
        f'\n  ✓ "{title}" removed. '
        f"({remaining} task{'s' if remaining != 1 else ''} remaining)\n"
    )


# filter tasks
def cmd_filter(tasks: list[Task]) -> None:
    """Interactively filter tasks by priority, category, or status."""
    if not tasks:
        print("\n  ✗ No tasks to filter.\n")
        return

    print()
    print("  Filter by:")
    print("    1. Priority  (high / medium / low)")
    print("    2. Category  (work / personal / health / learning / other)")
    print("    3. Status    (pending / done / overdue)")
    print()
    choice = input("  Enter 1, 2, or 3: ").strip()

    if choice == "1":
        priority = prompt_valid("  Priority: ", VALID_PRIORITIES, "priority")
        filtered = [t for t in tasks if _get_attr(t, "priority") == priority]
        label = f"{priority.upper()} priority"

    elif choice == "2":
        category = prompt_valid("  Category: ", VALID_CATEGORIES, "category")
        filtered = [t for t in tasks if _get_attr(t, "category") == category]
        label = f"Category: {category}"

    elif choice == "3":
        status = input("  Status (pending/done/overdue): ").strip().lower()
        if status == "pending":
            filtered = [t for t in tasks if not _is_done(t)]
            label = "Pending tasks"
        elif status == "done":
            filtered = [t for t in tasks if _is_done(t)]
            label = "Completed tasks"
        elif status == "overdue":
            filtered = [t for t in tasks if not _is_done(t) and _is_overdue(t)]
            label = "Overdue tasks"
        else:
            print("  ✗ Invalid status. Use: pending / done / overdue\n")
            return
    else:
        print("  ✗ Invalid choice. Enter 1, 2, or 3.\n")
        return

    if filtered:
        print(f"\n  {label} ({len(filtered)} task{'s' if len(filtered) != 1 else ''}):")
        display_tasks(filtered)
    else:
        print(f"\n  No tasks found for filter: {label}\n")


# search tasks
def cmd_search(tasks: list[Task], keyword: str = "") -> None:
    """
    Search tasks by keyword or regex pattern.

    Prefix with 're:' for regex mode.

    Args:
        tasks   (list): Task list.
        keyword (str) : Pre-supplied keyword (one-shot CLI); empty = prompt.
    """
    if not tasks:
        print("\n  ✗ No tasks to search.\n")
        return

    if not keyword:
        print()
        keyword = input("  Keyword (or re:pattern): ").strip()

    if not keyword:
        print("  ✗ Please enter a search term.\n")
        return

    use_regex = keyword.startswith("re:")
    matches = []

    if use_regex:
        pat_str = keyword[3:]
        try:
            pattern = re_module.compile(pat_str, re_module.IGNORECASE)
            matches = [t for t in tasks if pattern.search(_get_attr(t, "title", ""))]
        except re_module.error as e:
            print(f"  ✗ Invalid regex '{pat_str}': {e}\n")
            return
    else:
        kw = keyword.lower()
        matches = [t for t in tasks if kw in _get_attr(t, "title", "").lower()]

    if matches:
        print(
            f"\n  {len(matches)} result{'s' if len(matches) != 1 else ''} "
            f"for '{keyword}':"
        )
        display_tasks(matches)
    else:
        print(f"\n  No tasks matching '{keyword}'.\n")


# stats tasks
def cmd_stats(tasks: list[Task]) -> None:
    """Display the full statistics dashboard."""
    display_stats_dashboard(tasks)

    if tasks:
        avg = average_title_length(tasks)
        top = most_productive_category(tasks)
        if avg:
            print(f"  Avg title length : {avg} chars")
        if top:
            print(f"  Most productive  : {top} category")
        print()


# detail ─


def cmd_detail(tasks: list[Task]) -> None:
    """Show full detail for a single selected task."""
    if not tasks:
        print("\n  ✗ No tasks to inspect.\n")
        return

    display_tasks(tasks)
    index = prompt_task_number(tasks, action="inspect")
    if index is None:
        return

    display_task_detail(tasks[index], index + 1)


# rename tasks
def cmd_rename(tasks: list[Task]) -> None:
    """Rename a task with validation."""
    if not tasks:
        print("\n  ✗ No tasks to rename.\n")
        return

    display_tasks(tasks)
    index = prompt_task_number(tasks, action="rename")
    if index is None:
        return

    task = tasks[index]
    old_title = _get_attr(task, "title")
    print(f'\n  Current title: "{old_title}"')
    new_title = input("  New title    : ").strip()

    if not new_title:
        print("  ✗ Title cannot be empty.\n")
        return
    if len(new_title) > 200:
        print("  ✗ Title too long (max 200 characters).\n")
        return

    if isinstance(task, Task):
        try:
            task.rename(new_title)
        except ValidationError as e:
            print(f"\n  ✗ {e}\n")
            return
    else:
        task["title"] = new_title

    print(f'\n  ✓ Renamed to "{new_title}"\n')


# weather
def cmd_weather() -> dict | None:
    """Fetch and display current weather. Returns weather dict for caching."""
    try:
        weather = fetch_weather(
            settings.user_latitude, settings.user_longitude, settings.user_location
        )
        display_weather(weather)
        return weather
    except Exception as e:
        print(f"\n  ✗ Weather unavailable: {e}\n")
        return None


# forecast
def cmd_forecast() -> None:
    """Fetch and display a 3-day weather forecast."""
    try:
        forecast = fetch_forecast(
            settings.user_latitude, settings.user_longitude, settings.user_location
        )
        display_forecast(forecast, settings.user_location)
    except Exception as e:
        print(f"\n  ✗ Forecast unavailable: {e}\n")


# backup
def cmd_backup() -> None:
    """Create a timestamped backup of the task storage file."""
    backup_tasks()


# storage
def cmd_storage() -> None:
    """Display metadata about the storage file."""
    info = get_storage_info()
    display_storage_info(info)


# quit


def cmd_quit(tasks: list[Task], save: bool = True) -> None:
    """
    Save tasks and print a goodbye message.

    Args:
        tasks (list): Task list to save.
        save  (bool): If True, save before quitting.
    """
    if save:
        try:
            save_tasks(tasks)
            count = len(tasks)
            print(f"\n  ✓ {count} task{'s' if count != 1 else ''} saved.")
        except StorageError as e:
            print(f"\n  ✗ Could not save tasks: {e}")
            print("  ⚠  Your changes may not have been persisted.")

    stats = calculate_stats(tasks) if tasks else {"done": 0, "total": 0, "rate": 0.0}
    print()
    if stats["total"] == 0:
        print(f"  Goodbye, {settings.user_name}! No tasks — clean slate. 👋")
    else:
        print(
            f"  Goodbye, {settings.user_name}! "
            f"{stats['done']}/{stats['total']} tasks complete "
            f"({stats['rate']}%). Keep going! 👋"
        )
    print()
