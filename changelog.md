# Changelog

All notable changes to TaskFlow AI are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com).
Versions follow [Semantic Versioning](https://semver.org).

---

## [Unreleased]

---

## [1.1.0] — Day 20 (Phase 2 Engineering Milestone)

### Added
- `taskflow/services.py` — pure business logic layer, no print/input (Day 21)
- `taskflow/utils.py` — shared helpers: `task_attr`, `pluralise`, `truncate` (Day 21)
- `taskflow/logging_config.py` — `JsonFormatter` + rotating file handler (Day 23)
- `taskflow/env_config.py` — `Settings` dataclass, `get_settings()`, python-dotenv (Day 24)
- `taskflow/filters.py` — `TaskFilter` fluent pipeline (Day 16)
- `taskflow/decorators.py` — `@timer`, `@retry`, `@validate_non_empty`, `@log_call`, `@deprecated` (Day 17)
- `taskflow/context.py` — `task_snapshot`, `timed_operation`, `temporary_data_file` (Day 17)
- `taskflow/events.py` — `EventBus` (Observer pattern), `Events` constants (Day 29)
- `taskflow/strategies.py` — `SortByPriority`, `SortByTitle`, `SortByDueDate`, `CompositeSort` (Day 29)
- `taskflow/repositories/` — `TaskRepository` ABC + `JsonTaskRepository` (Day 28)
- `taskflow/async_startup.py` — concurrent startup with `asyncio.gather()` (Day 30)
- `pyproject.toml` — project metadata, dependencies, Black/Ruff/Mypy/pytest config (Day 18)
- `.env.example` + `.env.test` — environment template and test overrides (Day 24)
- `.pre-commit-config.yaml` — Black, Ruff, Mypy hooks (Day 18)
- `CONTRIBUTING.md` — branch naming, commit format, PR checklist (Day 19)
- `tests/` — full test suite: 120+ tests across 10 test files (Days 25-26)
- `tests/conftest.py` — shared fixtures with autouse counter/bus/settings resets
- `--debug` flag for DEBUG-level console logging (Day 23)
- `--no-weather` flag to skip weather fetch (Day 30)

### Changed
- `main.py` uses `asyncio.run(run_startup())` for concurrent startup (Day 30)
- `main.py` reads all config from `get_settings()` — no hardcoded values (Day 24)
- `logging_config.py` called first in `main()` before any other code (Day 23)
- `display/commands.py` delegates mutations to `services.py` (Day 21)
- `display/renderer.py` accepts Task objects natively (Day 22)
- `TaskFactory` upgraded to class with `register()` method (Day 29)
- `task_from_dict()` now uses `TaskFactory.create_from_dict()` (Day 29)

### Fixed
- Weather cached to `data/weather_cache.json` with 10-minute TTL (Day 18)
- `load_tasks_safe()` returns `([], error_str)` tuple — never raises (Day 10)
- Atomic write via `.tmp` rename prevents corrupt storage files (Day 08)

---

## [1.0.0] — Day 15 (Phase 1 Milestone)

### Added
- Interactive terminal shell with full command loop
- `add`, `view`, `done`, `remove`, `filter`, `search`, `stats`, `detail`,
  `rename`, `backup`, `forecast`, `weather`, `storage`, `help`, `quit` commands
- Smart task parser: `!!`, `~daily/weekly/monthly`, `#priority`, `@category`, `!date`
- Task type system: `Task`, `UrgentTask`, `RecurringTask`, `DeadlineTask`
- JSON persistence with atomic writes and backup on corruption
- Open-Meteo weather integration (no API key required)
- 3-day weather forecast display
- Custom exception hierarchy: `TaskFlowError` → `StorageError`, `ValidationError`,
  `TaskNotFoundError`, `WeatherError`
- `argparse` dual-mode CLI (interactive + one-shot subcommands)
- Proper Python package structure: `core/`, `storage/`, `integrations/`, `display/`
- `if __name__ == "__main__"` in every runnable file
- `CONTRIBUTING.md` placeholder (completed Day 19)

### Architecture
- `Task` class with `__str__`, `__repr__`, `__eq__`, `__lt__`, `__hash__`
- `@property` validation on `priority` and `category`
- `Task._id_counter` class attribute replaces `next_id = [1]` list hack
- `Task.from_dict()` / `Task.to_dict()` for clean JSON round-trips
- `TaskFactory` for polymorphic deserialisation
- `ParseResult` dataclass from natural language parser
- `COMMANDS` dict registry — help auto-generates from it

---

## [0.4.0] — Day 07

- Code review pass, `debug_practice.py`, edge cases hardened, checklist 10/10

## [0.3.0] — Day 06

- Full function refactor, docstrings, command registry, `if __name__ == "__main__"`

## [0.2.0] — Day 05

- Tasks upgraded from strings to dict objects, categories, priorities, set tracking

## [0.1.0] — Day 04

- Initial interactive task list with add/view/remove/quit command loop