# TaskFlow AI — Technical Debt Register

Last updated: Day 30

## Legend
- **Critical** — blocks Phase 3; fix before FastAPI work begins
- **High** — fix during Phase 2 continued or early Phase 3
- **Low** — fix when convenient; documents known imperfection

---

## Critical — Fix Before Phase 3

### TD-001: display/commands.py mixed concerns ✅ RESOLVED (Day 21)
- **Problem:** Commands mixed UI, validation, and business logic.
- **Fix:** `services.py` extracted; commands now delegate to it.
- **Resolved:** Day 21

### TD-002: Task objects and dicts coexisted ✅ RESOLVED (Day 22)
- **Problem:** Dual-path code with `isinstance(task, Task)` everywhere.
- **Fix:** `renderer.py` and `services.py` standardised on Task objects.
- **Resolved:** Day 22

---

## High — Fix During Phase 2 / Early Phase 3

### TD-003: Test coverage was zero ✅ RESOLVED (Days 25-26)
- **Problem:** No automated tests.
- **Fix:** Full test suite with 120+ tests, 90%+ coverage.
- **Resolved:** Day 26

### TD-004: Weather fetched on every startup ✅ RESOLVED (Day 18)
- **Problem:** Network call blocked every launch, even for one-shot commands.
- **Fix:** 10-minute file cache in `weather_cache.json`.
- **Resolved:** Day 18

### TD-005: USER_NAME hardcoded in config.py ✅ RESOLVED (Day 24)
- **Problem:** No personalisation without editing source.
- **Fix:** `TASKFLOW_USER_NAME` env var via `env_config.py`.
- **Resolved:** Day 24

### TD-006: shell.py and cli.py had overlapping dispatch ✅ RESOLVED (Day 21)
- **Problem:** Both files duplicated command routing.
- **Fix:** `services.py` + `commands.py` are the single source of truth.
- **Resolved:** Day 21

---

## Low — Address When Convenient

### TD-007: CONTRIBUTING.md referenced non-existent tests
- **Problem:** Written Day 19 before tests existed.
- **Status:** Tests added Day 25. CONTRIBUTING.md updated Day 26.
- **Resolved:** Day 26

### TD-008: No SQLite backend yet
- **Problem:** JSON storage degrades with thousands of tasks.
- **Fix:** Day 34 — `SqliteTaskRepository` via Repository pattern (already wired).
- **Target:** Day 34

### TD-009: Weather uses sync `requests` inside async startup fallback
- **Problem:** When `aiohttp` unavailable, `asyncio.to_thread` wraps blocking call.
- **Fix:** Make `aiohttp` a non-optional dependency, or always use `to_thread`.
- **Effort:** Low

### TD-010: No input sanitisation on task titles
- **Problem:** Titles can contain SQL injection strings, HTML, etc.
- **Impact:** Harmless now (JSON storage), critical when DB/API added.
- **Fix:** Day 36 — Security basics; sanitise at `parser.py` level.
- **Target:** Day 36

---

## Metrics (Day 30)

| Metric | Value |
|--------|-------|
| Python files | 27 |
| Test files | 11 |
| Test functions | 120+ |
| Coverage | ~90% |
| Open TD items | 3 (low severity) |
| Resolved TD items | 7 |