# --- Constants ---
APP_NAME = "TaskFlow AI"
VERSION = "0.1"
MAX_TASKS_FREE = 10
USER_NAME = "Udit"
USER_PLAN = "free"

# --- Setup ---
tasks = []  # our task list starts empty
max_tasks = MAX_TASKS_FREE

# --- Helper Functions (preview — we formalise these on Day 06) ---


def display_header():
    print("=" * 40)
    print(f"   {APP_NAME} — Task Manager v{VERSION}")
    print("=" * 40)
    print()


def display_tasks(task_list):
    if not task_list:
        print("  No tasks yet. Type 'add' to create one.")
        return
    print("\nYour Tasks:")
    print("-" * 20)
    for i, task in enumerate(task_list, start=1):
        print(f"  {i}. {task}")
    print()


def add_task(task_list, limit):
    if len(task_list) >= limit:
        print(f"  ✗ Task limit reached ({limit} tasks on {USER_PLAN} plan).")
        return
    task = input("Enter task: ").strip()
    if not task:
        print("  ✗ Task cannot be empty.")
        return
    task_list.append(task)
    print(
        f"  ✓ Task added! ({len(task_list)} task{'s' if len(task_list) != 1 else ''} total)"
    )


def remove_task(task_list):
    if not task_list:
        print("  ✗ No tasks to remove.")
        return
    display_tasks(task_list)
    raw = input("Enter task number to remove: ").strip()
    if not raw.isdigit():
        print("  ✗ Please enter a valid number.")
        return
    index = int(raw) - 1  # convert 1-based user input to 0-based index
    if 0 <= index < len(task_list):
        removed = task_list.pop(index)
        remaining = len(task_list)
        print(
            f'  ✓ "{removed}" removed. ({remaining} task{"s" if remaining != 1 else ""} remaining)'
        )
    else:
        print(f"  ✗ Invalid number. Choose between 1 and {len(task_list)}.")


# --- Main Command Loop ---
display_header()
print("Commands: add | view | remove | quit")
print()

while True:
    command = input("> ").strip().lower()

    if command == "add":
        add_task(tasks, max_tasks)

    elif command == "view":
        display_tasks(tasks)

    elif command == "remove":
        remove_task(tasks)

    elif command == "quit":
        count = len(tasks)
        if count == 0:
            print(f"Goodbye, {USER_NAME}. No tasks remaining — clean slate!")
        elif count == 1:
            print(f"Goodbye, {USER_NAME}. You have 1 task remaining. Don't forget!")
        else:
            print(
                f"Goodbye, {USER_NAME}. You have {count} tasks remaining. Stay productive!"
            )
        break

    elif command == "":
        continue  # user just pressed Enter — ignore and re-prompt

    else:
        print(f"  ✗ Unknown command '{command}'. Try: add | view | remove | quit")
