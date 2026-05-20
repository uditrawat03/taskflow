from ..parser import parse_and_create
from ..errors import ValidationError


def cmd_add(tasks: list) -> None:
    """Smart task add — supports full shorthand syntax."""

    print("\n  Shorthand: !! for urgent | ~daily/weekly/monthly for recurring")
    print("  Tokens: #high/#medium/#low  @category  !YYYY-MM-DD")
    print("  Example: Review PR #high @work !2025-06-01\n")

    raw = input("  Input: ").strip()
    if not raw:
        print("  ✗ Input cannot be empty.\n")
        return

    try:
        task = parse_and_create(raw)
        tasks.append(task)

        print(f"\n  ✓ {type(task).__name__} created:")
        print(f"    Title    : {task.title}")
        print(f"    Priority : {task.priority}")
        print(f"    Category : {task.category}")

        if hasattr(task, "due_date"):
            days = task.days_until_due
            print(f"    Due date : {task.due_date} ({task.urgency_label})")
        if hasattr(task, "recurrence"):
            print(f"    Recurs   : {task.recurrence}")

        print()

    except ValidationError as e:
        print(f"\n  ✗ {e}\n")
