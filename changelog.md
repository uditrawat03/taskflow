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