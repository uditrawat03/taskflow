# TaskFlow AI 🗒️

> Intelligent task management from the terminal — built across 90 days of learning Python & AI Engineering.

[![Python](https://img.shields.io/badge/python-3.14-blue)]()
[![Version](https://img.shields.io/badge/version-1.1.0-green)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()

## What Is This?

TaskFlow AI is a command-line task manager built day-by-day in a public 90-day Python & AI Engineering series. It demonstrates:

- Python 3.14 best practices and type hints
- Object-oriented design (Task class hierarchy with polymorphism)
- Repository pattern for pluggable storage backends
- Observer pattern (event bus) and Strategy pattern (pluggable sort)
- JSON persistence with atomic writes
- Real API integration (weather via Open-Meteo — no key required)
- Natural language task input parsing with regex
- Async startup with asyncio.gather()
- Professional logging (structured JSON + rotating file handler)
- Environment-based configuration via python-dotenv
- Design patterns: Repository, Singleton, Factory, Observer, Strategy
- Full test suite with pytest (90%+ coverage)

## Quick Start

```bash
git clone https://github.com/udit/taskflow
cd taskflow

# Create virtual environment
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
.venv\Scripts\activate        # Windows

# Install dependencies
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env
# Edit .env with your name and location

# Run
python run.py
```

Or with uv (10× faster):

```bash
uv venv && uv pip install -e ".[dev]"
python run.py
```

## Task Shorthand Syntax

| Syntax | Meaning | Example |
|--------|---------|---------|
| `!!` prefix | Urgent task (priority forced to high) | `!! Server down @work` |
| `~daily` prefix | Recurring task | `~daily Standup @work` |
| `#high` token | Set priority | `Review PR #high` |
| `@work` token | Set category | `Buy milk @personal` |
| `!YYYY-MM-DD` token | Set due date (DeadlineTask) | `Submit report !2025-06-01` |

Tokens can be combined: `Review PR #high @work !2025-06-01`

## Interactive Commands

| Command | Description |
|---------|-------------|
| `add` | Add a task (smart shorthand parser) |
| `view` | View all tasks in a formatted table |
| `done` | Mark a task as done |
| `remove` | Remove a task permanently |
| `rename` | Rename a task |
| `filter` | Filter by priority / category / status |
| `search` | Search by keyword or `re:regex` pattern |
| `stats` | Statistics dashboard |
| `detail` | Full detail view for one task |
| `weather` | Current weather (Open-Meteo) |
| `forecast` | 3-day weather forecast |
| `backup` | Create a timestamped backup |
| `storage` | Show storage file information |
| `help` | Command reference |
| `quit` | Save and exit |

## One-Shot CLI

```bash
python run.py add "Review PR #high @work"
python run.py view --priority high --pending
python run.py view --limit 5
python run.py done 3
python run.py remove 5
python run.py search "review"
python run.py stats
python run.py forecast
python run.py --help
```

## Task Types

| Type | Shorthand | Behaviour |
|------|-----------|-----------|
| `Task` | default | Standard task |
| `UrgentTask` | `!! title` | Priority always high, escalation note |
| `RecurringTask` | `~daily title` | Auto-resets to pending after done |
| `DeadlineTask` | `title !date` | Tracks urgency by due date |

## Project Structure

```
taskflow/
├── config.py          — All static constants
├── env_config.py      — Environment-based settings (python-dotenv)
├── errors.py          — Custom exception hierarchy
├── services.py        — Pure business logic (no print, no I/O)
├── utils.py           — Shared helper functions
├── parser.py          — Natural language task input parser
├── filters.py         — TaskFilter fluent pipeline
├── decorators.py      — @timer, @retry, @validate_non_empty
├── context.py         — task_snapshot, timed_operation context managers
├── events.py          — EventBus (Observer pattern)
├── strategies.py      — Sort strategies (Strategy pattern)
├── logging_config.py  — Structured JSON + console logging
├── async_startup.py   — Concurrent startup with asyncio
├── shell.py           — Interactive command loop
├── cli.py             — argparse one-shot CLI
├── main.py            — Application entry point
├── core/
│   ├── task.py        — Task base class
│   ├── task_types.py  — UrgentTask, RecurringTask, DeadlineTask
│   ├── task_factory.py — Polymorphic deserialisation
│   └── stats.py       — Pure statistics calculations
├── storage/
│   └── json_store.py  — JSON persistence with atomic writes
├── integrations/
│   └── weather.py     — Open-Meteo API integration + file cache
├── repositories/
│   ├── base.py        — Abstract TaskRepository (interface)
│   └── json_repo.py   — JSON file implementation
└── display/
    ├── renderer.py    — ALL terminal output (only module with print())
    └── commands.py    — Command handlers (thin UI layer)
```

## Configuration

Copy `.env.example` to `.env` and edit:

```bash
TASKFLOW_USER_NAME=Udit
TASKFLOW_USER_PLAN=free         # free | premium | enterprise
TASKFLOW_LATITUDE=28.6139       # your location for weather
TASKFLOW_LONGITUDE=77.2090
TASKFLOW_LOCATION=Delhi, IN
TASKFLOW_LOG_LEVEL=INFO         # DEBUG | INFO | WARNING
TASKFLOW_WEATHER=true
```

## Running Tests

```bash
pytest                          # all tests
pytest -v                       # verbose
pytest tests/test_task.py       # single file
pytest -k "test_mark_done"      # by name
pytest --cov=taskflow           # with coverage
pytest --cov=taskflow --cov-report=html  # HTML report
```

## Dependencies

```
requests>=2.28       # HTTP client for weather API
python-dotenv>=1.0   # .env file loading
```

Optional:
```
aiohttp>=3.9         # Async HTTP (faster weather fetch)
```

Install all: `pip install -e ".[dev]"` or `uv pip install -e ".[dev]"`

## What's Next (Phase 3 — Days 41-60)

- FastAPI REST API replacing the CLI shell
- JWT authentication — per-user task isolation
- PostgreSQL + SQLAlchemy ORM
- Redis caching
- Celery background jobs
- Docker + docker-compose
- GitHub Actions CI/CD
- Cloud deployment (Railway/Render)

## License

MIT License — see `LICENSE` for details.

---

*Built across 90 days of public learning — from `print("Hello World")` to an AI-powered cloud product.*