from .config import PLAN_LIMITS, OVERDUE_THRESHOLD_DAYS
from .errors import ValidationError, TaskNotFoundError
from .core.task       import Task
from .core.task_types import RecurringTask
from .core.stats      import calculate_stats

from .env_config import get_settings

settings = get_settings()

__all__ = [
    "add_task_to_list",
    "remove_task_by_index",
    "remove_task_by_id",
    "mark_task_done",
    "rename_task",
    "find_task_by_id",
    "find_task_index_by_id",
    "get_task_limit",
    "is_at_limit",
    "filter_tasks",
    "search_tasks",
    "get_overdue_tasks",
    "get_summary_stats",
]


# ─ Limit checks ─

def get_task_limit(plan: str | None = None) -> int:
    """
    Return the task limit for the given plan.

    Args:
        plan (str | None): Plan name. Defaults to USER_PLAN from config.

    Returns:
        int: Maximum number of tasks allowed.
    """
    p = plan or settings.user_plan
    return PLAN_LIMITS.get(p, PLAN_LIMITS["free"])


def is_at_limit(tasks: list, plan: str | None = None) -> bool:
    """Return True if the task list has reached its plan limit."""
    return len(tasks) >= get_task_limit(plan)


# ─ Add 

def add_task_to_list(
    tasks: list,
    task: Task,
    plan: str | None = None,
) -> Task:
    """
    Append a Task to the task list after checking the plan limit.

    Args:
        tasks (list)     : Current task list — modified in place.
        task  (Task)     : The Task to add.
        plan  (str|None) : Plan name for limit check.

    Returns:
        Task: The added task (same object that was passed in).

    Raises:
        ValidationError: If the task list is already at its limit.
    """
    limit = get_task_limit(plan)
    if len(tasks) >= limit:
        raise ValidationError(
            f"Task limit reached ({limit} tasks on "
            f"{plan or settings.user_plan} plan). Upgrade to premium.",
            field="tasks",
            value=len(tasks),
        )
    tasks.append(task)
    return task


# ─ Remove ─

def remove_task_by_index(tasks: list, index: int) -> Task:
    """
    Remove a task at the given 0-based index.

    Args:
        tasks (list): Current task list — modified in place.
        index (int) : 0-based index.

    Returns:
        Task: The removed task.

    Raises:
        IndexError: If index is out of range.
    """
    if not (0 <= index < len(tasks)):
        raise IndexError(
            f"Index {index} is out of range for a list of "
            f"{len(tasks)} task{'s' if len(tasks) != 1 else ''}."
        )
    return tasks.pop(index)


def remove_task_by_id(tasks: list, task_id: int) -> Task:
    """
    Remove a task by its ID.

    Args:
        tasks   (list): Current task list — modified in place.
        task_id (int) : Task ID to remove.

    Returns:
        Task: The removed task.

    Raises:
        TaskNotFoundError: If no task with that ID exists.
    """
    index = find_task_index_by_id(tasks, task_id)
    return tasks.pop(index)


# ─ Done ─

def mark_task_done(tasks: list, index: int) -> Task:
    """
    Mark a task as done, handling RecurringTask reset behaviour.

    Args:
        tasks (list): Task list.
        index (int) : 0-based index of the task to mark done.

    Returns:
        Task: The updated task.

    Raises:
        IndexError:      If index is out of range.
        ValidationError: If the task is already done (non-recurring).
    """
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range.")

    task = tasks[index]

    if isinstance(task, Task) and task.done and not isinstance(task, RecurringTask):
        raise ValidationError(
            f"Task '{task.title}' is already marked as done.",
            field="done",
            value=True,
        )

    task.mark_done()
    return task


# ─ Rename ─

def rename_task(tasks: list, index: int, new_title: str) -> Task:
    """
    Rename a task with full validation.

    Args:
        tasks     (list): Task list.
        index     (int) : 0-based index.
        new_title (str) : Replacement title.

    Returns:
        Task: The updated task.

    Raises:
        IndexError:      If index is out of range.
        ValidationError: If new_title is empty or too long.
    """
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range.")
    new_title = new_title.strip()
    if not new_title:
        raise ValidationError(
            "New title cannot be empty.", field="title", value=new_title
        )
    if len(new_title) > 200:
        raise ValidationError(
            "New title too long (max 200 characters).",
            field="title", value=len(new_title),
        )
    task = tasks[index]
    if isinstance(task, Task):
        task.rename(new_title)
    else:
        task["title"] = new_title
    return task


# ─ Lookup ─

def find_task_by_id(tasks: list, task_id: int) -> Task:
    """
    Find a task by its ID.

    Args:
        tasks   (list): Task list to search.
        task_id (int) : Task ID to find.

    Returns:
        Task: The matching task.

    Raises:
        TaskNotFoundError: If no task with that ID exists.
    """
    for task in tasks:
        tid = task.id if isinstance(task, Task) else task.get("id")
        if tid == task_id:
            return task
    raise TaskNotFoundError(task_id)


def find_task_index_by_id(tasks: list, task_id: int) -> int:
    """
    Find the 0-based index of a task by ID.

    Raises:
        TaskNotFoundError: If no task with that ID exists.
    """
    for i, task in enumerate(tasks):
        tid = task.id if isinstance(task, Task) else task.get("id")
        if tid == task_id:
            return i
    raise TaskNotFoundError(task_id)


# ─ Filtering 

def filter_tasks(
    tasks: list,
    priority: str | None = None,
    category: str | None = None,
    is_done: bool | None = None,
    overdue_only: bool = False,
    limit: int | None = None,
) -> list:
    """
    Apply one or more filters to a task list and return a new list.

    All arguments are optional — omitting one means "no filter on that field."

    Args:
        tasks       (list)     : Task list to filter.
        priority    (str|None) : Keep only tasks with this priority.
        category    (str|None) : Keep only tasks with this category.
        is_done     (bool|None): True → done only, False → pending only.
        overdue_only(bool)     : Keep only overdue tasks.
        limit       (int|None) : Return at most N tasks.

    Returns:
        list: Filtered task list (new list, original unmodified).
    """
    result = list(tasks)

    if priority is not None:
        p = priority.lower()
        result = [t for t in result if _attr(t, "priority") == p]

    if category is not None:
        c = category.lower()
        result = [t for t in result if _attr(t, "category") == c]

    if is_done is True:
        result = [t for t in result if _is_done(t)]
    elif is_done is False:
        result = [t for t in result if not _is_done(t)]

    if overdue_only:
        result = [t for t in result if _is_overdue(t)]

    if limit is not None:
        result = result[:limit]

    return result


def search_tasks(tasks: list, keyword: str) -> list:
    """
    Return tasks whose titles contain keyword (case-insensitive).

    Args:
        tasks   (list): Task list to search.
        keyword (str) : Search keyword.

    Returns:
        list: Matching tasks.
    """
    kw = keyword.strip().lower()
    return [t for t in tasks if kw in _attr(t, "title", "").lower()]


def get_overdue_tasks(tasks: list) -> list:
    """Return tasks that are overdue according to their type's definition."""
    return [t for t in tasks if _is_overdue(t)]


# ─ Stats 

def get_summary_stats(tasks: list) -> dict:
    """
    Return a summary statistics dict for the task list.

    Wraps calculate_stats() for import convenience.

    Returns:
        dict: total, done, pending, rate.
    """
    return calculate_stats(tasks)


# ─ Private helpers 

def _attr(task, key: str, default=""):
    if isinstance(task, Task):
        return getattr(task, key, default)
    return task.get(key, default)


def _is_done(task) -> bool:
    if isinstance(task, Task):
        return task.done
    return task.get("done", False)


def _is_overdue(task) -> bool:
    if isinstance(task, Task):
        return task.is_overdue()
    import datetime
    from .config import DATE_FMT
    created = task.get("created_at", "")
    if not created or _is_done(task):
        return False
    try:
        age = (datetime.datetime.now()
               - datetime.datetime.strptime(created, DATE_FMT)).days
        return age >= OVERDUE_THRESHOLD_DAYS
    except ValueError:
        return False