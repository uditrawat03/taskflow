# Day 02 — Variables & Data Types

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Building the user profile module

---

## Learning Objective

By the end of today, you will understand how Python stores different kinds of information — text, numbers, true/false values — and how to work with each type correctly. You will write the first real piece of TaskFlow AI: a user profile script that captures and displays information about the person using the app.

---

## What We Build Today

A `profile.py` script — the first module of TaskFlow AI — that stores a user's personal information, validates it, and displays a formatted summary. This file will be reused and expanded across the coming days.

```
=== TaskFlow AI — User Profile ===

Name      : Udit Rawat
Age       : 28
Email     : udit@example.com
Role      : Developer
Premium   : Yes
Tasks     : 0

Account active: True
Days until trial ends: 14
Welcome, Udit! Let's get productive.
```

---

## Concepts Covered

- The four core data types: `str`, `int`, `float`, `bool`
- `type()` — inspecting what type a value is
- Type conversion — `int()`, `float()`, `str()`, `bool()`
- String methods — `.upper()`, `.lower()`, `.strip()`, `.title()`
- String formatting — f-strings, `.format()`, alignment
- Arithmetic operators — `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Boolean logic — `True`, `False`, truthiness
- Multiple assignment and constants
- `None` — the absence of a value
- Python 3.14: improved error messages for type mistakes

---

## Full Tutorial

### Why Data Types Matter

On Day 01 you stored a name and a day number in variables. Both were different *kinds* of things — one was text, one was a number. Python needs to know the kind of data it is working with because the rules differ for each kind.

You can add two numbers together (`5 + 3 = 8`). You can join two strings together (`"Task" + "Flow" = "TaskFlow"`). But you cannot add a number to a string without converting one of them first — and Python will tell you loudly if you try.

Understanding data types is the difference between writing code that works and code that crashes in confusing ways. Today you learn the four types you will use in every Python program you ever write.

---

### The Four Core Types

Python has four fundamental data types that cover the vast majority of real-world programming needs.

#### 1. `str` — String (text)

A string is any sequence of characters. It is always wrapped in quotes.

```python
name = "Udit Rawat"
email = "udit@example.com"
role = 'Developer'           # single quotes work too
empty = ""                   # an empty string is still a string
multiline = """This is
a string that spans
multiple lines."""
```

The type of `name` is `str`. You can verify this with the built-in `type()` function:

```python
print(type(name))   # <class 'str'>
```

#### 2. `int` — Integer (whole number)

An integer is any whole number — positive, negative, or zero. No decimal point.

```python
age = 28
task_count = 0
days_in_trial = 14
year = 2025
negative = -5
```

Python integers have no size limit. You can work with numbers as large as your computer's memory allows.

#### 3. `float` — Floating-Point Number (decimal)

A float is a number with a decimal point.

```python
completion_rate = 0.75       # 75%
price_monthly = 9.99
pi = 3.14159
temperature = -2.5
```

When you divide two integers in Python 3, the result is always a float:

```python
print(10 / 3)    # 1.3333...  (float division)
print(10 // 3)   # 3          (integer division — floor)
print(10 % 3)    # 1          (modulo — remainder)
```

#### 4. `bool` — Boolean (true or false)

A boolean can only be one of two values: `True` or `False`. Note the capital letters — this matters in Python.

```python
is_premium = True
is_active = False
email_verified = True
```

Booleans are the result of comparisons:

```python
print(5 > 3)      # True
print(5 == 3)     # False  (== means "is equal to")
print(5 != 3)     # True   (!= means "is not equal to")
```

> **Common beginner mistake:** Using `=` (assignment) instead of `==` (comparison). `x = 5` stores 5 in x. `x == 5` asks "is x equal to 5?" and returns `True` or `False`.

---

### `type()` — Inspecting Types

The built-in `type()` function tells you exactly what type a value is. Use it whenever you are unsure:

```python
print(type("hello"))    # <class 'str'>
print(type(42))         # <class 'int'>
print(type(3.14))       # <class 'float'>
print(type(True))       # <class 'bool'>
print(type(None))       # <class 'NoneType'>
```

---

### `None` — The Absence of a Value

`None` is a special value in Python that means "nothing" or "no value yet." It is its own type: `NoneType`.

```python
last_login = None       # user has never logged in
profile_picture = None  # not uploaded yet
```

`None` is not the same as `0`, `""`, or `False`. It specifically means "this value does not exist yet." You will use it constantly when building real applications.

---

### Type Conversion

You can convert between types using built-in conversion functions.

```python
# String → Integer
age_text = "28"
age = int(age_text)       # 28 (now a number you can do math with)

# Integer → String
count = 7
count_text = str(count)   # "7" (now text you can join with other strings)

# String → Float
price_text = "9.99"
price = float(price_text)  # 9.99

# Integer → Boolean
print(bool(0))    # False  — zero is falsy
print(bool(1))    # True   — any non-zero number is truthy
print(bool(-5))   # True

# String → Boolean
print(bool(""))       # False — empty string is falsy
print(bool("hello"))  # True  — any non-empty string is truthy
```

**Why this matters in TaskFlow AI:** When we later read user input from the terminal or from a database, everything arrives as a string. You will need to convert it to the right type before you can use it safely.

> **Python 3.14 improvement:** If you try to use the wrong type (e.g., add a string and an integer), Python 3.14 gives you a significantly clearer error message than previous versions, pointing directly to the line and explaining what went wrong. This makes debugging much faster when you are learning.

---

### String Methods

Strings in Python come with dozens of built-in methods — functions that belong to a string object. You call them with dot notation: `string.method()`.

```python
name = "  udit rawat  "

print(name.strip())       # "udit rawat"   — removes leading/trailing spaces
print(name.strip().title())  # "Udit Rawat" — title case
print(name.upper())       # "  Udit Rawat  "
print(name.lower())       # "  udit rawat  "

email = "Udit@Example.COM"
print(email.lower())      # "udit@example.com" — always normalize emails

sentence = "taskflow is an ai-powered todo app"
print(sentence.replace("todo", "task manager"))
# "taskflow is an ai-powered task manager"

print("udit" in sentence)   # True — check if a substring exists
print(sentence.startswith("taskflow"))  # True
print(sentence.endswith("app"))         # True
print(sentence.split(" "))  # ["taskflow", "is", "an", "ai-powered", "todo", "app"]
```

Methods can be **chained** — the output of one becomes the input of the next:

```python
raw_input = "  Udit Rawat   "
clean_name = raw_input.strip().title()
print(clean_name)   # "Udit Rawat"
```

---

### String Formatting — Three Ways

You will see three approaches to string formatting in Python code. Know all three; use f-strings in this series.

```python
name = "Udit"
tasks = 7

# Method 1: Concatenation (old, avoid)
print("Hello " + name + ", you have " + str(tasks) + " tasks.")

# Method 2: .format() (works in Python 2 and 3, still used)
print("Hello {}, you have {} tasks.".format(name, tasks))
print("Hello {name}, you have {tasks} tasks.".format(name=name, tasks=tasks))

# Method 3: f-strings (Python 3.6+, preferred — use this always)
print(f"Hello {name}, you have {tasks} tasks.")

# f-strings can contain expressions, not just variables
print(f"Tasks remaining: {100 - tasks}")
print(f"Name length: {len(name)} characters")
print(f"Name uppercase: {name.upper()}")
```

**f-string alignment** — for building formatted tables in the terminal:

```python
label = "Name"
value = "Udit Rawat"

# Left-align label in a 12-char column, left-align value in a 20-char column
print(f"{label:<12}: {value:<20}")

# Right-align a number
score = 97.5
print(f"Score: {score:>8.2f}")   # right-aligned, 2 decimal places
```

---

### Arithmetic Operators

```python
a = 10
b = 3

print(a + b)    # 13   — addition
print(a - b)    # 7    — subtraction
print(a * b)    # 30   — multiplication
print(a / b)    # 3.333...  — true division (always float)
print(a // b)   # 3    — floor division (integer result)
print(a % b)    # 1    — modulo (remainder)
print(a ** b)   # 1000 — exponentiation (a to the power of b)
```

**Augmented assignment** — a shortcut for updating a variable:

```python
count = 0
count = count + 1   # long form
count += 1          # shortcut — equivalent, preferred
count -= 1
count *= 2
count //= 3
```

---

### Multiple Assignment & Constants

Python lets you assign multiple variables in one line:

```python
# Assign the same value to multiple variables
x = y = z = 0

# Assign different values to multiple variables at once (tuple unpacking)
first_name, last_name = "Udit", "Rawat"
print(first_name)   # "Udit"
print(last_name)    # "Rawat"

# Swap two variables — elegant in Python, no temp variable needed
a, b = 10, 20
a, b = b, a
print(a, b)   # 20 10
```

**Constants** — Python does not have true constants (values that cannot be changed), but the convention is to write them in `ALL_CAPS`. This tells every developer "do not modify this value":

```python
MAX_TASKS = 100
FREE_TRIAL_DAYS = 14
APP_NAME = "TaskFlow AI"
VERSION = "0.1.0"
```

---

### Truthiness — Python's Boolean Logic

Every value in Python is either truthy or falsy. You will use this constantly in conditions (Day 03):

**Falsy values** — things Python treats as `False`:
- `False`
- `None`
- `0` and `0.0`
- `""` (empty string)
- `[]` (empty list)
- `{}` (empty dict)

**Everything else is truthy.**

```python
print(bool(0))       # False
print(bool(""))      # False
print(bool(None))    # False
print(bool([]))      # False

print(bool(1))       # True
print(bool("hi"))    # True
print(bool([1,2]))   # True
```

This matters in real code. Instead of `if is_active == True:` you can write `if is_active:` — shorter and more Pythonic.

---

### Building `profile.py`

Now let's put everything together into the first real file of TaskFlow AI. Create `profile.py` inside your `taskflow` folder.

```python
# profile.py
# TaskFlow AI — Day 02
# User profile module.
# Stores and displays information about the current user.

# --- Constants ---
APP_NAME = "TaskFlow AI"
VERSION = "0.1.0"
FREE_TRIAL_DAYS = 14
MAX_TASKS_FREE = 10
MAX_TASKS_PREMIUM = 100

# --- User Profile ---
# In a real app this data would come from a database or user input.
# For now, we define it directly to practise data types.

name = "Udit Rawat"             # str
age = 28                        # int
email = "udit@example.com"      # str
role = "Developer"              # str
is_premium = True               # bool
is_active = True                # bool
task_count = 0                  # int
completion_rate = 0.0           # float  (percentage as decimal)
profile_picture = None          # NoneType — not uploaded yet

# --- Derived Values ---
# These are calculated from the base data above.

max_tasks = MAX_TASKS_PREMIUM if is_premium else MAX_TASKS_FREE
tasks_remaining = max_tasks - task_count
trial_status = "Premium" if is_premium else f"Free ({FREE_TRIAL_DAYS} days remaining)"

# --- Clean & Normalize ---
# Always normalize user-supplied text before storing or displaying it.

name_clean = name.strip().title()
email_clean = email.strip().lower()
first_name = name_clean.split()[0]      # "Udit"

# --- Display Profile ---

print("=" * 38)
print(f"  {APP_NAME} — User Profile  ")
print("=" * 38)
print()
print(f"{'Name':<14}: {name_clean}")
print(f"{'Age':<14}: {age}")
print(f"{'Email':<14}: {email_clean}")
print(f"{'Role':<14}: {role}")
print(f"{'Account':<14}: {trial_status}")
print(f"{'Tasks done':<14}: {task_count}")
print(f"{'Tasks left':<14}: {tasks_remaining}")
print(f"{'Profile pic':<14}: {'Uploaded' if profile_picture else 'Not set'}")
print()
print(f"Account active   : {is_active}")
print(f"Completion rate  : {completion_rate:.1%}")
print()
print(f"Welcome, {first_name}! Let's get productive.")
print(f"You are running {APP_NAME} v{VERSION}.")
```

Run it:

```bash
python profile.py
```

Expected output:

```
======================================
  TaskFlow AI — User Profile
======================================

Name          : Udit Rawat
Age           : 28
Email         : udit@example.com
Role          : Developer
Account       : Premium
Tasks done    : 0
Tasks left    : 100
Profile pic   : Not set

Account active   : True
Completion rate  : 0.0%

Welcome, Udit! Let's get productive.
You are running TaskFlow AI v0.1.0.
```

---

### Understanding the New Lines

A few things in `profile.py` that deserve explanation:

**The conditional expression (ternary):**

```python
max_tasks = MAX_TASKS_PREMIUM if is_premium else MAX_TASKS_FREE
```

This is a one-line `if/else`. Read it as: "use `MAX_TASKS_PREMIUM` if `is_premium` is `True`, otherwise use `MAX_TASKS_FREE`." We will cover full `if/else` blocks on Day 03 — this is a preview.

**f-string with format spec:**

```python
print(f"{'Name':<14}: {name_clean}")
```

`{label:<14}` means: insert `label` left-aligned in a field 14 characters wide. This lines up the colons perfectly regardless of label length.

```python
print(f"Completion rate  : {completion_rate:.1%}")
```

`:.1%` means: format as a percentage with 1 decimal place. `0.75` becomes `75.0%`.

**`"=" * 38`:**

Multiplying a string by an integer repeats it. `"=" * 38` produces 38 `=` characters — a quick way to draw a line in the terminal.

**`profile_picture` check:**

```python
'Uploaded' if profile_picture else 'Not set'
```

Because `None` is falsy, this evaluates to `'Not set'` when `profile_picture` is `None`. When it has a value (a URL, for example), it will evaluate to `'Uploaded'`. Clean and readable.

---

## Exercises

**Exercise 1 — Personalize the profile.**
Change `name`, `age`, `email`, and `role` to your own information. Run the script. Verify that the formatting still lines up correctly.

**Exercise 2 — Add a new field.**
Add a `country` variable (str) and a `years_experience` variable (int). Display them in the profile table using the same left-aligned format.

**Exercise 3 — Type investigation.**
Add these lines at the bottom of the script and run it. Before you run, predict what each line will print:

```python
print(type(name))
print(type(age))
print(type(is_premium))
print(type(completion_rate))
print(type(profile_picture))
print(type(max_tasks))
```

Were your predictions correct?

**Exercise 4 — Type conversion practice.**
Add the following lines and fix the broken ones. Python will raise a `TypeError` on some of them — read the error, understand why, and add the right conversion function:

```python
age_next_year = age + 1
age_message = "Next year you will be " + age_next_year + " years old."  # broken
print(age_message)

price = "9.99"
discounted = price * 0.9   # broken
print(f"Discounted price: {discounted:.2f}")
```

**Exercise 5 — String methods exploration.**
Add the following to your script and predict the output before running:

```python
test = "  Hello, TaskFlow AI!  "
print(test.strip())
print(test.strip().lower())
print(test.strip().upper())
print(test.strip().replace("Hello", "Welcome"))
print(len(test.strip()))
print(test.strip().count("l"))
print(test.strip().split(","))
```

**Exercise 6 (stretch) — Truthiness table.**
Create a truthiness investigation block. Test at least 8 different values with `bool()` — including `0`, `1`, `-1`, `""`, `"0"`, `None`, `[]`, `[0]`. Print each value alongside its boolean result. This will save you hours of confusion later.

---

## Checkpoint

Before moving to Day 03:

- [ ] I understand the difference between `str`, `int`, `float`, and `bool`
- [ ] I can use `type()` to inspect any value
- [ ] I know what `None` means and when to use it
- [ ] I can convert between types using `int()`, `float()`, `str()`, `bool()`
- [ ] I can call string methods like `.strip()`, `.lower()`, `.title()`, `.replace()`
- [ ] I understand f-string formatting including alignment specs like `:<14`
- [ ] I can use all arithmetic operators including `//`, `%`, and `**`
- [ ] I know what "truthy" and "falsy" mean
- [ ] `profile.py` runs without errors and displays a clean, formatted profile

---

## Common Errors on Day 02

**`TypeError: can only concatenate str (not "int") to str`**

```python
age = 28
print("Age: " + age)   # ❌ TypeError
print("Age: " + str(age))  # ✅ correct
print(f"Age: {age}")       # ✅ f-strings handle this automatically
```

f-strings are safer than concatenation because they call `str()` on any value automatically. This is one of many reasons to prefer them.

**`TypeError: unsupported operand type(s) for +: 'int' and 'str'`**

```python
count = "7"           # came from user input — it's a string
total = count + 3     # ❌ TypeError
total = int(count) + 3  # ✅ convert first
```

**`ValueError: invalid literal for int() with base 10: '7.5'`**

```python
int("7.5")        # ❌ ValueError — can't convert decimal string directly to int
int(float("7.5")) # ✅ convert to float first, then to int → 7
```

**`AttributeError: 'int' object has no attribute 'upper'`**

```python
age = 28
age.upper()   # ❌ integers don't have string methods
str(age).upper()  # ✅ convert to string first → "28"
```

**Forgetting `==` vs `=`:**

```python
is_premium = True          # assignment — stores True in the variable
if is_premium == True:     # comparison — works, but verbose
if is_premium:             # Pythonic — preferred
```

---

## Python 3.14 Spotlight: Better Type Error Messages

One of the quality-of-life improvements in Python 3.14 is significantly more helpful error messages when you use the wrong types. In older Python versions, type errors could be cryptic. In 3.14, the interpreter gives you context about what was expected and what it got, often pointing directly to the variable that caused the problem.

When you hit a `TypeError` today — and you will — read the full message. Python 3.14 is trying to tell you exactly what went wrong. This is a skill: learning to read error messages rather than panic at them. Every error message in Python is a clue, not a wall.

---

## What's Coming

On **Day 03** we add interactivity — `input()` and `if/elif/else` — so TaskFlow AI can respond differently based on what the user types. The profile you built today becomes the starting point for a smart, personalized greeting system.

On **Day 04** we introduce lists and loops — the data structures that will let us store and manage multiple tasks, not just one user profile.
