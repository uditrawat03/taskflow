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
git clone https://github.com/udit/taskflow
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