# Day 01 — Welcome & Setup

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Project:** TaskFlow AI (your todo app that will grow into an AI product)

---

## Learning Objective

By the end of today, you will have Python installed, VS Code configured, a working terminal, and your very first Python script running on your own machine. You will understand what a programming environment is and why every piece of it matters.

---

## What We Build Today

A personal greeting script — `hello.py` — that prints your name, today's date, and a welcome message to the terminal. Small? Yes. But this is the foundation everything else is built on.

```
Hello, Udit!
Today is Monday, 19 May 2025.
Welcome to Day 01 of your Python journey.
Let's build something real.
```

---

## Concepts Covered

- What Python is and why we use it
- Installing Python 3.14 on Windows / macOS / Linux
- Setting up VS Code with the right extensions
- Terminal basics — the commands you'll use every day
- Running your first `.py` file
- `print()` — your first Python function
- Variables — storing information with a name
- f-strings — embedding variables inside text

---

## Full Tutorial

### What Is Python?

Python is a programming language. A programming language is a way to give precise instructions to a computer.

Computers don't understand English, but they do understand code. Python is designed to be as close to plain English as possible, which makes it one of the best languages to start with — and also one of the most used languages in the world for web backends, data science, automation, and AI engineering.

You are going to use Python every single day for the next 90 days.

> **Why Python 3.14?** This entire series is built on Python 3.14, released in October 2025. Here are a few things that make 3.14 special — you don't need to understand all of these today, but you will by Day 90:
> - **t-strings (template strings):** A new, safer way to build dynamic strings — especially useful for AI prompt engineering, which we cover in Phase 4.
> - **Lazy annotations:** Type hints are no longer evaluated at import time, making large codebases faster to load.
> - **Colorized REPL:** The interactive Python shell now highlights your code in color, making it easier to spot mistakes instantly.
> - **Experimental JIT compiler:** Python 3.14 ships with an opt-in Just-In-Time compiler that can speed up long-running programs — a glimpse at Python's performance future.
> - **Free-threaded mode:** True parallelism support is maturing — important for AI workloads in Phase 4.
>
> You are learning Python at exactly the right time.

---

### Step 1 — Install Python

Go to [https://www.python.org/downloads/](https://www.python.org/downloads/) and download **Python 3.14** — the latest stable release (released October 7, 2025).

> **Why 3.14 specifically?** This series uses 3.14 throughout because it is the current production-standard version with the longest support window (until October 2030). It also ships with a colorized interactive shell, better error messages, and an experimental JIT compiler — all things we will briefly explore across the series.

**Windows:**

Python 3.14 introduced a new install manager for Windows. You have two options:

Option A — **New Install Manager** (recommended): Download it from the Windows Store or from the link on the python.org downloads page. It handles PATH automatically.

Option B — **Traditional installer**: Run the `.exe` file. **Critical:** Check the box that says **"Add Python to PATH"** before clicking Install. Then click "Install Now."

**macOS:**

Option A — Official installer from python.org (recommended for beginners).

Option B — If you have Homebrew installed:

```bash
brew install python@3.14
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3.14 python3-pip
```

If Python 3.14 is not yet in your distribution's default package list, use the `deadsnakes` PPA:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.14 python3.14-venv python3-pip
```

**Verify the installation worked.** Open your terminal and type:

```bash
python --version
```

You should see:

```
Python 3.14.x
```

If you see `Python 2.x.x`, try `python3 --version` instead. On some systems, `python3` is the correct command.

**Bonus — try the new colorized REPL.** Just type `python` in your terminal (no file name). You will see the Python prompt (`>>>`). In 3.14, the REPL has syntax highlighting built in — keywords appear in color. Type `print("hello")` and press Enter. Type `exit()` to leave. This colorized shell is a 3.14 feature that makes interactive experimentation much easier for beginners.

---

### Step 2 — Install VS Code

VS Code (Visual Studio Code) is the code editor you will use throughout this series. It is free, fast, and used by millions of professional developers.

Download it from [https://code.visualstudio.com/](https://code.visualstudio.com/).

Install it like any normal application on your OS.

---

### Step 3 — Configure VS Code

Once VS Code is open, install these extensions. Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS) to open the Extensions panel, then search for each one:

| Extension | Why You Need It |
|---|---|
| **Python** (by Microsoft) | Syntax highlighting, IntelliSense, run Python files |
| **Pylance** | Type checking and smarter autocomplete |
| **Python Indent** | Fixes automatic indentation |
| **Material Icon Theme** | Makes the file explorer easier to read |
| **GitLens** | Git superpowers (we'll use this in Day 19) |

After installing the Python extension, VS Code will ask you to **select a Python interpreter**. Click the notification or press `Ctrl+Shift+P` → "Python: Select Interpreter" → choose the Python 3.14 version you just installed.

---

### Step 4 — Learn the Terminal

The terminal (also called the command line, shell, or console) is a text interface to your computer. Professional developers live in the terminal. You will use it every day.

**How to open it:**

- **Windows:** Search for "Windows Terminal" or "Command Prompt" in the Start menu. Or in VS Code: `Ctrl+`` ` (backtick).
- **macOS:** Search for "Terminal" in Spotlight (`Cmd+Space`).
- **Linux:** `Ctrl+Alt+T` on most distributions.

**The commands you need today:**

```bash
# Print the current directory (where you are)
pwd

# List files and folders in the current directory
ls          # macOS / Linux
dir         # Windows

# Change directory (move into a folder)
cd Desktop

# Go up one level (to the parent folder)
cd ..

# Create a new folder
mkdir my_project

# Create a new file (macOS/Linux)
touch hello.py

# Clear the terminal screen
clear       # macOS / Linux
cls         # Windows
```

**Practice:** Open your terminal and navigate to your Desktop using `cd`. Create a folder called `taskflow`:

```bash
cd Desktop
mkdir taskflow
cd taskflow
```

You are now inside your project folder. Everything we build for the next 90 days will live here.

---

### Step 5 — Your First Python Script

Open the `taskflow` folder in VS Code:

```bash
code .
```

The `.` means "open VS Code in the current folder." If this command doesn't work on macOS, open VS Code manually, then go to `File → Open Folder` and select the `taskflow` folder.

Create a new file called `hello.py`. You can do this from the VS Code file explorer (click the new file icon) or in the terminal:

```bash
touch hello.py   # macOS / Linux
type nul > hello.py   # Windows
```

Now open `hello.py` in VS Code and type the following. Type it — don't copy and paste. Typing builds muscle memory:

```python
# Day 01 - hello.py
# This is our very first Python script.
# Lines starting with # are comments. Python ignores them.
# They are notes for humans.

# --- Variables ---
# A variable is a named container that holds a value.
# We use = to assign a value to a variable.

name = "Udit Rawat"
day_number = 1
series_name = "Python & AI Engineering"

# --- Printing ---
# print() is a built-in function that displays output to the terminal.
# We will use it constantly while learning.

print("Hello, " + name + "!")

# --- f-strings ---
# An f-string (formatted string) lets you embed variables directly inside text.
# Prefix the string with f and wrap variable names in curly braces {}.
# f-strings are the standard way to format strings in Python 3.6+.

print(f"Welcome to Day {day_number} of {series_name}.")

# --- Using the datetime module ---
# Python comes with a standard library full of useful tools.
# 'datetime' is a module (a file of reusable code) for working with dates and times.

import datetime

today = datetime.date.today()
formatted_date = today.strftime("%A, %d %B %Y")

print(f"Today is {formatted_date}.")
print("Let's build something real.")

# --- Python 3.14 curiosity: t-strings (preview, don't worry about this yet) ---
# Python 3.14 introduced t-strings — template strings that give you more control
# over how values are inserted into text. We'll use them in Phase 4 for AI prompts.
# For now, just know they exist. f-strings are what we'll use all through Phase 1.
# t"Hello {name}" — same look as f-strings, but safer for dynamic content.
```

---

### Step 6 — Run Your Script

In the terminal (make sure you are inside the `taskflow` folder):

```bash
python hello.py
```

Or on some systems:

```bash
python3 hello.py
```

You should see:

```
Hello, Udit Rawat!
Welcome to Day 1 of Python & AI Engineering.
Today is Monday, 19 May 2025.
Let's build something real.
```

**You just ran your first Python program.**

---

### Step 7 — Understand What You Wrote

Let's break down every important line.

**Comments:**

```python
# This is a comment
```

Python ignores any line that starts with `#`. Use comments to explain *why* you wrote something, not *what* it does. Good comments are a habit worth building from Day 1.

**Variables:**

```python
name = "Udit"
day_number = 1
```

A variable is a named box that stores a value. The `=` sign is the assignment operator — it means "store the value on the right inside the box named on the left." Variable names should be lowercase with underscores separating words. This convention is called **snake_case** and it is the Python standard.

**Strings:**

```python
name = "Udit"
series_name = "Python & AI Engineering"
```

A string is a sequence of characters (text). Strings are always wrapped in quotes — either single `'` or double `"`. Python treats them identically. Pick one style and be consistent.

**Integers:**

```python
day_number = 1
```

An integer is a whole number without a decimal point.

**print():**

```python
print("Hello!")
print(f"Day {day_number}")
```

`print()` is a function. A function is a reusable block of code that does something. You *call* a function by writing its name followed by parentheses. Whatever you put inside the parentheses is called an *argument* — the input you are giving to the function.

**f-strings:**

```python
print(f"Welcome to Day {day_number}.")
```

The `f` before the opening quote makes this an f-string. Anything inside `{}` is evaluated as Python code and its result is inserted into the string. This is the cleanest, most modern way to build strings in Python. Use f-strings everywhere.

**import:**

```python
import datetime
```

`import` loads a module — a library of pre-written Python code. `datetime` is part of Python's standard library (it comes with Python, you don't install anything extra). After importing, you access its contents with the dot notation: `datetime.date.today()`.

---

## Exercises

Work through these before Day 02. Do not skip them.

**Exercise 1 — Personalize it.**
Change the `name` variable to your own name. Change `day_number` to any number. Run the script and verify the output changes.

**Exercise 2 — Add more variables.**
Add variables for your city and your goal for this series. Print them using f-strings.

```python
city = "Mumbai"
goal = "build an AI product"
print(f"I am {name} from {city} and I want to {goal}.")
```

**Exercise 3 — Explore print().**
What happens if you call `print()` with no arguments? Try it. What does it output?

**Exercise 4 — Break it on purpose.**
Delete one of the closing `"` from a string. Run the script. Read the error message carefully. This is a `SyntaxError`. Learning to read error messages is a core skill. Then fix it.

**Exercise 5 — Format the date.**
The `datetime` module can format dates as readable text. Look at this:

```python
today = datetime.date.today()
formatted = today.strftime("%A, %d %B %Y")
print(f"Today is {formatted}.")
```

Add this to your script and run it. The output should look like: `Today is Monday, 19 May 2025.`

---

## Checkpoint

Before you move on to Day 02, you should be able to answer all of these:

- [ ] Python is installed and `python --version` shows 3.14.x
- [ ] VS Code is installed with the Python extension active
- [ ] You can open a terminal and navigate folders with `cd`
- [ ] You can create and run a `.py` file from the terminal
- [ ] You understand what a variable is
- [ ] You understand what `print()` does
- [ ] You understand what an f-string is
- [ ] You know what `import` does at a basic level

If any of these are unclear, re-read the relevant section or Google the specific question before moving on. Getting stuck is normal. Skipping confusion is not.

---

## Common Errors on Day 01

**`python` is not recognized as a command**
You forgot to check "Add Python to PATH" during installation. Reinstall Python and check that box, or search for how to add Python to PATH manually on your OS.

**`SyntaxError: EOL while scanning string literal`**
You have an unclosed string. A quote was opened but never closed. Check every `"` in your file.

**`IndentationError`**
Python uses indentation (spaces or tabs at the start of lines) to define structure. If you accidentally added a space before a line at the top level, Python will complain. We will cover indentation properly on Day 03 when we get to conditions.

**`ModuleNotFoundError: No module named 'datetime'`**
This should not happen since `datetime` is part of the standard library. If it does, your Python installation may be corrupted. Reinstall Python.

---

## What's Coming

On Day 02, we go deeper into variables and data types — strings, integers, floats, booleans — and you will start building the first version of the TaskFlow application that will carry us through all 90 days.

Every line of code you write from here will be part of something real.

> **A note on Python 3.14 features across this series:** We use f-strings throughout Phase 1 and 2 because they are universal and beginner-friendly. In Phase 4 (AI Engineering), we will introduce **t-strings** — Python 3.14's new template string feature — when building AI prompts, because t-strings are specifically designed for safely handling dynamic, user-supplied content in strings. Every new feature of 3.14 will appear at the moment it is most naturally useful in our project.

---

## Vlog Content Angle

**"The programmer's first day — raw, honest, and real."**

Film your actual setup process. Don't hide the confusion. If something doesn't install correctly the first time, keep the camera rolling and fix it on screen. That raw moment — the error, the frustration, the fix — is more valuable to a beginner than a perfect tutorial.

Talk directly to the viewer who is terrified to start. Tell them what you were thinking when you first ran `python hello.py`. Keep it human. The goal of Day 01 is not to teach Python. It is to make someone believe they can do this.

Show your desktop. Show your terminal. Show the error message you got. Show it working. That journey in 10 minutes is what builds an audience for 90 days.
