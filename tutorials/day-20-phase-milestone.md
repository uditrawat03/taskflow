# Day 20 — Phase 1 Retrospective & Architecture Review

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering (Milestone)
> **Python Version:** 3.14
> **Project:** TaskFlow AI v1.1 — Shipping the Phase 2 engineering upgrade

---

## Learning Objective

By the end of today, you will have done a full architectural review of everything built across 20 days, identified and documented technical debt, shipped TaskFlow AI v1.1 with all Phase 2 improvements consolidated, and have a clear, written plan for Phase 3. This is not a coding day — it is a thinking and shipping day. These matter just as much.

---

## What We Build Today

A complete architectural review document, a system diagram, a technical debt register, the v1.1 release, and a Phase 3 roadmap written into `CHANGELOG.md`. The deliverable is clarity — knowing exactly what you have, what it owes, and where it is going.

```
TaskFlow AI — Architecture at Day 20
=====================================

Entry Points:
  python run.py           → interactive shell
  python run.py add "..."  → one-shot command (Day 15)
  taskflow add "..."       → installed entry point

Data Flow:
  User input
    → parser.py (regex, shorthand)
    → display/commands.py (validation, dispatch)
    → core/task*.py (business logic, Task objects)
    → storage/json_store.py (atomic JSON write)
    → display/renderer.py (terminal output)

External:
  weather.py → Open-Meteo API (no auth required)

Cross-cutting:
  decorators.py → @timer, @retry, @validate_non_empty
  context.py    → task_snapshot, timed_operation
  filters.py    → TaskFilter fluent pipeline
  errors.py     → exception hierarchy
  config.py     → all constants
```

---

## Concepts Covered

- Architectural review — reading your own codebase critically
- System diagrams — C4 model basics
- Technical debt — identification, classification, prioritisation
- Retrospective — what worked, what did not, what to change
- ADRs — Architecture Decision Records
- Semantic versioning — when to bump MAJOR, MINOR, PATCH
- Release process — tag, changelog, push
- Phase planning — turning a roadmap into concrete next steps

---

## Full Tutorial

### Why Review Days Matter

Most tutorials skip review days. That is why most tutorial projects never grow beyond the tutorial. In real engineering, teams spend 20-30% of their time reviewing, refactoring, and paying down technical debt. The projects that survive for years are the ones that treat review as a first-class activity.

Today you do what senior engineers do after every significant milestone: zoom out, read the whole system, ask hard questions, write down what you find, and make concrete decisions about what to do next.

---

### The Architectural Review Process

Work through these four steps in order. Take your time.

---

#### Step 1 — Read Every File

Open every `.py` file in the project. For each one, ask:

- Does this file do one thing?
- Is the naming clear and consistent?
- Are there any functions longer than 30 lines?
- Is there anything I would be embarrassed to show another developer?
- Is there any logic that is duplicated somewhere else?

Write down everything you find. Do not fix anything yet — just observe.

---

#### Step 2 — Draw the System Diagram

Draw (on paper, whiteboard, or in a tool like Excalidraw) the complete system at three levels:

**Level 1 — Context (who uses it and what it connects to):**

```
┌─┐
│              TaskFlow AI                │
│                                         │
│  User ► CLI / Shell ► Task Storage  │
│                    │                    │
│                    └► Weather API     │
└─┘
```

**Level 2 — Container (what modules exist):**

```
┌┐
│  taskflow package                                       │
│                                                         │
│  ┌┐  ┌┐  ┌─┐  │
│  │ shell.py │  │  cli.py  │  │  display/commands.py │  │
│  └┬─┘  └┬─┘  └┬┘  │
│       │              │                   │              │
│  ┌▼▼─▼┐  │
│  │              core/                               │  │
│  │  task.py │ task_types.py │ task_factory.py       │  │
│  │  stats.py                                        │  │
│  └┬┘  │
│                        │                               │
│  ┌─▼┐                   │
│  │  storage/json_store.py         │                   │
│  └┘                   │
│                                                         │
│  ┌─┐                  │
│  │  integrations/weather.py        │► Open-Meteo   │
│  └─┘                  │
│                                                         │
│  Cross-cutting: decorators.py, context.py,            │
│                 filters.py, parser.py,                │
│                 errors.py, config.py                  │
└┘
```

**Level 3 — Component (how modules interact):**
This is the dependency flow diagram already documented in the Day 18 file listing supplement. Verify it is still accurate.

---

#### Step 3 — Technical Debt Register

A **technical debt register** is a list of things you know are not ideal and should eventually be fixed. Writing it down prevents the debt from being forgotten or growing invisibly.

Create `docs/technical-debt.md`:

```markdown
# TaskFlow AI — Technical Debt Register
Last updated: Day 20

## Critical (fix before Phase 3)

### TD-001: display/commands.py handles both display and business logic
- **File:** taskflow/display/commands.py
- **Problem:** The module does too much — it validates input, calls business
  logic, and formats output. The name 'display' is misleading.
- **Impact:** Hard to test business logic in isolation.
- **Fix:** Split into commands.py (input handling) and a separate
  services.py (business logic calls). Renderer stays in renderer.py.
- **Effort:** Medium (1-2 hours)

### TD-002: Task objects and dicts coexist in the same lists
- **File:** taskflow/display/commands.py, shell.py
- **Problem:** Some parts of the app use Task objects (post-Day 12),
  some parts still pass raw dicts. The _to_dict() helper is a workaround.
- **Impact:** Confusing, error-prone, hard to type-check.
- **Fix:** Standardise on Task objects throughout. The renderer.py
  should accept Task objects directly, not dicts.
- **Effort:** Medium (2-3 hours)

## High (fix during Phase 2 or 3)

### TD-003: No tests
- **File:** tests/ (empty)
- **Problem:** Zero test coverage. Changes are verified manually only.
- **Impact:** High risk of regressions as codebase grows.
- **Fix:** Add unit tests for Task, stats, storage, and parser (Day 25).
- **Effort:** High (ongoing)

### TD-004: Weather fetched on every startup
- **File:** taskflow/main.py, integrations/weather.py
- **Problem:** Weather API is called on every `python run.py` invocation,
  even for one-shot commands like `taskflow view`.
- **Impact:** Slow cold start (~0.5-1s) for simple commands.
- **Fix:** Cache weather to a file with a 10-minute TTL. Skip fetch
  for one-shot commands unless `--weather` flag is passed.
- **Effort:** Low (30 minutes)

### TD-005: USER_NAME hardcoded in config.py
- **File:** taskflow/config.py
- **Problem:** "Udit" is baked into the source code. Other users cannot
  personalise without editing config.py.
- **Impact:** Not a real multi-user app.
- **Fix:** Read USER_NAME from .env or a user settings file (Day 24).
- **Effort:** Low (30 minutes)

## Low (nice to have, fix when convenient)

### TD-006: shell.py and cli.py have overlapping command dispatch
- **Problem:** Both shell.py and cli.py duplicate parts of the command
  dispatch logic.
- **Fix:** Unify into a single dispatch table in commands.py.
- **Effort:** Low

### TD-007: renderer.py accepts dicts but Task objects are richer
- **Problem:** display_tasks() takes a list[dict] but Task objects have
  methods (is_overdue(), urgency_label) that dicts do not.
- **Fix:** Accept list[Task | dict] and use isinstance() to call the
  right attributes.
- **Effort:** Low
```

---

#### Step 4 — Architecture Decision Records

An **Architecture Decision Record (ADR)** documents a significant architectural decision — what was decided, why, and what alternatives were rejected. They prevent the same debates from happening twice.

Create `docs/adr/` and write one ADR for the most important decision of Phase 1:

```markdown
# ADR-001: Use JSON files for task storage (not SQLite)

**Date:** Day 08
**Status:** Accepted
**Deciders:** Udit Rawat

## Context

TaskFlow AI needed a persistence mechanism for task data.
Options considered: plain text files, JSON files, SQLite, PostgreSQL.

## Decision

Use JSON files with atomic writes (temp file + rename).

## Rationale

- **Zero dependencies** — no database driver, no server, no setup
- **Human-readable** — tasks can be inspected and edited in any text editor
- **Debuggable** — corrupted state is visible and fixable without tools
- **Sufficient for Phase 1** — 10-100 tasks fits comfortably in one JSON file
- **Migration path clear** — to_dict() / from_dict() on Task objects means
  swapping storage backends requires changing only json_store.py

## Consequences

- Not suitable for concurrent access (multiple processes writing simultaneously)
- Performance degrades for thousands of tasks (full file rewrite on every save)
- No querying capabilities (all filtering done in Python)

## Superseded by

ADR-003: Switch to SQLite (Day 34)
ADR-005: Switch to PostgreSQL (Day 55)
```

---

### Shipping TaskFlow AI v1.1

After the review, apply the fixes you identified as "Critical" and "Low effort". Then release v1.1:

```bash
# Apply TD-004 fix — cache weather to file
# (Quick implementation)

# taskflow/integrations/weather.py — add simple file cache
import json, time
from pathlib import Path

_CACHE_FILE = Path(__file__).parent.parent.parent / "data" / "weather_cache.json"
_CACHE_TTL  = 600   # 10 minutes

def _load_cache() -> dict | None:
    if not _CACHE_FILE.exists():
        return None
    try:
        data = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
        if time.time() - data.get("fetched_at", 0) < _CACHE_TTL:
            return data.get("weather")
    except Exception:
        pass
    return None

def _save_cache(weather: dict) -> None:
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(
            json.dumps({"fetched_at": time.time(), "weather": weather},
                       indent=2),
            encoding="utf-8"
        )
    except Exception:
        pass   # cache failure is never critical

def fetch_weather(latitude, longitude, location_name="", use_cache=True):
    if use_cache:
        cached = _load_cache()
        if cached:
            return cached
    # ... existing fetch logic ...
    weather = _do_fetch(latitude, longitude, location_name)
    if weather:
        _save_cache(weather)
    return weather
```

Update `CHANGELOG.md`:

```markdown
## [1.1.0] — Day 20

### Added
- TaskFilter fluent pipeline for composable task filtering (Day 16)
- `@timer`, `@retry`, `@validate_non_empty`, `@log_call`, `@deprecated` decorators (Day 17)
- `task_snapshot`, `timed_operation`, `temporary_data_file` context managers (Day 17)
- `pyproject.toml` with full project metadata and tool configuration (Day 18)
- `uv` support — faster dependency management (Day 18)
- `pre-commit` hooks — black, ruff, mypy on every commit (Day 18)
- `CONTRIBUTING.md` — developer guide and PR checklist (Day 19)
- `docs/technical-debt.md` — documented debt register (Day 20)
- `docs/adr/ADR-001.md` — storage decision record (Day 20)

### Fixed
- Weather cached to file — 10-minute TTL prevents repeated API calls (TD-004)
- `.gitignore` updated to exclude weather cache file

### Changed
- `requirements.in` / `requirements-dev.in` replace raw `requirements.txt`
- All secrets moved to `.env.example` pattern

### Architecture
- `display/commands.py` created as the integration layer between
  user input and business logic
- Dependency flow fully documented and verified (no circular imports)
- Technical debt register established
```

Tag and push:

```bash
git add .
git commit -m "release: TaskFlow AI v1.1.0 — Phase 2 engineering milestone"
git tag -a v1.1.0 -m "Phase 2 engineering milestone — Days 16-20"
git push origin main --tags
```

---

### Phase 3 Preview — What's Next

Write the Phase 3 plan into `docs/phase3-plan.md`:

```markdown
# Phase 3 Plan — Modern Backend Engineering (Days 41-60)

## Goal
Transform TaskFlow AI from a CLI tool into a production-grade
REST API with authentication, caching, background jobs, and
cloud deployment.

## Architecture Change
CLI (current) → FastAPI REST API + CLI client

## Key Milestones

### Day 41-44: FastAPI Foundation
- Replace shell.py with a FastAPI application
- Expose all task operations as REST endpoints
- Pydantic models for request/response validation
- Auto-generated Swagger docs

### Day 45-46: Authentication
- JWT-based auth — register, login, protected routes
- Per-user task isolation (currently all tasks are "Udit's")

### Day 47-49: Scalability
- Redis caching for GET /tasks
- Celery background jobs for AI analysis (Phase 4)
- WebSocket for real-time task updates

### Day 50-52: Database
- SQLite → PostgreSQL migration
- SQLAlchemy ORM replaces json_store.py
- Alembic migrations for schema changes

### Day 53-55: Containerisation
- Dockerfile for the FastAPI app
- docker-compose.yml: app + PostgreSQL + Redis
- Environment-based configuration (.env in container)

### Day 56-58: CI/CD
- GitHub Actions: test → lint → build → deploy
- Staging environment on Railway/Render
- Health check endpoint

### Day 59-60: Observability
- Sentry error tracking
- Prometheus metrics
- Structured JSON logging

## Technical Debt to Resolve Before Phase 3
- TD-001: Split commands.py (medium effort)
- TD-002: Standardise on Task objects (medium effort)
- TD-003: Add test suite — Day 25 (high effort, started Day 25)
```

---

## Phase 1 & 2 Retrospective — What to Reflect On

Answer these honestly in a journal, a vlog, or a document:

**What went well:**
- The project thread (one app across all 20 days) kept motivation high
- Each day's "What We Build" section gave clear, visible progress
- The Task class hierarchy (Day 12-13) was the most satisfying architectural moment
- The decorator and context manager day showed Python at its most elegant

**What was hard:**
- The package restructure (Day 11) required touching every file
- Keeping `commands.py`, `shell.py`, `renderer.py`, and `cli.py` from overlapping took discipline
- Managing state (task list) without a class or database required workarounds

**What to do differently in Phase 3:**
- Start with the data model (database schema) before writing any API code
- Write tests alongside features, not after (TDD from Day 41)
- Keep `commands.py` out of `display/` — it is not a display concern

---

## Exercises

**Exercise 1 — Complete the tech debt register.**
Add five more entries to `docs/technical-debt.md` based on your own code review. Classify each as Critical, High, or Low. Estimate effort. This document will be referenced every phase.

**Exercise 2 — Draw the full system diagram.**
Use Excalidraw (excalidraw.com), draw.io, or paper. Draw all three C4 levels. Export as PNG and add to `docs/architecture.png`. Reference it from `README.md`.

**Exercise 3 — Write ADR-002.**
Write an ADR for a second significant decision from Phase 1 — e.g.:
- "Why we chose Task objects over dicts"
- "Why we chose Open-Meteo over OpenWeatherMap"
- "Why we used pipe-separation before JSON"

Follow the same format as ADR-001.

**Exercise 4 — Metrics.**
Run these measurements and record the results in `docs/metrics-day20.md`:

```bash
# Lines of code (excluding blank lines and comments)
find taskflow/ -name "*.py" | xargs grep -v "^#" | grep -v "^$" | wc -l

# Number of functions
grep -r "^def \|^    def " taskflow/ | wc -l

# Number of classes
grep -r "^class " taskflow/ | wc -l

# Number of modules
find taskflow/ -name "*.py" | wc -l

# Test coverage (none yet — establish the baseline)
pytest --cov=taskflow --cov-report=term-missing 2>/dev/null || echo "No tests yet"
```

Record these numbers. You will compare them at Day 40 and Day 60 to measure growth.

**Exercise 5 — The "explain it to someone" test.**
Record a 5-minute video (or write 500 words) explaining TaskFlow AI's architecture to a developer who has not seen the code. Cover: what it does, how data flows through it, where the main complexity lives, what you would change with hindsight. This forces you to understand your own system deeply.

**Exercise 6 (stretch) — Dependency graph tool.**
Install `pydeps` and generate a visual dependency graph of the `taskflow` package:

```bash
pip install pydeps
pydeps taskflow --max-bacon=3 --output docs/dependency-graph.svg
```

Open the SVG in a browser. Does the graph match the dependency flow diagram in the Day 18 supplement? Are there any unexpected connections? Add the graph to `README.md`.

---

## Checkpoint — End of Phase 2 Opening

Before moving to Day 21 (Clean Code Principles):

- [ ] I have read every file in the project and written down observations
- [ ] The system diagram exists at all three C4 levels
- [ ] `docs/technical-debt.md` has at least 5 entries, classified and estimated
- [ ] `docs/adr/ADR-001.md` is written
- [ ] `CHANGELOG.md` is updated for v1.1.0
- [ ] `git tag v1.1.0` is applied and pushed
- [ ] The Phase 3 plan is written in `docs/phase3-plan.md`
- [ ] I can explain the full system architecture from memory

---

## What's Coming — Days 21-40

Phase 2 continues with the engineering practices that transform good code into great code:

- **Day 21** — Clean Code Principles (naming, function length, comments)
- **Day 22** — Project structure deep dive
- **Day 23** — Logging and observability
- **Day 24** — Environment configuration and secrets
- **Day 25** — Testing fundamentals (pytest)
- **Day 26** — Test coverage and mocking
- **Day 27** — Type hints and mypy
- **Day 28** — Design Patterns I (Repository, Singleton)
- **Day 29** — Design Patterns II (Factory, Observer, Strategy)
- **Day 30** — Async programming I
- ...through Day 40 — Phase 2 milestone