
import datetime

# --- Constants ---
APP_NAME    = "TaskFlow AI"
VERSION     = "0.2"
USER_NAME   = "Udit"
USER_PLAN   = "free"
MAX_TASKS   = 10

VALID_PRIORITIES = {"high", "medium", "low"}
VALID_CATEGORIES = {"work", "personal", "health", "learning", "other"}

# --- State ---
tasks      = []          # list of task dicts
task_id    = 1           # auto-incrementing ID counter
categories = set()       # track unique categories in use

# --- Helper: Create a task dict ---
def make_task(title, priority, category):
    global task_id
    task = {
        "id":         task_id,
        "title":      title,
        "priority":   priority.lower(),
        "category":   category.lower(),
        "status":     "pending",
        "done":       False,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    task_id += 1
    return task

# --- Helper: Display tasks as a table ---
def display_tasks(task_list):
    if not task_list:
        print("\n  No tasks yet. Type 'add' to get started.\n")
        return

    col_title    = 24
    col_priority = 10
    col_category = 12
    col_status   = 10
    total_width  = 4 + col_title + col_priority + col_category + col_status + 6

    header = (
        f"  {'#':<4}"
        f"{'Title':<{col_title}}"
        f"{'Priority':<{col_priority}}"
        f"{'Category':<{col_category}}"
        f"{'Status':<{col_status}}"
    )

    print()
    print("-" * total_width)
    print(header)
    print("-" * total_width)

    for i, task in enumerate(task_list, start=1):
        status_display = "✓ done" if task["done"] else "pending"
        title_display  = task["title"][:col_title - 2] + ".." \
                         if len(task["title"]) > col_title - 1 \
                         else task["title"]
        print(
            f"  {i:<4}"
            f"{title_display:<{col_title}}"
            f"{task['priority'].upper():<{col_priority}}"
            f"{task['category']:<{col_category}}"
            f"{status_display:<{col_status}}"
        )

    print("-" * total_width)

    # Summary line
    done_count    = sum(1 for t in task_list if t["done"])
    pending_count = len(task_list) - done_count
    print(f"  {len(task_list)} total · {pending_count} pending · {done_count} done")

    # Active categories
    if categories:
        print(f"  Categories in use: {', '.join(sorted(categories))}")
    print()

# --- Command: Add task ---
def add_task():
    if len(tasks) >= MAX_TASKS:
        print(f"\n  ✗ Limit reached ({MAX_TASKS} tasks on {USER_PLAN} plan). "
              f"Upgrade to premium for more.\n")
        return

    title = input("  Title    : ").strip()
    if not title:
        print("  ✗ Title cannot be empty.\n")
        return

    # Validated priority input loop
    while True:
        priority = input("  Priority : ").strip().lower()
        if priority in VALID_PRIORITIES:
            break
        print(f"  ✗ Enter one of: {', '.join(sorted(VALID_PRIORITIES))}")

    # Validated category input loop
    while True:
        category = input("  Category : ").strip().lower()
        if category in VALID_CATEGORIES:
            break
        print(f"  ✗ Enter one of: {', '.join(sorted(VALID_CATEGORIES))}")

    task = make_task(title, priority, category)
    tasks.append(task)
    categories.add(category)

    count = len(tasks)
    print(f"\n  ✓ Task added! ({count} task{'s' if count != 1 else ''} total)\n")

    # Soft limit warnings
    if count == MAX_TASKS - 2:
        print(f"  ⚠ Warning: 2 tasks until your {USER_PLAN} plan limit.\n")
    elif count == MAX_TASKS:
        print("  ⚠ Task limit reached. Upgrade to premium for more.\n")

# --- Command: Mark task done ---
def mark_done():
    pending = [t for t in tasks if not t["done"]]
    if not pending:
        print("\n  ✓ All tasks are already done! Great work.\n")
        return

    display_tasks(tasks)
    raw = input("  Mark task number as done: ").strip()

    if not raw.isdigit():
        print("  ✗ Please enter a valid number.\n")
        return

    index = int(raw) - 1
    if 0 <= index < len(tasks):
        if tasks[index]["done"]:
            print("  ✗ Task already marked as done.\n")
        else:
            tasks[index]["done"]   = True
            tasks[index]["status"] = "done"
            print(f"\n  ✓ \"{tasks[index]['title']}\" marked as done!\n")
    else:
        print(f"  ✗ Invalid number. Choose between 1 and {len(tasks)}.\n")

# --- Command: Remove task ---
def remove_task():
    if not tasks:
        print("\n  ✗ No tasks to remove.\n")
        return

    display_tasks(tasks)
    raw = input("  Remove task number: ").strip()

    if not raw.isdigit():
        print("  ✗ Please enter a valid number.\n")
        return

    index = int(raw) - 1
    if 0 <= index < len(tasks):
        removed = tasks.pop(index)
        # Rebuild categories set from remaining tasks
        categories.clear()
        for t in tasks:
            categories.add(t["category"])
        remaining = len(tasks)
        print(f"\n  ✓ \"{removed['title']}\" removed. "
              f"({remaining} task{'s' if remaining != 1 else ''} remaining)\n")
    else:
        print(f"  ✗ Invalid number. Choose between 1 and {len(tasks)}.\n")

# --- Command: Filter by priority ---
def filter_by_priority():
    while True:
        priority = input("  Show priority (high/medium/low): ").strip().lower()
        if priority in VALID_PRIORITIES:
            break
        print("  ✗ Enter one of: high, medium, low")

    filtered = [t for t in tasks if t["priority"] == priority]
    if not filtered:
        print(f"\n  No {priority}-priority tasks found.\n")
    else:
        print(f"\n  {priority.upper()} priority tasks:")
        display_tasks(filtered)

# --- Main Command Loop ---
print("=" * 40)
print(f"   {APP_NAME} — Task Manager v{VERSION}")
print("=" * 40)
print(f"\n  Hello, {USER_NAME}! Plan: {USER_PLAN.title()} ({MAX_TASKS} tasks max)")
print("\n  Commands: add | view | done | remove | filter | quit\n")

while True:
    command = input("> ").strip().lower()

    if command == "add":
        add_task()
    elif command == "view":
        display_tasks(tasks)
    elif command == "done":
        mark_done()
    elif command == "remove":
        remove_task()
    elif command == "filter":
        filter_by_priority()
    elif command == "quit":
        count = len(tasks)
        done  = sum(1 for t in tasks if t["done"])
        print(f"\n  Goodbye, {USER_NAME}!")
        if count == 0:
            print("  No tasks — clean slate. See you tomorrow.")
        else:
            print(f"  {done}/{count} tasks completed. Keep going!")
        break
    elif command == "":
        continue
    else:
        print(f"\n  ✗ Unknown command '{command}'.")
        print("  Try: add | view | done | remove | filter | quit\n")