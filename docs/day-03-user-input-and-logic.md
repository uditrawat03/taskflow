# Day 03 — User Input & Logic

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Building the smart greeting & onboarding flow

---

## Learning Objective

By the end of today, you will make TaskFlow AI interactive. Instead of hardcoded values, the app will ask the user questions and respond differently based on their answers. You will understand `input()`, `if/elif/else`, comparison operators, and logical operators — the building blocks of every decision your program will ever make.

---

## What We Build Today

An `onboarding.py` script — the entry point of TaskFlow AI — that greets users by name, asks them a few setup questions, and responds intelligently based on their answers.

```
========================================
   Welcome to TaskFlow AI v0.1.0
========================================

What is your name? Udit Rawat
How old are you? 24
Are you a developer? (yes/no): yes
Choose your plan — free or premium: premium

----------------------------------------
Hey Udit! Great to have you onboard.
You are 24 years old.
Role detected   : Developer
Plan selected   : Premium (100 tasks max)
Tip             : Premium users get AI-powered task analysis. 
                  We'll build that in Phase 4!

Your TaskFlow AI journey starts now.
----------------------------------------
```

---

## Concepts Covered

- `input()` — reading user input from the terminal
- Type conversion of input values (`int()`, `float()`)
- `if / elif / else` — conditional branching
- Comparison operators — `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical operators — `and`, `or`, `not`
- Nested conditions
- Truthy/falsy input checks
- Defensive input handling — `.strip().lower()`
- `in` operator for membership testing
- Python 3.14: cleaner `match` statement (structural pattern matching)

---

## Full Tutorial

### How Programs Make Decisions

Every useful program makes decisions. "If the user is premium, show AI features. If the task is overdue, mark it red. If the password is wrong, show an error." Decision-making in Python is built around one core structure: the `if` statement.

Before we get there, we need to understand how the program gets information from the user in the first place.

---

### `input()` — Talking to the User

The `input()` function pauses the program, displays a message, waits for the user to type something and press Enter, then returns what they typed as a **string**.

```python
name = input("What is your name? ")
print(f"Hello, {name}!")
```

Run this. The terminal waits. You type. The program continues.

**Critical rule: `input()` always returns a string.** Always. Even if the user types `24`, Python gives you the string `"24"`, not the integer `24`. This is one of the most common sources of bugs for beginners.

```python
age = input("How old are you? ")
print(type(age))   # <class 'str'> — NOT int

# This will crash:
next_year = age + 1   # TypeError: can only concatenate str (not "int") to str

# Correct approach — convert immediately after input:
age = int(input("How old are you? "))
print(type(age))   # <class 'int'>
next_year = age + 1   # works perfectly
```

The pattern `int(input("..."))` wraps `input()` inside `int()` so the conversion happens in one line. You will write this pattern hundreds of times.

---

### Cleaning Input — Always

Users are unpredictable. They add extra spaces, use random capitalization, type "YES" instead of "yes." Always clean input before using it:

```python
raw = input("Are you a developer? (yes/no): ")

# raw might be "  YES  " or "Yes" or "y " — normalize it
answer = raw.strip().lower()

# Now 'answer' is always a clean lowercase string with no surrounding spaces
print(answer)   # "yes"
```

`.strip()` removes leading and trailing whitespace. `.lower()` converts to lowercase. Chain them immediately on every text input. This habit will save you from countless bugs across your entire career.

---

### `if / elif / else` — Making Decisions

The `if` statement lets your program take different paths based on a condition.

**Basic structure:**

```python
if condition:
    # runs if condition is True
elif another_condition:
    # runs if first condition was False AND this is True
else:
    # runs if ALL conditions above were False
```

**Indentation is not optional.** Python uses indentation (4 spaces, or one Tab key) to define which lines belong inside an `if` block. This is one of Python's most distinctive features — get it wrong and you get an `IndentationError`.

```python
age = 24

if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teenager")
else:
    print("Child")
```

You can have as many `elif` branches as you need. `else` is always last and is optional. Only one branch ever runs — the first one whose condition is `True`.

---

### Comparison Operators

These operators compare two values and return `True` or `False`:

```python
x = 10
y = 20

print(x == y)   # False — equal to
print(x != y)   # True  — not equal to
print(x < y)    # True  — less than
print(x > y)    # False — greater than
print(x <= y)   # True  — less than or equal to
print(x >= y)   # False — greater than or equal to
```

**String comparison works too:**

```python
plan = "premium"

print(plan == "premium")   # True
print(plan == "free")      # False
print(plan != "free")      # True
```

---

### Logical Operators — `and`, `or`, `not`

Logical operators combine multiple conditions into one:

**`and`** — both conditions must be True:

```python
age = 24
is_verified = True

if age >= 18 and is_verified:
    print("Access granted")
```

**`or`** — at least one condition must be True:

```python
plan = "premium"

if plan == "premium" or plan == "enterprise":
    print("Advanced features unlocked")
```

**`not`** — flips True to False and vice versa:

```python
is_guest = False

if not is_guest:
    print("Welcome back, registered user!")
```

**Combining them:**

```python
age = 24
plan = "free"
is_developer = True

if (age >= 18 and is_developer) or plan == "premium":
    print("AI features available")
```

Use parentheses to make the logic explicit and readable. Don't rely on operator precedence — clarity always wins.

---

### The `in` Operator — Membership Testing

The `in` operator checks whether a value exists inside a collection. It reads almost like English:

```python
valid_plans = ["free", "premium", "enterprise"]
user_plan = "premium"

if user_plan in valid_plans:
    print("Valid plan selected")
else:
    print("Unknown plan — defaulting to free")
```

For strings, `in` checks for substrings:

```python
email = "udit@example.com"

if "@" in email and "." in email:
    print("Email looks valid")
else:
    print("Invalid email format")
```

You will use `in` constantly throughout this series.

---

### Nested Conditions

Conditions can be nested inside other conditions. Use this carefully — deep nesting becomes hard to read:

```python
plan = "premium"
is_active = True

if is_active:
    if plan == "premium":
        print("Premium features active")
    else:
        print("Free features active")
else:
    print("Account inactive — please reactivate")
```

A flat `and` is often cleaner than nested `if`:

```python
if is_active and plan == "premium":
    print("Premium features active")
elif is_active:
    print("Free features active")
else:
    print("Account inactive — please reactivate")
```

**Rule of thumb:** if your `if` block is more than 2 levels deep, step back and think about restructuring. Flat is better than nested — a Python philosophy you will hear repeatedly.

---

### Python 3.14: `match` Statement — Structural Pattern Matching

Python 3.10 introduced the `match` statement (similar to `switch` in other languages), and Python 3.14 has refined it further. It is clean and readable for handling multiple fixed options:

```python
plan = "premium"

match plan:
    case "free":
        max_tasks = 10
        ai_features = False
    case "premium":
        max_tasks = 100
        ai_features = True
    case "enterprise":
        max_tasks = 10000
        ai_features = True
    case _:
        print("Unknown plan — defaulting to free")
        max_tasks = 10
        ai_features = False

print(f"Max tasks: {max_tasks}, AI: {ai_features}")
```

`case _:` is the default — it matches anything not caught above (equivalent to `else`). We will use `match` statements more in Phase 2 when building the CLI interface. For now, `if/elif/else` is the foundation to master.

---

### Building `onboarding.py`

Create `onboarding.py` inside your `taskflow` folder:

```python
# onboarding.py
# TaskFlow AI — Day 03
# Onboarding flow: greets the user, collects setup info, responds intelligently.

# --- Constants ---
APP_NAME = "TaskFlow AI"
VERSION = "0.1.0"
MAX_TASKS_FREE = 10
MAX_TASKS_PREMIUM = 100
VALID_PLANS = ["free", "premium"]

# --- Header ---
print("=" * 40)
print(f"   Welcome to {APP_NAME} v{VERSION}")
print("=" * 40)
print()

# --- Collect Name ---
raw_name = input("What is your name? ")
name = raw_name.strip().title()      # clean and title-case
first_name = name.split()[0]         # extract first name

if not name:
    name = "Friend"
    first_name = "Friend"

# --- Collect Age ---
raw_age = input("How old are you? ").strip()

if raw_age.isdigit():
    age = int(raw_age)
else:
    print("Invalid age entered — setting to 0.")
    age = 0

# --- Collect Role ---
raw_role = input("Are you a developer? (yes/no): ").strip().lower()

if raw_role in ["yes", "y"]:
    is_developer = True
    role = "Developer"
elif raw_role in ["no", "n"]:
    is_developer = False
    role = "General User"
else:
    is_developer = False
    role = "Unknown"
    print("Unrecognized input — defaulting to General User.")

# --- Collect Plan ---
raw_plan = input("Choose your plan — free or premium: ").strip().lower()

if raw_plan in VALID_PLANS:
    plan = raw_plan
else:
    print("Unrecognized plan — defaulting to free.")
    plan = "free"

# --- Derive Settings from Input ---
if plan == "premium":
    max_tasks = MAX_TASKS_PREMIUM
    plan_label = "Premium (100 tasks max)"
    ai_tip = "Premium users get AI-powered task analysis. We'll build that in Phase 4!"
else:
    max_tasks = MAX_TASKS_FREE
    plan_label = "Free (10 tasks max)"
    ai_tip = "Upgrade to Premium to unlock AI features. Type 'upgrade' anytime."

# --- Age-based message ---
if age < 18:
    age_note = "Young builder — impressive!"
elif age < 30:
    age_note = "Prime building years."
elif age < 50:
    age_note = "Experience + code = power."
else:
    age_note = "Wisdom-driven engineering."

# --- Developer-specific message ---
if is_developer:
    dev_note = "Dev mode: you will see extra technical details throughout."
else:
    dev_note = "No coding experience needed — we start from absolute zero."

# --- Summary Output ---
print()
print("-" * 40)
print(f"Hey {first_name}! Great to have you onboard.")
print(f"You are {age} years old. {age_note}")
print()
print(f"{'Role detected':<16}: {role}")
print(f"{'Plan selected':<16}: {plan_label}")
print(f"{'Max tasks':<16}: {max_tasks}")
print()
print(f"Tip: {ai_tip}")
print()
print(dev_note)
print()
print("Your TaskFlow AI journey starts now.")
print("-" * 40)
```

Run it:

```bash
python onboarding.py
```

Try running it multiple times with different inputs — a developer on premium, a non-developer on free, an invalid age, an unrecognized plan. Watch how the output changes each time. This is your first interactive, branching program.

---

### Understanding Key Lines

**`raw_age.isdigit()`**

Before calling `int()` on a string, it is safer to check if the string actually contains only digits. `.isdigit()` returns `True` if every character is a digit — `"24"` → `True`, `"abc"` → `False`, `"24.5"` → `False` (the dot is not a digit). This prevents a `ValueError` crash if the user types something unexpected.

```python
"24".isdigit()     # True
"abc".isdigit()    # False
"24.5".isdigit()   # False — use float() for decimals
```

**`if not name:`**

Because an empty string is falsy, `if not name:` is True when the user just presses Enter without typing anything. This is a defensive check — real apps must always handle empty input gracefully.

**`raw_role in ["yes", "y"]`**

Instead of `if raw_role == "yes" or raw_role == "y":`, the `in` operator checks membership in a list. Clean, readable, and easy to extend — just add `"yeah"` or `"yep"` to the list without touching the condition logic.

---

## Exercises

**Exercise 1 — Try to break it.**
Run `onboarding.py` and try entering: an empty name, letters instead of age, `"maybe"` for the developer question, `"enterprise"` as the plan. Does the app handle all of these gracefully? Fix any case that crashes or produces wrong output.

**Exercise 2 — Add a new question.**
Add an `experience_years` question: ask how many years of coding experience the user has. Accept `0` for complete beginners. Use it to customize one more line in the summary output:
- 0 years: `"Perfect starting point — we build everything from scratch."`
- 1–2 years: `"Some experience — we will move at a good pace."`
- 3+ years: `"Solid background — you will pick this up very fast."`

**Exercise 3 — Email validation.**
Add an email input. Check that it contains `@` and `.` using the `in` operator. If invalid, print a warning but continue (don't crash). Display the cleaned (lowercased, stripped) email in the summary.

**Exercise 4 — Logical operators practice.**
Add a condition that prints a special message only if the user is a developer AND on the premium plan. Add another for non-developers on free. Cover all four combinations (`dev+premium`, `dev+free`, `non-dev+premium`, `non-dev+free`) with different messages.

**Exercise 5 — Rewrite with `match`.**
Take the plan selection block and rewrite it using a `match` statement instead of `if/elif/else`. Add a third case: `"enterprise"` with `max_tasks = 10000`. Confirm the output is identical to the original.

**Exercise 6 (stretch) — Input loop.**
Right now, if the user enters an invalid plan, the app silently defaults to free. Instead, keep asking until they enter a valid plan. You don't know loops yet (that's Day 04), but try to reason about how you would repeat a question. Write your best attempt, even if it's repetitive. We will fix it elegantly tomorrow.

---

## Checkpoint

Before moving to Day 04:

- [ ] I understand that `input()` always returns a string
- [ ] I always `.strip().lower()` text input before using it
- [ ] I can write `if / elif / else` blocks with correct indentation
- [ ] I know all six comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
- [ ] I can combine conditions with `and`, `or`, `not`
- [ ] I use `in` to check membership in a list or substring in a string
- [ ] I use `.isdigit()` before converting input to `int()`
- [ ] I handle empty input gracefully with `if not value:`
- [ ] `onboarding.py` runs correctly for all inputs — valid and invalid

---

## Common Errors on Day 03

**`IndentationError: expected an indented block`**

```python
if age >= 18:
print("Adult")   # ❌ not indented — Python expects 4 spaces here
```

```python
if age >= 18:
    print("Adult")   # ✅ 4 spaces inside the if block
```

**`ValueError: invalid literal for int() with base 10: 'abc'`**

```python
age = int(input("Age: "))   # user types "abc" → crashes
```

Fix: use `.isdigit()` before converting, or use `try/except` (coming on Day 10):

```python
raw = input("Age: ").strip()
age = int(raw) if raw.isdigit() else 0
```

**`SyntaxError: invalid syntax` on `elif` or `else`**

This often means the `if` block above it is empty or has a syntax error:

```python
if age >= 18:
    # TODO: add something here
elif age >= 13:   # ❌ SyntaxError if the if block is empty
```

Fix: use `pass` as a placeholder in empty blocks:

```python
if age >= 18:
    pass   # ✅ valid empty block
elif age >= 13:
    print("Teenager")
```

**Using `=` instead of `==` inside a condition:**

```python
if plan = "premium":   # ❌ SyntaxError — this is assignment, not comparison
if plan == "premium":  # ✅ correct
```

Python 3.14 gives a clear error here pointing to the exact character that caused the problem.

**Forgetting that `input()` returns a string:**

```python
age = input("Age: ")
if age > 17:           # ❌ TypeError: '>' not supported between 'str' and 'int'
    print("Adult")

age = int(input("Age: "))
if age > 17:           # ✅ now age is an int, comparison works
    print("Adult")
```

---

## What's Coming

On **Day 04** we introduce lists and loops. Exercise 6 above — the "keep asking until valid" problem — will be trivially solvable with a `while` loop. We will also upgrade the `onboarding.py` to loop until the user provides valid input, and build the first version of the task list that will become the heart of TaskFlow AI.
