# Command implementations. Day 11/21/28.
# Thin command handlers: collect input → call services → show output.
from __future__ import annotations
import re as re_module, logging

from taskflow.env_config import get_settings
from ..config import PLAN_LIMITS, VALID_PRIORITIES, VALID_CATEGORIES
from ..errors import ValidationError, StorageError, TaskFlowError
from ..core.task        import Task
from ..core.task_types  import UrgentTask, RecurringTask, DeadlineTask
from ..core.stats       import calculate_stats, average_title_length, most_productive_category
from ..services         import (add_task_to_list, remove_task_by_index, remove_task_by_id,
                                 mark_task_done, rename_task, find_task_index_by_id,
                                 get_task_limit, is_at_limit, filter_tasks, search_tasks,
                                 get_summary_stats)
from ..storage.json_store import save_tasks, backup_tasks, get_storage_info
from ..decorators import validate_non_empty
from ..utils      import pluralise, truncate
from .renderer    import (display_tasks, display_task_detail, display_stats_dashboard,
                           display_help, display_storage_info, prompt_valid,
                           prompt_task_number, COMMANDS)

settings = get_settings()
logger = logging.getLogger(__name__)
__all__ = ["cmd_add","cmd_view","cmd_done","cmd_remove","cmd_filter","cmd_search",
           "cmd_stats","cmd_detail","cmd_rename","cmd_weather","cmd_forecast",
           "cmd_backup","cmd_storage","cmd_quit"]


def _cfg():
    from ..env_config import get_settings
    return get_settings()


#  add 
def cmd_add(tasks: list, raw_input: str = "") -> None:
    max_tasks = get_task_limit()
    if len(tasks) >= max_tasks:
        print(f"\n  ✗ {pluralise(max_tasks,'task')} limit reached on {settings.user_plan} plan.\n")
        return
    if not raw_input:
        print()
        print("  Shorthand: !!  ~daily/weekly/monthly  #priority  @category  !YYYY-MM-DD")
        print()
        raw_input = input("  Input: ").strip()
    if not raw_input:
        print("  ✗ Input cannot be empty.\n")
        return
    try:
        from ..parser import parse_task_input, create_task_from_parse
        result = parse_task_input(raw_input)
        task   = create_task_from_parse(result)
    except ImportError:
        task = _prompted_fallback(raw_input, tasks)
        if task is None: return
    except ValidationError as e:
        print(f"\n  ✗ {e}\n")
        return
    try:
        add_task_to_list(tasks, task)
        logger.info("Task added", extra={"task_id": task.id, "type": type(task).__name__,
                                          "priority": task.priority})
    except ValidationError as e:
        print(f"\n  ✗ {e}\n")
        return
    print(f"\n  ✓ {type(task).__name__} added: \"{task.title}\"")
    print(f"  Total: {pluralise(len(tasks),'task')}")
    remaining = max_tasks - len(tasks)
    if 0 < remaining <= 2:
        print(f"  ⚠  Only {pluralise(remaining,'slot')} remaining on {settings.user_plan} plan.")
    if isinstance(task, DeadlineTask):    print(f"  Due: {task.due_date} — {task.urgency_label}")
    elif isinstance(task, RecurringTask): print(f"  Recurs: {task.recurrence}")
    elif isinstance(task, UrgentTask):    print(f"  {task.escalation_note}")
    print()


def _prompted_fallback(title: str, tasks: list) -> Task | None:
    title = title.strip()
    if not title:
        print("  ✗ Title cannot be empty.\n")
        return None
    priority = prompt_valid("  Priority (high/medium/low): ", VALID_PRIORITIES, "priority")
    category = prompt_valid("  Category: ", VALID_CATEGORIES, "category")
    try:
        return Task(title=title, priority=priority, category=category)
    except ValidationError as e:
        print(f"\n  ✗ {e}\n")
        return None


#  view 
def cmd_view(tasks: list, priority: str | None = None, category: str | None = None,
             show_done: bool = False, show_pending: bool = False,
             show_overdue: bool = False, limit: int | None = None) -> None:
    try:
        from ..filters import TaskFilter
        f = TaskFilter(tasks)
        if priority:     f = f.by_priority(priority)
        if category:     f = f.by_category(category)
        if show_done:    f = f.done()
        if show_pending: f = f.pending()
        if show_overdue: f = f.overdue()
        if limit:        f = f.limit(limit)
        filtered = f.get()
    except ImportError:
        filtered = filter_tasks(tasks, priority=priority, category=category,
                                is_done=True if show_done else (False if show_pending else None),
                                overdue_only=show_overdue, limit=limit)
    display_tasks(filtered)


#  done 
@validate_non_empty
def cmd_done(tasks: list, task_id: int | None = None) -> None:
    def _find_index():
        if task_id is not None:
            try:
                return find_task_index_by_id(tasks, task_id)
            except Exception:
                print(f"\n  ✗ No task found with ID {task_id}.\n")
                return None
        pending = [t for t in tasks if not (t.done if isinstance(t,Task) else t.get("done",False))]
        if not pending:
            print("\n  ✓ All tasks are already done! Great work.\n")
            return None
        display_tasks(tasks)
        return prompt_task_number(tasks, action="mark done")

    index = _find_index()
    if index is None: return
    task = tasks[index]
    is_done = task.done if isinstance(task, Task) else task.get("done", False)
    if is_done:
        print("  ✗ This task is already marked as done.\n")
        return
    try:
        mark_task_done(tasks, index)
    except ValidationError as e:
        print(f"\n  ✗ {e}\n")
        return
    if isinstance(task, RecurringTask):
        print(f"\n  ✓ \"{task.title}\" completed (×{task.completion_count}) — reset to pending.\n")
    else:
        title = task.title if isinstance(task, Task) else task.get("title","")
        print(f"\n  ✓ \"{title}\" marked as done!\n")


#  remove 
@validate_non_empty
def cmd_remove(tasks: list, task_id: int | None = None) -> None:
    if task_id is not None:
        try:
            idx = find_task_index_by_id(tasks, task_id)
        except Exception:
            print(f"\n  ✗ No task found with ID {task_id}.\n")
            return
    else:
        display_tasks(tasks)
        idx = prompt_task_number(tasks, action="remove")
        if idx is None: return
    removed   = tasks.pop(idx)
    title     = removed.title if isinstance(removed, Task) else removed.get("title","")
    remaining = len(tasks)
    print(f"\n  ✓ \"{title}\" removed. ({pluralise(remaining,'task')} remaining)\n")


#  filter 
def cmd_filter(tasks: list) -> None:
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
        filtered = [t for t in tasks if (t.priority if isinstance(t,Task) else t.get("priority")) == priority]
        label    = f"{priority.upper()} priority"
    elif choice == "2":
        category = prompt_valid("  Category: ", VALID_CATEGORIES, "category")
        filtered = [t for t in tasks if (t.category if isinstance(t,Task) else t.get("category")) == category]
        label    = f"Category: {category}"
    elif choice == "3":
        status = input("  Status (pending/done/overdue): ").strip().lower()
        def _done(t): return t.done if isinstance(t,Task) else t.get("done",False)
        if status == "pending":
            filtered = [t for t in tasks if not _done(t)]; label = "Pending"
        elif status == "done":
            filtered = [t for t in tasks if _done(t)]; label = "Completed"
        elif status == "overdue":
            filtered = [t for t in tasks if not _done(t) and (t.is_overdue() if isinstance(t,Task) else False)]
            label = "Overdue"
        else:
            print("  ✗ Use: pending / done / overdue\n"); return
    else:
        print("  ✗ Enter 1, 2, or 3.\n"); return
    if filtered:
        print(f"\n  {label} ({pluralise(len(filtered),'task')}):")
        display_tasks(filtered)
    else:
        print(f"\n  No tasks found for filter: {label}\n")


#  search 
def cmd_search(tasks: list, keyword: str = "") -> None:
    if not tasks:
        print("\n  ✗ No tasks to search.\n"); return
    if not keyword:
        print()
        keyword = input("  Keyword (or re:pattern): ").strip()
    if not keyword:
        print("  ✗ Please enter a search term.\n"); return
    use_regex = keyword.startswith("re:")
    matches   = []
    if use_regex:
        pat_str = keyword[3:]
        try:
            pattern = re_module.compile(pat_str, re_module.IGNORECASE)
            matches = [t for t in tasks if pattern.search(t.title if isinstance(t,Task) else t.get("title",""))]
        except re_module.error as e:
            print(f"  ✗ Invalid regex '{pat_str}': {e}\n"); return
    else:
        kw      = keyword.lower()
        matches = [t for t in tasks if kw in (t.title if isinstance(t,Task) else t.get("title","")).lower()]
    if matches:
        print(f"\n  {pluralise(len(matches),'result')} for '{keyword}':")
        display_tasks(matches)
    else:
        print(f"\n  No tasks matching '{keyword}'.\n")


#  stats 
def cmd_stats(tasks: list) -> None:
    display_stats_dashboard(tasks)
    if tasks:
        avg = average_title_length(tasks)
        top = most_productive_category(tasks)
        if avg: print(f"  Avg title length : {avg} chars")
        if top: print(f"  Most productive  : {top} category")
        print()


#  detail 
def cmd_detail(tasks: list) -> None:
    if not tasks:
        print("\n  ✗ No tasks to inspect.\n"); return
    display_tasks(tasks)
    index = prompt_task_number(tasks, action="inspect")
    if index is None: return
    display_task_detail(tasks[index], index + 1)


#  rename 
def cmd_rename(tasks: list) -> None:
    if not tasks:
        print("\n  ✗ No tasks to rename.\n"); return
    display_tasks(tasks)
    index = prompt_task_number(tasks, action="rename")
    if index is None: return
    task      = tasks[index]
    old_title = task.title if isinstance(task, Task) else task.get("title","")
    print(f"\n  Current title: \"{old_title}\"")
    new_title = input("  New title    : ").strip()
    try:
        rename_task(tasks, index, new_title)
        print(f"\n  ✓ Renamed to \"{new_title}\"\n")
    except (ValidationError, IndexError) as e:
        print(f"\n  ✗ {e}\n")


#  weather 
def cmd_weather() -> dict | None:
    cfg = _cfg()
    try:
        from ..integrations.weather import fetch_weather, display_weather
        weather = fetch_weather(cfg.user_latitude, cfg.user_longitude, cfg.user_location)
        display_weather(weather)
        return weather
    except Exception as e:
        print(f"\n  ✗ Weather unavailable: {e}\n")
        return None


#  forecast 
def cmd_forecast() -> None:
    cfg = _cfg()
    try:
        from ..integrations.weather import fetch_forecast, display_forecast
        forecast = fetch_forecast(cfg.user_latitude, cfg.user_longitude, cfg.user_location)
        display_forecast(forecast, cfg.user_location)
    except Exception as e:
        print(f"\n  ✗ Forecast unavailable: {e}\n")


#  backup 
def cmd_backup() -> None:
    backup_tasks()


#  storage 
def cmd_storage() -> None:
    display_storage_info(get_storage_info())


#  quit 
def cmd_quit(tasks: list, save: bool = True) -> None:
    if save:
        try:
            save_tasks(tasks)
            print(f"\n  ✓ {pluralise(len(tasks),'task')} saved.")
        except StorageError as e:
            print(f"\n  ✗ Could not save tasks: {e}")
            print("  ⚠  Your changes may not have been persisted.")
    stats = calculate_stats(tasks) if tasks else {"done": 0, "total": 0, "rate": 0.0}
    print()
    if stats["total"] == 0:
        print(f"  Goodbye, {settings.user_name}! No tasks — clean slate. 👋")
    else:
        print(f"  Goodbye, {settings.user_name}! {stats['done']}/{stats['total']} tasks complete ({stats['rate']}%). 👋")
    print()