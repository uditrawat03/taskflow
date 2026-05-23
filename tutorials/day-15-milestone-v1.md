# Day 15 — Project Milestone: TaskFlow AI CLI v1.0

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Shipping the first real release

---

## Learning Objective

By the end of today, TaskFlow AI v1.0 is shipped. You will add a proper CLI interface with `argparse`, write a professional `README.md`, run the complete code review checklist across every file, record the version in a `CHANGELOG.md`, and do a full end-to-end demo. This is the series' first "ship day" — the discipline of finishing matters as much as the code itself.

---

## What We Build Today

A proper `argparse` CLI, a `README.md`, a `CHANGELOG.md`, and a final hardened release of every module. By end of day, someone who has never seen the project can clone it, read the README, run it, and understand everything it does.

```
$ python run.py --help

usage: taskflow [-h] [--version] [--no-weather] [--data PATH]
                {add,view,done,remove,filter,search,stats,forecast,backup} ...

TaskFlow AI — Intelligent task management from the terminal.

options:
  -h, --help    show this help message and exit
  --version     show program version and exit
  --no-weather  disable weather fetching at startup
  --data PATH   use a custom data file path

commands:
  {add,view,done,remove,filter,search,stats,forecast,backup}
    add         Add a new task (supports shorthand syntax)
    view        Display all tasks
    done        Mark a task as done
    remove      Remove a task
    filter      Filter tasks by priority or category
    search      Search tasks by keyword or regex
    stats       Show task statistics dashboard
    forecast    Show 3-day weather forecast
    backup      Create a timestamped backup of task data

$ python run.py add "Review PR #high @work !2025-06-01"
✓ DeadlineTask created: Review PR [due 2025-06-01 🟢 13d]

$ python run.py view --priority high
[Showing 2 high-priority tasks]

$ python run.py stats
[Stats dashboard]

$ python run.py  # interactive mode (no subcommand)
[Launches full interactive shell]
```

---

## Concepts Covered

- `argparse` — building professional CLIs
- Subcommands with `add_subparsers()`
- Positional vs optional arguments
- `--flags` and default values
- Dual-mode CLI — interactive shell + one-shot commands
- `CHANGELOG.md` — documenting version history
- `README.md` — writing developer-facing documentation
- Final code review across the entire codebase
- Semantic versioning — `MAJOR.MINOR.PATCH`
- Entry points — `pyproject.toml` basics
- The ship mindset — finishing is a skill

---

## Full Tutorial

### `argparse` — Professional CLI Arguments

`argparse` is Python's standard library module for parsing command-line arguments. It automatically generates `--help` output, validates argument types, and handles errors:

```python
import argparse

parser = argparse.ArgumentParser(
    prog="taskflow",
    description="TaskFlow AI — Intelligent task management from the terminal.",
    epilog="Run without arguments to enter interactive mode.",
)

# Optional flags
parser.add_argument("--version",    action="version", version="TaskFlow AI 1.0.0")
parser.add_argument("--no-weather", action="store_true",
                    help="Disable weather fetching at startup")
parser.add_argument("--data",       metavar="PATH",
                    help="Use a custom data file path")

# Parse — returns a Namespace object
args = parser.parse_args()
print(args.no_weather)   # True/False
print(args.data)         # None or the path string
```

---

### Subcommands with `add_subparsers()`

Subcommands work like `git commit`, `git push` — the first word after the program name selects a sub-parser:

```python
parser = argparse.ArgumentParser(prog="taskflow")
subparsers = parser.add_subparsers(dest="command", metavar="command")

# 'add' subcommand
add_parser = subparsers.add_parser("add", help="Add a new task")
add_parser.add_argument("input", nargs="?", default="",
                        help="Task input (shorthand supported)")

# 'view' subcommand
view_parser = subparsers.add_parser("view", help="Display all tasks")
view_parser.add_argument("--priority", choices=["high", "medium", "low"],
                         help="Filter by priority")
view_parser.add_argument("--category", help="Filter by category")
view_parser.add_argument("--done",  action="store_true", help="Show only done tasks")
view_parser.add_argument("--pending", action="store_true", help="Show only pending tasks")

# 'done' subcommand
done_parser = subparsers.add_parser("done", help="Mark a task as done")
done_parser.add_argument("id", type=int, help="Task ID to mark done")

# 'remove' subcommand
remove_parser = subparsers.add_parser("remove", help="Remove a task")
remove_parser.add_argument("id", type=int, help="Task ID to remove")

# 'filter' subcommand
filter_parser = subparsers.add_parser("filter", help="Filter tasks")
filter_parser.add_argument("--priority", choices=["high", "medium", "low"])
filter_parser.add_argument("--category")
filter_parser.add_argument("--overdue", action="store_true")

# 'search' subcommand
search_parser = subparsers.add_parser("search", help="Search tasks")
search_parser.add_argument("keyword", help="Search keyword or re:pattern")

# 'stats' subcommand
subparsers.add_parser("stats",    help="Show statistics dashboard")
subparsers.add_parser("forecast", help="Show 3-day weather forecast")
subparsers.add_parser("backup",   help="Create a backup of task data")
```

---

### Building `taskflow/cli.py`

```python
# taskflow/cli.py
# TaskFlow AI — Day 15
# Argument parser and dual-mode CLI dispatcher.

import argparse
import sys
from pathlib import Path

from .config       import APP_NAME, VERSION, USER_LATITUDE, USER_LONGITUDE, USER_LOCATION
from .errors       import TaskFlowError, ValidationError, StorageError
from .storage.json_store import load_tasks, save_tasks, backup_tasks
from .core.task    import Task
from .core.stats   import calculate_stats, priority_breakdown, category_breakdown
from .parser       import parse_task_input, create_task_from_parse
from .integrations.weather import fetch_weather, display_weather, fetch_forecast, display_forecast
from .display.renderer     import display_tasks, display_stats_dashboard, display_header


def build_parser() -> argparse.ArgumentParser:
    """Build and return the full argument parser."""

    parser = argparse.ArgumentParser(
        prog="taskflow",
        description=f"{APP_NAME} — Intelligent task management from the terminal.",
        epilog="Run without arguments to launch the interactive shell.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{APP_NAME} {VERSION}",
    )
    parser.add_argument(
        "--no-weather",
        action="store_true",
        help="Skip weather fetch at startup (faster cold start)",
    )
    parser.add_argument(
        "--data",
        metavar="PATH",
        type=Path,
        help="Use a custom JSON data file",
    )

    subs = parser.add_subparsers(dest="command", metavar="command")

    # add
    p_add = subs.add_parser("add", help="Add a task (shorthand supported)")
    p_add.add_argument("input", nargs="?", default="",
                       help='Task input, e.g. "Review PR #high @work !2025-06-01"')

    # view
    p_view = subs.add_parser("view", help="View tasks")
    p_view.add_argument("--priority", choices=["high","medium","low"])
    p_view.add_argument("--category")
    p_view.add_argument("--done",    action="store_true")
    p_view.add_argument("--pending", action="store_true")
    p_view.add_argument("--overdue", action="store_true")

    # done
    p_done = subs.add_parser("done", help="Mark a task done by ID")
    p_done.add_argument("id", type=int, help="Task ID")

    # remove
    p_remove = subs.add_parser("remove", help="Remove a task by ID")
    p_remove.add_argument("id", type=int, help="Task ID")

    # search
    p_search = subs.add_parser("search", help="Search tasks")
    p_search.add_argument("keyword", help="Keyword or re:pattern")

    # stats
    subs.add_parser("stats",    help="Statistics dashboard")
    subs.add_parser("forecast", help="3-day weather forecast")
    subs.add_parser("backup",   help="Backup task data")

    return parser


def run_one_shot(args: argparse.Namespace, tasks: list[Task]) -> bool:
    """
    Execute a single non-interactive command and return True,
    or return False if no command was given (caller should launch shell).

    Args:
        args  (Namespace): Parsed arguments.
        tasks (list)     : Loaded task list.

    Returns:
        bool: True if a command was executed, False if interactive mode needed.
    """
    if not args.command:
        return False   # no subcommand — launch interactive shell

    if args.command == "add":
        raw = args.input or input("  Input: ").strip()
        try:
            result = parse_task_input(raw)
            task   = create_task_from_parse(result)
            tasks.append(task)
            save_tasks(tasks, args.data or None)
            print(f"\n  ✓ {type(task).__name__} created: {task.title}")
            _print_task_meta(task)
        except (ValidationError, StorageError) as e:
            print(f"\n  ✗ {e}")

    elif args.command == "view":
        filtered = tasks[:]
        if args.priority:
            filtered = [t for t in filtered if t.priority == args.priority]
        if args.category:
            filtered = [t for t in filtered if t.category == args.category]
        if args.done:
            filtered = [t for t in filtered if t.done]
        if args.pending:
            filtered = [t for t in filtered if not t.done]
        if args.overdue:
            filtered = [t for t in filtered if t.is_overdue()]
        display_tasks(filtered)

    elif args.command == "done":
        task = _find_by_id(tasks, args.id)
        if task:
            task.mark_done()
            save_tasks(tasks, args.data or None)
            print(f"\n  ✓ \"{task.title}\" marked as done.\n")

    elif args.command == "remove":
        task = _find_by_id(tasks, args.id)
        if task:
            tasks.remove(task)
            save_tasks(tasks, args.data or None)
            print(f"\n  ✓ \"{task.title}\" removed.\n")

    elif args.command == "search":
        kw = args.keyword
        import re
        use_regex = kw.startswith("re:")
        pattern   = kw[3:] if use_regex else None
        results   = []
        for t in tasks:
            if use_regex:
                try:
                    if re.search(pattern, t.title, re.IGNORECASE):
                        results.append(t)
                except re.error as e:
                    print(f"  ✗ Invalid regex: {e}")
                    return True
            else:
                if kw.lower() in t.title.lower():
                    results.append(t)
        if results:
            print(f"\n  Found {len(results)} task(s):")
            display_tasks(results)
        else:
            print(f"\n  No tasks matching '{kw}'.\n")

    elif args.command == "stats":
        display_stats_dashboard(tasks)

    elif args.command == "forecast":
        forecast = fetch_forecast(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
        display_forecast(forecast, USER_LOCATION)

    elif args.command == "backup":
        backup_tasks()

    return True


def _find_by_id(tasks: list[Task], task_id: int) -> Task | None:
    """Find a task by ID. Prints error and returns None if not found."""
    for task in tasks:
        if task.id == task_id:
            return task
    print(f"\n  ✗ No task found with ID {task_id}.\n")
    return None


def _print_task_meta(task: Task) -> None:
    """Print type-specific metadata after task creation."""
    print(f"    Priority : {task.priority}")
    print(f"    Category : {task.category}")
    if hasattr(task, "due_date"):
        print(f"    Due      : {task.due_date} ({task.urgency_label})")
    if hasattr(task, "recurrence"):
        print(f"    Recurs   : {task.recurrence}")
    print()
```

---

### The Dual-Mode Entry Point

```python
# taskflow/main.py — updated for Day 15
# Dual-mode: runs one-shot command OR interactive shell.

from .cli      import build_parser, run_one_shot
from .shell    import run_interactive_shell
from .storage.json_store import load_tasks, load_tasks_safe, backup_tasks
from .integrations.weather import fetch_weather
from .display.renderer     import display_header
from .config   import USER_LATITUDE, USER_LONGITUDE, USER_LOCATION
from .errors   import StorageError


def main() -> None:
    """
    TaskFlow AI entry point.

    One-shot mode:  python run.py add "Review PR #high @work"
    Interactive:    python run.py
    """
    parser = build_parser()
    args   = parser.parse_args()

    #  Load tasks 
    filepath = args.data if hasattr(args, "data") and args.data else None
    tasks, load_error = load_tasks_safe(filepath)

    if load_error:
        print(f"\n  ⚠  {load_error}")
        print("  Creating backup and starting fresh.\n")
        try:
            backup_tasks()
        except Exception:
            pass
        tasks = []

    #  One-shot mode ─
    if run_one_shot(args, tasks):
        return   # command executed — exit

    #  Interactive mode 
    weather = None
    if not (hasattr(args, "no_weather") and args.no_weather):
        weather = fetch_weather(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)

    display_header(weather)
    run_interactive_shell(tasks)
```

---

### Writing the README

Create `README.md` in the project root:

```markdown
# TaskFlow AI 🗒️

> Intelligent task management from the terminal — built in 15 days of learning Python.

[![Python](https://img.shields.io/badge/python-3.14-blue)]()
[![Version](https://img.shields.io/badge/version-1.0.0-green)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()

## What Is This?

TaskFlow AI is a command-line task manager built as a learning project across
the first 15 days of a 90-day Python & AI Engineering series. It demonstrates:

- Python 3.14 best practices
- Object-oriented design (Task class hierarchy)
- JSON persistence with atomic writes
- Real API integration (weather via Open-Meteo)
- Natural language task input parsing
- Professional package structure

## Quick Start

```bash
# Clone the project
git clone https://github.com/uditrawat03/taskflow
cd taskflow

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Run interactive mode
python run.py

# Run a single command
python run.py add "Review PR #high @work !2025-06-01"
python run.py view --priority high
python run.py stats
```

## Task Shorthand Syntax

| Syntax | Meaning | Example |
|--------|---------|---------|
| `!!` prefix | Urgent task | `!! Server down @work` |
| `~daily` prefix | Recurring task | `~daily Standup @work` |
| `#priority` | Set priority | `Review PR #high` |
| `@category` | Set category | `Buy milk @personal` |
| `!YYYY-MM-DD` | Set due date | `Submit report !2025-06-01` |

Tokens can be combined: `Review PR #high @work !2025-06-01`

## Commands

### Interactive Mode

| Command | Description |
|---------|-------------|
| `add` | Add a task (smart parser) |
| `view` | View all tasks |
| `done` | Mark a task done |
| `remove` | Remove a task |
| `filter` | Filter by priority/category |
| `search` | Search by keyword or regex |
| `stats` | Statistics dashboard |
| `forecast` | 3-day weather forecast |
| `backup` | Backup task data |
| `help` | Show command reference |
| `quit` | Exit (auto-saves) |

### One-Shot Mode

```bash
python run.py add "Task title #high @work"
python run.py view --priority high --pending
python run.py done 3
python run.py remove 5
python run.py search "review"
python run.py stats
python run.py forecast
python run.py backup
```

## Task Types

| Type | How to Create | Special Behaviour |
|------|--------------|-------------------|
| `Task` | Default | Standard task |
| `UrgentTask` | `!!` prefix | Priority always high, escalation note |
| `RecurringTask` | `~daily/weekly/monthly` prefix | Auto-resets after done |
| `DeadlineTask` | `!YYYY-MM-DD` token | Tracks urgency by due date |

## Project Structure

```
taskflow/               Python package
├ __init__.py         Public API
├ main.py             Entry point
├ cli.py              Argument parser
├ shell.py            Interactive shell
├ parser.py           Natural language task parser
├ config.py           Configuration constants
├ errors.py           Custom exception hierarchy
├ core/
│   ├ task.py         Task base class
│   ├ task_types.py   UrgentTask, RecurringTask, DeadlineTask
│   ├ task_factory.py Polymorphic deserialization
│   └ stats.py        Statistics calculations
├ storage/
│   └ json_store.py   JSON persistence with atomic writes
├ integrations/
│   └ weather.py      Open-Meteo weather API
└ display/
    └ renderer.py     Terminal UI rendering

run.py                  Root entry point
requirements.txt        Dependencies
README.md               This file
CHANGELOG.md            Version history
```

## Dependencies

```
requests>=2.31
```

Install: `pip install -r requirements.txt`

No paid APIs. No API keys required.

## Configuration

Edit `taskflow/config.py` to change:
- `USER_NAME` — your name
- `USER_LATITUDE` / `USER_LONGITUDE` / `USER_LOCATION` — your location
- `USER_PLAN` — `"free"` or `"premium"`
- `MAX_TASKS_FREE` / `MAX_TASKS_PREMIUM` — task limits

## What's Next

This project will evolve over 90 days into:
- Web API (FastAPI) — Day 41
- Database backend (PostgreSQL) — Day 55
- AI-powered task analysis (Claude/OpenAI) — Day 61
- Vector search (embeddings + Qdrant) — Day 66
- Autonomous AI agents — Day 71
- Production deployment (Docker + cloud) — Day 58

Follow the series: [youtube.com/@udit-taskflow]

## License

MIT License — see `LICENSE` for details.
```

---

### Writing `CHANGELOG.md`

```markdown
# Changelog

All notable changes to TaskFlow AI are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com).

## [1.0.0] — 2025-05-19

### Added
- Interactive terminal shell with full command loop
- `add`, `view`, `done`, `remove`, `filter`, `search`, `stats`, `backup`, `forecast` commands
- Smart task parser with shorthand syntax: `#priority`, `@category`, `!date`, `!!`, `~recurrence`
- Task type system: `Task`, `UrgentTask`, `RecurringTask`, `DeadlineTask`
- JSON persistence with atomic writes and automatic backup on corruption
- Live weather integration via Open-Meteo API (no API key required)
- 3-day weather forecast display
- Custom exception hierarchy: `TaskFlowError`, `StorageError`, `ValidationError`, `TaskNotFoundError`, `WeatherError`
- `argparse`-based dual-mode CLI (interactive + one-shot commands)
- Proper Python package structure with submodules
- Code review checklist — all items passing

### Architecture
- `taskflow/` package with `core/`, `storage/`, `integrations/`, `display/` submodules
- `Task` class with `__str__`, `__repr__`, `__eq__`, `__lt__`, `__hash__` dunder methods
- `@property` validation on `priority` and `category`
- `Task.from_dict()` / `Task.to_dict()` for clean JSON round-trips
- `TaskFactory` for polymorphic deserialization
- `ParseResult` dataclass from natural language parser

## [0.4.0] — Day 07
- Code review pass, debug_practice.py, hardened edge cases

## [0.3.0] — Day 06
- Full function refactor, docstrings, command registry, `if __name__ == "__main__"`

## [0.2.0] — Day 05
- Tasks upgraded from strings to dict objects, categories, priorities, sets

## [0.1.0] — Day 04
- Initial interactive task list with add/view/remove/quit commands
```

---

### Final Code Review Checklist — v1.0

Run this across every file before tagging the release:

```
TaskFlow AI v1.0 — Pre-Release Code Review
==========================================

Package Structure:
[✓] taskflow/ is a proper Python package
[✓] Each subpackage has __init__.py
[✓] run.py is the clean root entry point
[✓] __all__ defined in every module

Code Quality:
[✓] Every function has a docstring
[✓] Type hints on all function signatures
[✓] No magic numbers — all constants in config.py
[✓] No dead code or unused imports
[✓] No print() in library code — only in display/renderer.py and CLI
[✓] snake_case variables, PascalCase classes, ALL_CAPS constants
[✓] if __name__ == "__main__" in every runnable file

Error Handling:
[✓] All file I/O wrapped in try/except StorageError
[✓] All network calls wrapped in try/except with specific types
[✓] All user input validated before use
[✓] KeyboardInterrupt and EOFError handled in shell
[✓] No bare except: clauses

Data & Storage:
[✓] Atomic writes — temp file + rename
[✓] Backup created on corruption detection
[✓] All Task objects serialise/deserialise cleanly
[✓] JSON round-trip tested manually

Security:
[✓] No secrets in code — config.py has no API keys
[✓] User-Agent header sent with all API requests
[✓] Rate limit handling in API calls

Documentation:
[✓] README.md written and accurate
[✓] CHANGELOG.md up to date
[✓] requirements.txt present
[✓] Code review checklist passing

Score: 30/30 ✓
Status: READY TO TAG v1.0.0
```

---

### Tagging v1.0.0 with Git

```bash
# Ensure everything is committed
git add .
git commit -m "feat: TaskFlow AI v1.0.0 - Phase 1 milestone

- Full interactive CLI with 9 commands
- Smart task parser with shorthand syntax
- Task type hierarchy (Urgent, Recurring, Deadline)
- JSON persistence with atomic writes
- Weather + forecast integration
- argparse dual-mode CLI
- Complete documentation and code review"

# Tag the release
git tag -a v1.0.0 -m "TaskFlow AI v1.0.0 — Phase 1 milestone"
git push origin main --tags
```

---

## Exercises

**Exercise 1 — Add `--json` output flag.**
Add a `--json` flag to the `view` subcommand that outputs tasks as JSON to stdout instead of the formatted table. Useful for scripting:

```bash
python run.py view --json | python -m json.tool
```

**Exercise 2 — `--limit` for view.**
Add `--limit N` to `view` to show only the first N tasks. Combine with `--priority` and `--pending` for a "today's top 3 urgent tasks" query:

```bash
python run.py view --priority high --pending --limit 3
```

**Exercise 3 — Shell completions preview.**
Write a `taskflow completion` subcommand that prints a bash completion script stub. Don't implement full completion — just print a comment explaining what it would do and the `complete -F` invocation. This plants the seed for a real completion script in Phase 2.

**Exercise 4 — `requirements.txt` and `pyproject.toml`.**
Create `requirements.txt` (just `requests>=2.31`). Then create a minimal `pyproject.toml`:

```toml
[project]
name    = "taskflow-ai"
version = "1.0.0"
description = "Intelligent task management from the terminal"
requires-python = ">=3.14"
dependencies    = ["requests>=2.31"]

[project.scripts]
taskflow = "taskflow.main:main"
```

Install in development mode: `pip install -e .` Then run `taskflow` as a global command.

**Exercise 5 — Full end-to-end test.**
Write a `test_e2e.py` that runs a sequence of one-shot commands using `subprocess.run()` and asserts the output contains expected strings:

```python
import subprocess, json

def run(args):
    result = subprocess.run(
        ["python", "run.py"] + args,
        capture_output=True, text=True
    )
    return result.stdout, result.returncode

out, code = run(["add", "Test task #high @work"])
assert "created" in out.lower(), f"Expected 'created' in: {out}"
assert code == 0

out, code = run(["view", "--priority", "high"])
assert "Test task" in out
```

**Exercise 6 (stretch) — Man page.**
Write a `docs/taskflow.1` man page in `troff` format (or generate it from `argparse` using `argparse-manpage`). This is the level of documentation polish that separates hobby projects from professional tools.

---

## Checkpoint

Before moving to Day 16 and Week 3:

- [ ] `argparse` CLI is working — `--help` shows all commands and flags
- [ ] One-shot mode works: `python run.py add "..."`, `python run.py view`, etc.
- [ ] Interactive mode launches when no subcommand is given
- [ ] `README.md` is written and accurate
- [ ] `CHANGELOG.md` documents all versions from 0.1.0 to 1.0.0
- [ ] `requirements.txt` is present and correct
- [ ] All 30 items on the code review checklist are passing
- [ ] `git tag v1.0.0` is applied and pushed
- [ ] The project can be cloned fresh and run with just `pip install -r requirements.txt && python run.py`

---

## What's Coming — Week 3 Preview

Phase 1 is complete. The foundation is solid. Week 3 starts Phase 2 — **Real Engineering** — where we apply professional software engineering practices to the codebase:

- **Day 16** — List comprehensions and lambdas (making code more Pythonic)
- **Day 17** — Decorators and context managers
- **Day 18** — Virtual environments and dependency management
- **Day 19** — Git and version control (deep dive)
- **Day 20** — Phase 1 retrospective and architecture review

The project will gain: filtering pipelines, timed decorators, proper environment isolation, a git workflow with branches and PRs, and a complete architectural diagram of everything built so far. TaskFlow AI v1.1 ships at Day 20.
