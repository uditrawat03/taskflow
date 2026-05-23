# Day 19 — Git & Version Control

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Professional git workflow with branches and history

---

## Learning Objective

By the end of today, you will use git the way professional engineering teams use it — not just `add`, `commit`, `push`, but branching strategies, atomic commits, meaningful messages, pull request workflows, merge conflict resolution, and a clean history that tells the story of your project. TaskFlow AI gets a proper git history rewritten with semantic commits, a `CONTRIBUTING.md`, and its first feature branch.

---

## What We Build Today

A professional git workflow for TaskFlow AI — clean history, a feature branch, a simulated pull request merge, and a `CONTRIBUTING.md` that explains how to contribute to the project.

```bash
# The history we are building:
git log --oneline

a3f9c12 (HEAD -> main) docs: add CONTRIBUTING.md and developer guide
7b2e841 feat: add TaskFilter fluent pipeline (Day 16)
4d1e923 feat: add decorators and context managers (Day 17)
2c8f710 feat: add virtual environment and pyproject.toml setup (Day 18)
1a7b305 refactor: restructure into taskflow package (Day 11)
9f3d218 feat: release TaskFlow AI v1.0.0 (Day 15)
...
```

---

## Concepts Covered

- Git internals — the three areas (working tree, staging area, repository)
- `git init`, `git clone`, `git status`, `git diff`
- `git add` — staging selectively with `-p`
- `git commit` — atomic commits and conventional commit messages
- `git log` — reading history (`--oneline`, `--graph`, `--all`)
- `git branch` — creating and switching branches
- `git merge` — fast-forward and three-way merges
- `git rebase` — keeping a linear history
- Merge conflict resolution
- `git stash` — temporary shelving of work
- `git tag` — marking releases
- `git remote` — working with GitHub
- `.gitignore` revisited
- The GitHub pull request workflow
- `git bisect` — finding the commit that introduced a bug
- Conventional Commits specification

---

## Full Tutorial

### Git's Three Areas

Understanding these three areas eliminates most git confusion:

```
Working Tree          Staging Area          Repository
(your files)          (index / cache)       (.git/objects)
     │                      │                     │
     │   git add file       │   git commit        │
     │─▶│▶│
     │                      │                     │
     │◀─│◀│
     │   git checkout       │   git reset HEAD    │
```

- **Working tree** — the files you see and edit
- **Staging area** — changes you have decided to include in the next commit
- **Repository** — the permanent history of all commits

`git add` moves changes from working tree → staging.
`git commit` moves staged changes → repository.
`git status` shows the state of all three areas.

---

### Initialising and the First Commit

```bash
# Initialise a new repository
cd taskflow-project
git init

# Check current state
git status

# Stage everything
git add .

# First commit
git commit -m "chore: initial project structure"

# Connect to GitHub (create the repo on GitHub first)
git remote add origin https://github.com/uditrawat03/taskflow.git
git branch -M main
git push -u origin main
```

---

### Atomic Commits — One Logical Change Per Commit

An **atomic commit** contains exactly one logical change. If you can describe it in a single sentence without "and", it is probably atomic.

```bash
# ❌ Not atomic — too many unrelated changes
git commit -m "fix bug, add feature, update README, refactor storage"

# ✅ Atomic — one clear purpose each
git commit -m "fix: prevent crash when storage file is empty"
git commit -m "feat: add TaskFilter fluent pipeline"
git commit -m "docs: update README with shorthand syntax examples"
git commit -m "refactor: extract task validation into make_task()"
```

Atomic commits make it easy to:
- Understand what changed and why
- Revert a specific change without affecting others
- Find bugs with `git bisect`
- Review code in pull requests

---

### Conventional Commits — A Standard Message Format

The **Conventional Commits** specification gives commit messages a consistent structure:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

| Type | When to use |
|------|------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, whitespace (no logic change) |
| `refactor` | Code restructure with no feature or fix |
| `test` | Adding or fixing tests |
| `chore` | Build process, dependencies, tooling |
| `perf` | Performance improvements |
| `ci` | CI/CD configuration changes |

**Examples:**

```bash
git commit -m "feat(parser): add support for ~weekly recurring tasks"
git commit -m "fix(storage): handle JSONDecodeError when file is corrupted"
git commit -m "refactor(core): replace task dicts with Task class"
git commit -m "docs: add CONTRIBUTING.md with branch naming convention"
git commit -m "chore(deps): upgrade requests to 2.31.0"
git commit -m "test(storage): add round-trip JSON serialisation tests"
```

The **scope** (in parentheses) is optional but useful — it names the module or feature area affected.

---

### Branching Strategy — GitHub Flow

**GitHub Flow** is the simplest effective branching strategy:

```
main ●●► (always deployable)
        \                        /
         ●●●  feature/x  ●   (short-lived feature branches)
```

Rules:
1. `main` is always deployable — only working, reviewed code lands here
2. All new work happens on a feature branch
3. Feature branches are short-lived (hours to days, not weeks)
4. Merge via pull request — code is reviewed before landing on `main`
5. Delete feature branches after merging

```bash
# Start a feature branch
git checkout -b feature/add-task-tags

# Work, commit atomically
git add taskflow/core/task.py
git commit -m "feat(core): add tags attribute to Task class"

git add tests/test_task.py
git commit -m "test(core): add tests for Task.tags"

# Push the branch
git push -u origin feature/add-task-tags

# Open a pull request on GitHub, get review, merge
# Then delete the branch
git checkout main
git pull origin main
git branch -d feature/add-task-tags
```

---

### `git add -p` — Staging Selectively

`git add -p` (patch mode) lets you stage individual hunks of a file — not the whole file. This is essential for atomic commits when you have changed multiple things in one file:

```bash
git add -p taskflow/core/task.py
# Git shows each changed section and asks: stage this hunk? (y/n/s/q/?)
# y = yes, stage it
# n = no, skip it
# s = split into smaller hunks
# q = quit
# ? = help
```

Use `git add -p` every time you commit. It forces you to review every change before it goes in, which catches bugs early and keeps commits atomic.

---

### `git log` — Reading History

```bash
# Simple one-line view
git log --oneline

# With branch graph
git log --oneline --graph --all

# Full detail for one commit
git show a3f9c12

# History of a specific file
git log --oneline taskflow/core/task.py

# Search commit messages
git log --oneline --grep="feat"

# Commits between two tags
git log --oneline v0.1.0..v1.0.0

# Who changed what line (blame)
git blame taskflow/storage/json_store.py
```

---

### Merge vs Rebase

**Merge** — creates a merge commit that preserves the full branch history:

```
main:    ABM
              \       /
feature:       CDE
```

**Rebase** — replays feature commits on top of main, giving a linear history:

```
main:    ABC'D'E'
```

Use **merge** for long-lived branches (feature is different enough to deserve its own story). Use **rebase** for short-lived branches to keep `main` history clean and linear.

```bash
# Merge (from main)
git merge feature/add-task-tags

# Rebase (from feature branch)
git rebase main

# Interactive rebase — squash, reorder, reword commits
git rebase -i HEAD~3   # edit last 3 commits
```

---

### Resolving Merge Conflicts

A merge conflict occurs when two branches modify the same lines differently:

```bash
git merge feature/add-task-tags
# CONFLICT (content): Merge conflict in taskflow/core/task.py
# Automatic merge failed; fix conflicts and then commit the result.
```

Open the conflicted file — Git marks the conflict:

```python
<<<<<<< HEAD
    def is_overdue(self, threshold_days: int = 7) -> bool:
=======
    def is_overdue(self, threshold_days: int = 3) -> bool:
>>>>>>> feature/add-task-tags
```

`<<<<<<< HEAD` — your version (current branch)
`=======` — separator
`>>>>>>> feature/...` — incoming version

Edit to keep what you want, remove the markers, then:

```bash
git add taskflow/core/task.py
git commit -m "merge: resolve threshold_days conflict in is_overdue()"
```

VS Code has a built-in merge conflict editor — click "Accept Current", "Accept Incoming", or "Accept Both" instead of editing markers manually.

---

### `git stash` — Shelving Work Temporarily

```bash
# You are mid-feature when an urgent fix is needed on main

# Stash current work
git stash push -m "WIP: adding task tags"

# Switch to main, fix the bug
git checkout main
git checkout -b fix/storage-crash
# ... fix, commit, PR, merge ...
git checkout feature/add-task-tags

# Restore stashed work
git stash pop

# View all stashes
git stash list

# Apply a specific stash without removing it
git stash apply stash@{0}
```

---

### `git bisect` — Finding the Bug-Introducing Commit

```bash
# Start bisect
git bisect start

# Mark the current (broken) commit as bad
git bisect bad

# Mark a known-good commit (e.g., the v1.0.0 release)
git bisect good v1.0.0

# Git checks out a commit halfway between — test it
python run.py   # does the bug exist?

git bisect good   # no bug here — git moves forward
git bisect bad    # bug exists — git moves backward

# Git narrows down until it finds the exact commit
# a3f9c12 is the first bad commit
git bisect reset  # return to HEAD when done
```

`git bisect` performs a binary search through your commit history. With 100 commits between good and bad, it finds the culprit in 7 checks. This is why atomic commits matter — bisect can only tell you which commit introduced the bug, not which line inside a 500-line "big refactor" commit.

---

### Writing `CONTRIBUTING.md`

```markdown
# Contributing to TaskFlow AI

Thank you for considering a contribution to TaskFlow AI!
This guide explains how to set up your environment and submit changes.

## Development Setup

```bash
git clone https://github.com/uditrawat03/taskflow.git
cd taskflow
uv venv && uv pip install -e ".[dev]"
pre-commit install
python run.py   # verify it runs
```

## Branch Naming

```
feature/<short-description>   feat(scope): ...
fix/<short-description>        fix(scope): ...
docs/<short-description>       docs: ...
refactor/<short-description>   refactor(scope): ...
```

Examples:
- `feature/recurring-task-support`
- `fix/storage-atomic-write`
- `docs/update-readme-shorthand`

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) spec:

```
<type>(<scope>): <short description>

[optional body — explain WHY, not what]

[optional footer — breaking changes, issue references]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`

## Pull Request Checklist

Before opening a PR:
- [ ] All tests pass: `pytest`
- [ ] No linting errors: `ruff check .`
- [ ] Code formatted: `black .`
- [ ] Type hints on all new functions: `mypy taskflow/`
- [ ] Docstrings on all new public functions
- [ ] `CHANGELOG.md` updated
- [ ] Relevant tests added for new features

## Code Style

- Line length: 88 (Black default)
- Type hints: required on all public function signatures
- Docstrings: Google style
- Imports: sorted by `ruff` (isort-compatible)

## Testing

```bash
pytest                        # run all tests
pytest tests/test_task.py     # specific file
pytest -k "test_mark_done"    # specific test
pytest --cov=taskflow         # with coverage
```

## Questions?

Open an issue on GitHub or start a discussion.
```

---

### Tagging the Current State

```bash
# After Day 18 — tag the state before Phase 2 ends
git tag -a v1.1.0-dev -m "Phase 2 in progress — Days 16-18 complete"

# List tags
git tag -l

# Push tags
git push origin --tags

# Checkout a specific tag (read-only)
git checkout v1.0.0
git checkout main   # return
```

---

## Exercises

**Exercise 1 — Rewrite history with atomic commits.**
Run `git log --oneline` and look at your history. If you have lumped multiple changes into one commit, use `git rebase -i` to split or reword them. Aim for a history where every commit message describes exactly one thing.

**Exercise 2 — Feature branch workflow.**
Create a branch `feature/task-tags`, add a `tags: set[str]` attribute to the `Task` class, update `to_dict()` and `from_dict()`, and commit atomically (one commit for the model change, one for serialisation). Open a simulated "PR" by pushing and inspecting the diff on GitHub.

**Exercise 3 — Merge conflict simulation.**
Create two branches from the same commit. In branch A, change `OVERDUE_THRESHOLD_DAYS = 7` to `5`. In branch B, change it to `10`. Merge branch A into main, then merge branch B — resolve the conflict and explain in the merge commit message which value you chose and why.

**Exercise 4 — `git bisect` practice.**
Introduce a deliberate bug in `calculate_stats()` (e.g., `total - done - 1`). Make 5 more commits on top. Use `git bisect` to find the exact commit that broke it. Reset. How many checks did bisect need?

**Exercise 5 — `git stash` workflow.**
Start implementing a new feature (any small change). Stash it. Make an unrelated fix. Commit the fix. Pop the stash. Verify your work-in-progress is restored exactly as you left it. Run `git stash list` before and after each step.

**Exercise 6 (stretch) — `pre-commit` + conventional commits.**
Install the `commitizen` tool and configure it to enforce conventional commit messages:

```bash
pip install commitizen
cz init   # interactive setup
cz commit # interactive commit builder
```

Try to commit with a non-conventional message and watch `commitizen` block it. Then use `cz bump` to automatically determine the next semantic version based on commit history.

---

## Checkpoint

Before moving to Day 20:

- [ ] I understand git's three areas — working tree, staging, repository
- [ ] I write atomic commits — one logical change per commit
- [ ] I follow Conventional Commits format for all messages
- [ ] I use `git add -p` to stage selectively
- [ ] I can create, work on, and merge feature branches
- [ ] I understand the difference between merge and rebase
- [ ] I can resolve merge conflicts in VS Code
- [ ] I have used `git stash` to shelve and restore work
- [ ] I know how to use `git bisect` to find regressions
- [ ] `CONTRIBUTING.md` is written and committed
- [ ] TaskFlow AI repository has a clean, readable commit history

---

## Common Errors on Day 19

**Committing secrets:**

```bash
git add .env   # ❌ exposes API keys!
```

If you accidentally commit a secret: immediately rotate the key (it is compromised), then remove it from history with `git filter-repo` (never `git filter-branch`). The key was visible the moment it was pushed, even if you delete the commit.

**Force-pushing to shared branches:**

```bash
git push --force origin main   # ❌ rewrites public history — breaks teammates
git push --force-with-lease origin feature/my-branch  # ✅ safer — fails if remote has changes you haven't seen
```

Never force-push to `main`. Only force-push to your own feature branches, and only before anyone else has pulled them.

**Large commits are not atomic:**

If your commit message needs the word "and", split the commit:

```bash
git add -p   # stage only the first logical change
git commit -m "feat: add Task.tags attribute"

git add -p   # stage the second logical change
git commit -m "feat: persist tags in JSON storage"
```

**`git pull` vs `git fetch` + `git merge`:**

```bash
git pull         # fetch + merge in one step — can create surprise merge commits
git fetch        # download changes without applying
git merge origin/main  # apply them explicitly when ready
# Or:
git pull --rebase  # fetch + rebase — cleaner linear history
```

---

## What's Coming

On **Day 20** we reach the Phase 1 retrospective milestone. We will review every architectural decision made across 20 days, draw the complete system diagram, identify technical debt, and plan the Phase 2 roadmap. TaskFlow AI v1.1 ships with all the Phase 2 improvements consolidated — decorators applied, filters wired, dependencies locked, git history clean. This is the last checkpoint before Phase 2's deeper engineering topics begin.
