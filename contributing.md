# Contributing to TaskFlow AI

Thank you for contributing! This guide explains the development workflow.

## Setup

```bash
git clone https://github.com/udit/taskflow.git
cd taskflow
uv venv && uv pip install -e ".[dev]"
pre-commit install
cp .env.example .env
python run.py   # verify it runs
```

## Branch Naming

| Work type | Branch name |
|-----------|-------------|
| New feature | `feature/<short-description>` |
| Bug fix | `fix/<short-description>` |
| Documentation | `docs/<short-description>` |
| Refactor | `refactor/<short-description>` |
| CI/tooling | `chore/<short-description>` |

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body — explain WHY, not what]

[optional footer — BREAKING CHANGE, closes #issue]
```

Types: `feat` `fix` `docs` `style` `refactor` `test` `chore` `perf` `ci`

Examples:
```
feat(parser): add support for ~weekly recurring tasks
fix(storage): handle JSONDecodeError on corrupted file
refactor(core): replace task dicts with Task class
test(services): add parametrised limit boundary tests
chore(deps): upgrade requests to 2.31.0
```

## Pull Request Checklist

Before opening a PR:
- [ ] `pytest` — all tests pass
- [ ] `ruff check .` — no linting errors
- [ ] `black --check .` — code is formatted
- [ ] `mypy taskflow/` — no type errors
- [ ] Docstrings on all new public functions
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] New features have corresponding tests

## Code Style

- **Line length:** 88 characters (Black default)
- **Imports:** sorted by `ruff` (`isort`-compatible order)
- **Docstrings:** Google style
- **Type hints:** required on all public function signatures
- **`print()`:** only in `taskflow/display/renderer.py`
- **`input()`:** only in `taskflow/display/commands.py`
- **Business logic:** in `taskflow/services.py` — no print, no input, fully testable

## Module Responsibility Rules

| Module | Sole responsibility |
|--------|-------------------|
| `config.py` | Static constants only |
| `errors.py` | Exception class definitions |
| `services.py` | Pure business logic — no I/O |
| `utils.py` | Shared pure helpers |
| `display/renderer.py` | All terminal output — the ONLY `print()` module |
| `display/commands.py` | Input collection + output formatting |
| `storage/json_store.py` | File persistence only |

## Running Tests

```bash
pytest                          # all tests
pytest tests/test_task.py       # single file
pytest -k "test_mark_done"      # by name
pytest --cov=taskflow           # with coverage
pytest --cov=taskflow --cov-report=html  # HTML report
open htmlcov/index.html
```

Coverage must stay above 75% (`fail_under` in `pyproject.toml`).

## Questions?

Open a GitHub Issue or start a Discussion.