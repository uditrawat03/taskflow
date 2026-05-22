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