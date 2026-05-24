# ALL terminal output lives here. Day 11/22.
# RULE: Only this module calls print(). All other modules raise or return.
from __future__ import annotations

from taskflow.env_config import get_settings
from ..config import APP_NAME, VERSION, PLAN_LIMITS
from ..core.task import Task
from ..utils import truncate

settings = get_settings()

__all__ = ["display_header","display_tasks","display_task_detail",
           "display_stats_dashboard","display_help","display_storage_info",
           "prompt_valid","prompt_task_number","COMMANDS"]

COMMANDS: dict[str, str] = {
    "add":      "Add a new task (shorthand syntax supported)",
    "view":     "View all tasks",
    "done":     "Mark a task as done",
    "remove":   "Remove a task permanently",
    "rename":   "Rename a task",
    "filter":   "Filter by priority / category / status",
    "search":   "Search by keyword or re:pattern",
    "stats":    "Statistics dashboard",
    "detail":   "Full detail for one task",
    "weather":  "Show current weather",
    "forecast": "Show 3-day weather forecast",
    "backup":   "Create a timestamped backup",
    "storage":  "Show storage file information",
    "help":     "Show this command reference",
    "quit":     "Save and exit",
}


def display_header(weather: dict | None = None) -> None:
    max_tasks = PLAN_LIMITS.get(settings.user_plan, 10)
    print("=" * 46)
    print(f"   {APP_NAME} — Task Manager v{VERSION}")
    if weather:
        emoji    = weather.get("emoji", "🌡")
        temp     = weather.get("temperature", "?")
        cond     = weather.get("condition", "")
        location = weather.get("location", "")
        print(f"   📍 {location}  |  {emoji} {temp}°C  {cond}")
    print("=" * 46)
    print(f"   Hello, {settings.user_name}!  Plan: {settings.user_plan.title()} ({max_tasks} tasks max)")
    print()


def display_tasks(tasks: list) -> None:
    if not tasks:
        print("\n  No tasks to display. Type 'add' to create one.\n")
        return
    col = {"num": 4, "title": 26, "priority": 10, "category": 13}
    width = sum(col.values()) + 10
    div   = "  " + "─" * width
    print()
    print(div)
    print(f"  {'#':<{col['num']}}{'Title':<{col['title']}}{'Priority':<{col['priority']}}{'Category':<{col['category']}}Status")
    print(div)
    for i, task in enumerate(tasks, start=1):
        if isinstance(task, Task):
            title    = truncate(task.title, col["title"] - 1)
            priority = task.priority
            category = task.category
            done     = task.done
        else:
            title    = truncate(task.get("title",""), col["title"] - 1)
            priority = task.get("priority","medium")
            category = task.get("category","general")
            done     = task.get("done", False)
        status = "✓ done" if done else "pending"
        extra  = ""
        if isinstance(task, Task):
            from ..core.task_types import DeadlineTask, RecurringTask, UrgentTask
            if isinstance(task, DeadlineTask):   extra = f" {task.urgency_label}"
            elif isinstance(task, RecurringTask): extra = f" {task.recurrence_label}"
            elif isinstance(task, UrgentTask):    extra = " 🚨"
        print(f"  {i:<{col['num']}}{title:<{col['title']}}{priority.upper():<{col['priority']}}{category:<{col['category']}}{status}{extra}")
    print(div)
    total   = len(tasks)
    done_n  = sum(1 for t in tasks if (t.done if isinstance(t, Task) else t.get("done", False)))
    pending = total - done_n
    rate    = round(done_n / total * 100, 1) if total > 0 else 0.0
    print(f"  {total} task{'s' if total != 1 else ''} · {pending} pending · {done_n} done · {rate}% complete")
    print()


def display_task_detail(task, index: int) -> None:
    if isinstance(task, Task):
        done = task.done; status = "✓ done" if done else "○ pending"
        print(f"\n  ── Task Detail — #{index} {'─'*30}")
        print(f"  {'ID':<16}: {task.id}")
        print(f"  {'Title':<16}: {task.title}")
        print(f"  {'Priority':<16}: {task.priority.upper()}")
        print(f"  {'Category':<16}: {task.category}")
        print(f"  {'Status':<16}: {status}")
        print(f"  {'Created':<16}: {task.created_at}")
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
    else:
        done   = task.get("done", False)
        status = "✓ done" if done else "○ pending"
        print(f"\n  ── Task Detail — #{index} {'─'*30}")
        for k, v in task.items():
            print(f"  {k:<16}: {v}")
    print()


def display_stats_dashboard(tasks: list) -> None:
    def _done(t): return t.done if isinstance(t, Task) else t.get("done", False)
    def _attr(t, k, d=""): return getattr(t, k, d) if isinstance(t, Task) else t.get(k, d)
    total   = len(tasks)
    done    = sum(1 for t in tasks if _done(t))
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0
    print()
    print("  ── Task Statistics ──────────────────────────")
    print(f"  {'Total':<16}: {total}")
    print(f"  {'Done':<16}: {done}  ({rate}%)")
    print(f"  {'Pending':<16}: {pending}")
    if tasks:
        print()
        print("  By Priority:")
        for p in ["high","medium","low"]:
            count = sum(1 for t in tasks if _attr(t,"priority") == p)
            bar   = "█" * count + "░" * max(0, 8 - count)
            print(f"    {p.upper():<8} {count:>3}  {bar}")
        categories = sorted({_attr(t,"category","other") for t in tasks})
        if categories:
            print()
            print("  By Category:")
            for cat in categories:
                count    = sum(1 for t in tasks if _attr(t,"category") == cat)
                done_cat = sum(1 for t in tasks if _attr(t,"category") == cat and _done(t))
                print(f"    {cat:<16} {count:>2} tasks  ({done_cat} done)")
    print()


def display_help() -> None:
    print()
    print("  ── Commands ─────────────────────────────────")
    for cmd, desc in COMMANDS.items():
        print(f"    {cmd:<12} — {desc}")
    print()


def display_storage_info(info: dict) -> None:
    print()
    print("  ── Storage Info ─────────────────────────────")
    if not info.get("exists"):
        print("  No storage file found yet.")
        print("  It will be created the first time you add a task.")
    else:
        size_kb = round(info.get("size_bytes", 0) / 1024, 2)
        print(f"  {'File':<16}: {info.get('filepath','unknown')}")
        print(f"  {'Size':<16}: {info.get('size_bytes',0)} bytes ({size_kb} KB)")
        print(f"  {'Last saved':<16}: {info.get('last_modified','unknown')}")
    print()


def prompt_valid(prompt: str, valid_options: set, label: str = "option") -> str:
    while True:
        value = input(prompt).strip().lower()
        if value in valid_options:
            return value
        print(f"  ✗ Invalid {label}. Choose from: {', '.join(sorted(valid_options))}")


def prompt_task_number(tasks: list, action: str = "select") -> int | None:
    raw = input(f"  Task number to {action}: ").strip()
    if not raw.isdigit():
        print("  ✗ Please enter a number.\n")
        return None
    index = int(raw) - 1
    if not (0 <= index < len(tasks)):
        print(f"  ✗ Choose a number between 1 and {len(tasks)}.\n")
        return None
    return index
