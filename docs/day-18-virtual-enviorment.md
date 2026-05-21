# Day 18 — Virtual Environments & Dependency Management

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Professional dependency isolation and management

---

## Learning Objective

By the end of today, you will understand why virtual environments exist, how to create and manage them, how to pin dependencies for reproducible builds, and how to separate development from production dependencies. TaskFlow AI gets a complete, professional dependency setup using both the standard `venv` + `pip` workflow and `uv` — the modern high-speed package manager.

---

## What We Build Today

A complete, reproducible dependency setup for TaskFlow AI — `requirements.txt`, `requirements-dev.txt`, a `pyproject.toml`, and a documented developer onboarding flow. Any developer (or your future self) can clone the repository and be running in under 60 seconds.

```bash
# The onboarding experience we are building toward:
git clone https://github.com/udit/taskflow
cd taskflow
uv venv && uv pip install -e ".[dev]"
python run.py
# ✓ Running in under 10 seconds
```

---

## Concepts Covered

- Why virtual environments exist — the dependency isolation problem
- `venv` — creating and activating virtual environments
- `pip install`, `pip freeze`, `pip list`
- `requirements.txt` — pinned production dependencies
- `requirements-dev.txt` — development-only dependencies
- `.gitignore` — what to exclude from version control
- `pyproject.toml` — the modern Python project standard
- `pip-tools` — compiling locked dependency files
- `uv` — the fast modern alternative (written in Rust)
- Dependency groups — production vs development vs testing
- Checking for outdated and vulnerable packages
- Environment variables and `.env` files (preview of Day 24)

---

## Full Tutorial

### The Problem Virtual Environments Solve

Without virtual environments, every Python project on your machine shares the same global Python installation. Install `requests==2.28` for Project A, then upgrade to `requests==2.31` for Project B — Project A breaks. There is no way to have two versions of the same package installed globally.

A **virtual environment** is a self-contained directory that has its own Python interpreter and its own set of installed packages, completely isolated from everything else on your machine.

```
Without venv (global Python):
  System Python
  └── site-packages/
      ├── requests 2.31    ← which version is "right"?
      ├── flask 3.0
      └── django 5.1

With venv (isolated):
  taskflow/.venv/
  └── site-packages/
      └── requests 2.31    ← exactly what taskflow needs

  other_project/.venv/
  └── site-packages/
      └── requests 2.28    ← exactly what other_project needs
```

Every Python project must use a virtual environment. No exceptions.

---

### Creating a Virtual Environment with `venv`

`venv` is built into Python — no installation needed:

```bash
# Create a virtual environment named .venv in the project root
python -m venv .venv

# Activate it
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows (Command Prompt)
.venv\Scripts\Activate.ps1     # Windows (PowerShell)

# Your prompt changes to show the active venv:
# (.venv) udit@machine:~/taskflow$

# Verify you are using the venv's Python
which python        # should show .venv/bin/python
python --version    # Python 3.14.x

# Deactivate when done
deactivate
```

**Convention:** name your virtual environment `.venv` (with the dot). It is hidden by default on Linux/macOS, universally recognized, and matched by `.gitignore` templates.

---

### Installing Packages

```bash
# Make sure your venv is activated first!

# Install a package
pip install requests

# Install a specific version
pip install requests==2.31.0

# Install with version constraints
pip install "requests>=2.28,<3.0"

# Install multiple packages at once
pip install requests pytest black ruff

# Install from a requirements file
pip install -r requirements.txt

# Upgrade a package
pip install --upgrade requests

# Uninstall
pip uninstall requests
```

---

### `pip freeze` and `requirements.txt`

After installing everything your project needs, capture the exact versions:

```bash
pip freeze > requirements.txt
```

This creates a file listing every installed package and its exact version:

```
# requirements.txt
certifi==2025.1.31
charset-normalizer==3.3.2
idna==3.7
requests==2.31.0
urllib3==2.2.1
```

Anyone can recreate your exact environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Problem with `pip freeze`:** it includes everything — not just what you directly installed, but all transitive dependencies too. If you only care about `requests`, your `requirements.txt` also lists `certifi`, `charset-normalizer`, `idna`, and `urllib3` (which `requests` depends on). This makes it hard to see what you actually chose to depend on.

The solution: maintain two files.

---

### Two Requirements Files — The Standard Pattern

```
requirements.in        ← what you CHOSE to depend on (hand-written)
requirements.txt       ← fully pinned with ALL transitive deps (generated)
requirements-dev.in    ← dev-only choices (hand-written)
requirements-dev.txt   ← fully pinned dev deps (generated)
```

**`requirements.in`** — hand-written, minimal:

```
# requirements.in
# Direct production dependencies only.
# Run: pip-compile requirements.in --output-file requirements.txt

requests>=2.28
```

**`requirements-dev.in`** — hand-written, minimal:

```
# requirements-dev.in
# Development and testing dependencies.
# Run: pip-compile requirements-dev.in --output-file requirements-dev.txt

-r requirements.in    # include production deps

pytest>=8.0
pytest-cov>=5.0
black>=24.0
ruff>=0.4
mypy>=1.10
pre-commit>=3.7
```

**`requirements.txt`** — generated with `pip-compile`:

```bash
pip install pip-tools
pip-compile requirements.in --output-file requirements.txt
pip-compile requirements-dev.in --output-file requirements-dev.txt
```

The generated files include every transitive dependency pinned to an exact version, with comments showing which direct dependency pulled each one in.

---

### `uv` — The Modern Python Package Manager

`uv` is a drop-in replacement for `pip` and `venv`, written in Rust. It is 10-100× faster than pip, manages virtual environments automatically, and is quickly becoming the standard in professional Python environments.

**Install `uv`:**

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

**Using `uv`:**

```bash
# Create a virtual environment (faster than python -m venv)
uv venv

# Install packages (faster than pip install)
uv pip install requests
uv pip install -r requirements.txt

# Generate a locked requirements file
uv pip compile requirements.in -o requirements.txt

# Sync environment to exact requirements (installs missing, removes extra)
uv pip sync requirements.txt

# Install the project itself in editable mode
uv pip install -e .
uv pip install -e ".[dev]"   # with dev extras
```

**The `uv` project workflow:**

```bash
# Full setup from scratch
git clone https://github.com/udit/taskflow
cd taskflow
uv venv
uv pip install -e ".[dev]"
python run.py
```

That is the entire onboarding. No separate `pip install` step, no manual venv activation scripts, no version mismatch issues.

---

### `pyproject.toml` — The Modern Project Standard

`pyproject.toml` is the single file that defines everything about your Python project: its metadata, dependencies, build system, and tool configuration. It replaces `setup.py`, `setup.cfg`, `tox.ini`, `mypy.ini`, `.flake8`, and more.

Create `pyproject.toml` in the project root:

```toml
# pyproject.toml
# TaskFlow AI — project definition and tool configuration.

[build-system]
requires      = ["setuptools>=70", "wheel"]
build-backend = "setuptools.backends.legacy:build"


# ── Project Metadata ──────────────────────────────────────

[project]
name        = "taskflow-ai"
version     = "1.0.0"
description = "Intelligent task management from the terminal — 90-day Python series"
readme      = "README.md"
license     = { text = "MIT" }
authors     = [{ name = "Udit Rawat", email = "udit@example.com" }]
keywords    = ["tasks", "productivity", "ai", "cli"]

requires-python = ">=3.14"

# Production dependencies — these are what pip/uv installs by default
dependencies = [
    "requests>=2.28",
]

# Optional dependency groups
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "black>=24.0",
    "ruff>=0.4",
    "mypy>=1.10",
    "pre-commit>=3.7",
    "pip-tools>=7.0",
]
ai = [
    # Added in Phase 4 — placeholder for now
    # "anthropic>=0.25",
    # "openai>=1.30",
]

# Entry point — makes `taskflow` a runnable command after install
[project.scripts]
taskflow = "taskflow.main:main"

[project.urls]
Homepage   = "https://github.com/udit/taskflow"
Repository = "https://github.com/udit/taskflow"


# ── Tool Configuration ────────────────────────────────────

[tool.setuptools.packages.find]
where = ["."]
include = ["taskflow*"]

# Black — code formatter
[tool.black]
line-length    = 88
target-version = ["py314"]

# Ruff — fast linter (replaces flake8, isort, and more)
[tool.ruff]
line-length = 88
target-version = "py314"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort (import sorting)
    "B",   # flake8-bugbear
    "UP",  # pyupgrade — modern Python idioms
]
ignore = [
    "E501",  # line too long — handled by black
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # allow assert in tests

# Mypy — static type checker
[tool.mypy]
python_version         = "3.14"
strict                 = false
warn_return_any        = true
warn_unused_configs    = true
ignore_missing_imports = true

# Pytest — test runner
[tool.pytest.ini_options]
testpaths    = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts      = "-v --tb=short"

# Coverage
[tool.coverage.run]
source = ["taskflow"]
omit   = ["tests/*", "run.py"]

[tool.coverage.report]
show_missing = true
skip_covered = false
```

---

### `.gitignore` — What Never Goes Into Version Control

Create `.gitignore` in the project root:

```gitignore
# .gitignore
# TaskFlow AI

# ── Virtual environments ──────────────────────────────────
.venv/
venv/
env/
ENV/

# ── Python cache ──────────────────────────────────────────
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# ── Distribution / packaging ──────────────────────────────
build/
dist/
*.egg-info/
*.egg
MANIFEST

# ── Testing ───────────────────────────────────────────────
.pytest_cache/
.coverage
htmlcov/
.tox/

# ── Type checking ─────────────────────────────────────────
.mypy_cache/
.dmypy.json
dmypy.json

# ── IDE and editors ───────────────────────────────────────
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# ── OS files ──────────────────────────────────────────────
.DS_Store
Thumbs.db

# ── Application data ──────────────────────────────────────
data/
*.tmp
taskflow_tasks*.json
taskflow_backup_*.json

# ── Secrets ───────────────────────────────────────────────
.env
.env.local
.env.*.local
secrets.py

# ── Logs ──────────────────────────────────────────────────
*.log
logs/
```

---

### Checking for Outdated and Vulnerable Packages

```bash
# List outdated packages
pip list --outdated

# Check for known security vulnerabilities
pip install pip-audit
pip-audit

# With uv
uv pip list --outdated

# Check a specific package
pip show requests   # shows version, location, dependencies
```

Add vulnerability checking to your CI pipeline (Day 57) so every commit is scanned automatically.

---

### The Complete Project File Structure

After Day 18, the full project layout looks like this:

```
taskflow/                    ← root of the repository
│
├── taskflow/                ← Python package
│   ├── __init__.py
│   ├── main.py
│   ├── shell.py
│   ├── cli.py
│   ├── parser.py
│   ├── config.py
│   ├── errors.py
│   ├── decorators.py
│   ├── context.py
│   ├── filters.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── task_types.py
│   │   ├── task_factory.py
│   │   └── stats.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── json_store.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   └── weather.py
│   └── display/
│       ├── __init__.py
│       └── renderer.py
│
├── tests/                   ← test suite (Day 25)
│   └── __init__.py
│
├── data/                    ← runtime data (git-ignored)
│   └── taskflow_tasks.json
│
├── run.py                   ← project entry point
├── pyproject.toml           ← project config and metadata
├── requirements.in          ← direct production deps (hand-written)
├── requirements.txt         ← pinned production deps (generated)
├── requirements-dev.in      ← direct dev deps (hand-written)
├── requirements-dev.txt     ← pinned dev deps (generated)
├── .gitignore
├── .env.example             ← template for environment variables
├── README.md
└── CHANGELOG.md
```

---

### Developer Onboarding Script

Create `scripts/setup.sh` to make onboarding one command:

```bash
#!/usr/bin/env bash
# scripts/setup.sh
# TaskFlow AI — developer environment setup
# Usage: bash scripts/setup.sh

set -e   # exit immediately on any error

echo "TaskFlow AI — Developer Setup"
echo "=============================="

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python -m venv .venv

# Activate
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip --quiet

# Install all dependencies
echo "Installing dependencies..."
pip install -e ".[dev]" --quiet

echo ""
echo "Setup complete!"
echo "Activate with: source .venv/bin/activate"
echo "Run with:      python run.py"
```

Make it executable:

```bash
chmod +x scripts/setup.sh
```

---

## Exercises

**Exercise 1 — Environment comparison.**
Create two separate virtual environments: `.venv-a` and `.venv-b`. Install `requests==2.28.0` in one and `requests==2.31.0` in the other. Activate each and run:

```python
import requests; print(requests.__version__)
```

Verify they are completely independent. Then inspect the folder sizes with `du -sh .venv-a .venv-b`.

**Exercise 2 — `pip freeze` vs `pip-compile`.**
In your active `.venv`, run `pip freeze > requirements-frozen.txt`. Then create `requirements.in` with only `requests>=2.28`. Run `pip-compile requirements.in -o requirements-compiled.txt`. Compare the two files. How many packages appear in `frozen` that are NOT in `compiled`? Why?

**Exercise 3 — Full `uv` workflow.**
Delete your `.venv`. Recreate it entirely using `uv`:

```bash
uv venv
uv pip install -e ".[dev]"
python run.py
```

Time the full install. Compare to `pip install -r requirements-dev.txt`. Record both times.

**Exercise 4 — `pyproject.toml` entry point.**
After adding the `[project.scripts]` entry in `pyproject.toml`, install the package in editable mode:

```bash
pip install -e .
```

Now run `taskflow` as a global command (without `python run.py`). Inspect where the `taskflow` script lives:

```bash
which taskflow        # Linux/macOS
where taskflow        # Windows
cat $(which taskflow) # read the generated script
```

**Exercise 5 — Security audit.**
Install `pip-audit` and run it against your virtual environment:

```bash
pip install pip-audit
pip-audit
```

If any vulnerabilities are found, identify the affected package and note the fixed version. Update `requirements.in` and recompile. If no vulnerabilities are found, deliberately install a vulnerable version of `requests` (e.g., `pip install requests==2.18.0`) and run `pip-audit` again.

**Exercise 6 (stretch) — `pre-commit` hooks.**
Install and configure `pre-commit` to run `black`, `ruff`, and `mypy` automatically before every commit:

Create `.pre-commit-config.yaml`:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        language_version: python3.14

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.7
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

Install the hooks:

```bash
pre-commit install
```

Make a deliberate style violation (extra space, unsorted import) and try to commit. Watch `pre-commit` catch and fix it automatically.

---

## Checkpoint

Before moving to Day 19:

- [ ] I understand why virtual environments exist — the dependency isolation problem
- [ ] I can create, activate, and deactivate a virtual environment with `venv`
- [ ] I always activate my venv before running `pip install`
- [ ] I maintain `requirements.in` (hand-written) and `requirements.txt` (generated)
- [ ] I separate production and development dependencies
- [ ] I have installed `uv` and can use it instead of `pip` + `venv`
- [ ] `pyproject.toml` is created with metadata, dependencies, and tool config
- [ ] `.gitignore` excludes `.venv/`, `data/`, `.env`, and all cache files
- [ ] `pip install -e .` works and `taskflow` is available as a command
- [ ] `pip-audit` shows no known vulnerabilities in my environment

---

## Common Errors on Day 18

**Installing without activating the venv — packages go to global Python:**

```bash
pip install requests   # ❌ installs globally if venv not active
source .venv/bin/activate
pip install requests   # ✅ installs into venv
```

Check: `which pip` should show `.venv/bin/pip`, not a system path.

**`ModuleNotFoundError` after activating a different terminal:**

Virtual environment activation is per-shell-session. Opening a new terminal resets to global Python. Always run `source .venv/bin/activate` at the start of each session, or configure your IDE to auto-activate.

**Committing `.venv/` to git — the repository bloats massively:**

The `.venv/` folder can be hundreds of megabytes. Always include it in `.gitignore`. Commit `requirements.txt` instead — anyone can recreate the environment from that.

**Committing `.env` to git — secrets exposed:**

Never commit `.env` files. Commit `.env.example` (a template with fake values) and add `.env` to `.gitignore`. We cover this properly on Day 24.

**`pip freeze` capturing test dependencies in production `requirements.txt`:**

Only run `pip freeze` after a clean install of production dependencies. Better: use `pip-compile` with separate `.in` files for production and development. This is why the two-file pattern exists.

---

## What's Coming

On **Day 19** we go deep on Git and version control — branching strategies, commits that tell a story, pull requests, merge conflicts, and the git workflow used by professional engineering teams. TaskFlow AI gets a proper git history, a `CONTRIBUTING.md`, and its first feature branch. This is the last day before the Phase 1 retrospective milestone on Day 20.