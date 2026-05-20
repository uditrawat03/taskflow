# Day 14 — Working with APIs & Regular Expressions

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Smart task parser & deeper API integration

---

## Learning Objective

By the end of today, you will understand regular expressions well enough to write a natural language task parser, and you will consume APIs more deeply — handling pagination, query parameters, headers, and rate limits. TaskFlow AI gains a powerful shorthand input syntax that automatically creates the right task type from a single line of text.

---

## What We Build Today

A `parser.py` module that understands natural language task shorthand, and a deeper weather integration that fetches a 3-day forecast alongside current conditions.

```
# Smart task input — one line creates a fully configured task:
> add
Input: Review PR #high @work !2025-06-01

✓ DeadlineTask created:
  Title    : Review PR
  Priority : high
  Category : work
  Due date : 2025-06-01 (13 days away 🟢)

> add
Input: Daily standup ~daily @work

✓ RecurringTask created:
  Title      : Daily standup
  Category   : work
  Recurrence : daily

> add
Input: !! Server is down @work

✓ UrgentTask created:
  Title    : Server is down
  Category : work
  Priority : high (forced)

> forecast
  ── 3-Day Forecast — Delhi, IN ───────────────
  Today      Mon 19 May   38°C   ☀  Clear
  Tomorrow   Tue 20 May   36°C   ⛅  Partly cloudy
  Wed 21 May              33°C   🌧  Rain showers
  ────────────────────────────────────────────
```

---

## Concepts Covered

- Regular expressions — `re` module
- `re.search()`, `re.match()`, `re.findall()`, `re.sub()`
- Patterns — character classes, quantifiers, groups, alternation
- Named groups — `(?P<name>pattern)`
- Compiling patterns — `re.compile()`
- Flags — `re.IGNORECASE`, `re.MULTILINE`
- Practical regex — email, date, hashtag, mention parsing
- API pagination and query parameters
- Request headers — `User-Agent`, `Accept`, `Authorization`
- Rate limiting — detecting and respecting `Retry-After`
- Parsing structured API responses
- Building a smart natural language parser

---

## Full Tutorial

### What Are Regular Expressions?

A regular expression (regex) is a pattern that describes a set of strings. It lets you search, extract, and transform text based on structure rather than exact values.

```python
import re

text = "Contact Udit at udit@taskflow.ai or call +91-9876543210"

# Does it contain an email?
if re.search(r"[\w.+-]+@[\w-]+\.\w+", text):
    print("Email found!")

# Extract the email
match = re.search(r"[\w.+-]+@[\w-]+\.\w+", text)
if match:
    print(match.group())   # "udit@taskflow.ai"

# Extract the phone number
phone = re.search(r"\+[\d-]+", text)
if phone:
    print(phone.group())   # "+91-9876543210"
```

---

### The `re` Module — Core Functions

```python
import re

text = "Task #1: Review PR [HIGH] due 2025-06-01"

# re.search() — find the first match anywhere in the string
match = re.search(r"\d{4}-\d{2}-\d{2}", text)
if match:
    print(match.group())    # "2025-06-01"
    print(match.start())    # 30  — position in string
    print(match.end())      # 40

# re.match() — match only at the START of the string
match = re.match(r"Task", text)     # ✅ matches — starts with "Task"
match = re.match(r"Review", text)   # None — not at start

# re.findall() — return ALL matches as a list
numbers = re.findall(r"\d+", text)
print(numbers)    # ["1", "2025", "06", "01"]

# re.sub() — replace matches
cleaned = re.sub(r"\[HIGH\]", "[URGENT]", text)
print(cleaned)    # "Task #1: Review PR [URGENT] due 2025-06-01"

# re.split() — split on a pattern
parts = re.split(r"[:\s]+", "key1:value1 key2:value2")
print(parts)    # ["key1", "value1", "key2", "value2"]
```

---

### Pattern Syntax — The Essential Reference

```
.       Any character except newline
\d      Digit (0-9)
\w      Word character (a-z, A-Z, 0-9, _)
\s      Whitespace (space, tab, newline)
\D      Non-digit
\W      Non-word character
\S      Non-whitespace

^       Start of string
$       End of string

*       0 or more (greedy)
+       1 or more (greedy)
?       0 or 1 (makes previous optional)
{n}     Exactly n times
{n,m}   Between n and m times
*?      0 or more (lazy — as few as possible)
+?      1 or more (lazy)

[abc]   Any of: a, b, c
[^abc]  Any character EXCEPT a, b, c
[a-z]   Any lowercase letter
[A-Z0-9] Any uppercase letter or digit

(...)   Capturing group
(?:...) Non-capturing group
|       Alternation — this OR that
```

---

### Named Groups — `(?P<name>pattern)`

Named groups let you extract parts of a match by name instead of index:

```python
import re

# Parse a task shorthand: "Review PR #high @work !2025-06-01"
pattern = re.compile(
    r"(?:#(?P<priority>high|medium|low))?"    # optional #priority
    r"\s*(?:@(?P<category>\w+))?"             # optional @category
    r"\s*(?:!(?P<due_date>\d{4}-\d{2}-\d{2}))?",  # optional !date
    re.IGNORECASE
)

text = "#high @work !2025-06-01"
match = pattern.search(text)
if match:
    print(match.group("priority"))  # "high"
    print(match.group("category"))  # "work"
    print(match.group("due_date"))  # "2025-06-01"
```

---

### `re.compile()` — Reuse Patterns Efficiently

Compiling a pattern once and reusing it is faster than calling `re.search()` with a string pattern each time:

```python
import re

# Compile once at module level
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.\w{2,}")
DATE_PATTERN  = re.compile(r"\d{4}-\d{2}-\d{2}")
HASHTAG       = re.compile(r"#(\w+)")
MENTION       = re.compile(r"@(\w+)")

# Use many times — no recompilation
emails = EMAIL_PATTERN.findall("Send to udit@ai.com and team@taskflow.io")
dates  = DATE_PATTERN.findall("Due 2025-06-01 or 2025-06-15")
tags   = HASHTAG.findall("#high #urgent #python")
```

---

### Flags

```python
import re

# IGNORECASE — case-insensitive matching
re.search(r"high", "PRIORITY: HIGH", re.IGNORECASE)   # matches

# MULTILINE — ^ and $ match start/end of each line
text = "task one\ntask two\ntask three"
matches = re.findall(r"^task \w+", text, re.MULTILINE)
# ["task one", "task two", "task three"]

# DOTALL — . matches newlines too
re.search(r"start.*end", "start\nmiddle\nend", re.DOTALL)   # matches

# Combine flags
re.findall(r"^#\w+", text, re.IGNORECASE | re.MULTILINE)
```

---

### Building `parser.py` — Smart Task Input

```python
# taskflow/parser.py
# TaskFlow AI — Day 14
# Natural language task input parser.
#
# Shorthand syntax:
#   !! title           → UrgentTask (forces priority=high)
#   ~daily title       → RecurringTask (daily/weekly/monthly)
#   title #priority    → sets priority (high/medium/low)
#   title @category    → sets category (work/personal/health/learning/other)
#   title !YYYY-MM-DD  → DeadlineTask with due date
#
# Multiple tokens can be combined:
#   "Review PR #high @work !2025-06-01" → DeadlineTask, priority=high, category=work

import re
import datetime
from .core.task       import Task
from .core.task_types import UrgentTask, RecurringTask, DeadlineTask
from .config          import VALID_PRIORITIES, VALID_CATEGORIES
from .errors          import ValidationError

# ── Compiled Patterns ─────────────────────────────────────

_URGENT_PREFIX    = re.compile(r"^!!\s*")
_RECURRING_PREFIX = re.compile(r"^~(daily|weekly|monthly)\s+", re.IGNORECASE)
_PRIORITY_TOKEN   = re.compile(r"#(high|medium|low)", re.IGNORECASE)
_CATEGORY_TOKEN   = re.compile(r"@(\w+)", re.IGNORECASE)
_DUE_DATE_TOKEN   = re.compile(r"!(\d{4}-\d{2}-\d{2})")
_WHITESPACE       = re.compile(r"\s{2,}")


class ParseResult:
    """
    Holds the structured data extracted from a raw task input string.

    Attributes:
        title      (str)       : Cleaned task title.
        priority   (str)       : Detected priority or default.
        category   (str)       : Detected category or default.
        due_date   (str | None): Detected due date string or None.
        recurrence (str | None): Detected recurrence or None.
        is_urgent  (bool)      : True if the '!!' prefix was found.
        task_type  (str)       : 'urgent', 'recurring', 'deadline', or 'standard'.
        raw        (str)       : The original input string.
    """

    def __init__(self, title: str, priority: str = "medium",
                 category: str = "work", due_date: str | None = None,
                 recurrence: str | None = None, is_urgent: bool = False,
                 raw: str = ""):
        self.title      = title
        self.priority   = priority
        self.category   = category
        self.due_date   = due_date
        self.recurrence = recurrence
        self.is_urgent  = is_urgent
        self.raw        = raw

        # Determine task type
        if is_urgent:
            self.task_type = "urgent"
        elif recurrence:
            self.task_type = "recurring"
        elif due_date:
            self.task_type = "deadline"
        else:
            self.task_type = "standard"

    def __repr__(self) -> str:
        return (f"ParseResult(title={self.title!r}, priority={self.priority!r}, "
                f"category={self.category!r}, task_type={self.task_type!r})")


def parse_task_input(raw: str) -> ParseResult:
    """
    Parse a raw task input string into a structured ParseResult.

    Supports shorthand tokens:
        !!       → urgent task
        ~daily   → daily recurring task
        #high    → priority
        @work    → category
        !date    → deadline (YYYY-MM-DD)

    Args:
        raw (str): Raw user input string.

    Returns:
        ParseResult: Extracted task attributes.

    Raises:
        ValidationError: If the input is empty or contains invalid values.
    """
    text = raw.strip()

    if not text:
        raise ValidationError("Task input cannot be empty",
                               field="input", value=text)

    is_urgent  = False
    recurrence = None
    priority   = "medium"
    category   = "work"
    due_date   = None

    # ── Detect urgent prefix (!!) ──────────────────────────
    if _URGENT_PREFIX.match(text):
        is_urgent = True
        priority  = "high"
        text      = _URGENT_PREFIX.sub("", text).strip()

    # ── Detect recurring prefix (~daily/weekly/monthly) ────
    rec_match = _RECURRING_PREFIX.match(text)
    if rec_match and not is_urgent:
        recurrence = rec_match.group(1).lower()
        text       = text[rec_match.end():].strip()

    # ── Extract #priority token ────────────────────────────
    pri_match = _PRIORITY_TOKEN.search(text)
    if pri_match:
        detected = pri_match.group(1).lower()
        if detected in VALID_PRIORITIES:
            priority = detected
        text = _PRIORITY_TOKEN.sub("", text).strip()

    # ── Extract @category token ────────────────────────────
    cat_match = _CATEGORY_TOKEN.search(text)
    if cat_match:
        detected = cat_match.group(1).lower()
        if detected in VALID_CATEGORIES:
            category = detected
        elif detected:
            raise ValidationError(
                f"Unknown category '@{detected}'. "
                f"Valid: {', '.join(sorted(VALID_CATEGORIES))}",
                field="category", value=detected
            )
        text = _CATEGORY_TOKEN.sub("", text).strip()

    # ── Extract !date token ────────────────────────────────
    date_match = _DUE_DATE_TOKEN.search(text)
    if date_match and not is_urgent and not recurrence:
        date_str = date_match.group(1)
        # Validate the date
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            due_date = date_str
        except ValueError:
            raise ValidationError(
                f"Invalid date '{date_str}'. Use YYYY-MM-DD format.",
                field="due_date", value=date_str
            )
        text = _DUE_DATE_TOKEN.sub("", text).strip()

    # ── Clean up remaining text as the title ──────────────
    title = _WHITESPACE.sub(" ", text).strip()

    if not title:
        raise ValidationError(
            "Could not extract a title from the input. "
            "Make sure the title comes before the tokens.",
            field="title", value=raw
        )

    return ParseResult(
        title=title,
        priority=priority,
        category=category,
        due_date=due_date,
        recurrence=recurrence,
        is_urgent=is_urgent,
        raw=raw,
    )


def create_task_from_parse(result: ParseResult) -> Task:
    """
    Create the appropriate Task subclass from a ParseResult.

    Args:
        result (ParseResult): Output from parse_task_input().

    Returns:
        Task: The constructed task instance.
    """
    if result.task_type == "urgent":
        return UrgentTask(
            title=result.title,
            category=result.category,
        )
    elif result.task_type == "recurring":
        return RecurringTask(
            title=result.title,
            priority=result.priority,
            category=result.category,
            recurrence=result.recurrence,
        )
    elif result.task_type == "deadline":
        return DeadlineTask(
            title=result.title,
            priority=result.priority,
            category=result.category,
            due_date=result.due_date,
        )
    else:
        return Task(
            title=result.title,
            priority=result.priority,
            category=result.category,
        )


def parse_and_create(raw: str) -> Task:
    """
    Parse a raw input string and return a fully constructed Task.

    Convenience wrapper around parse_task_input() + create_task_from_parse().

    Args:
        raw (str): Raw user input.

    Returns:
        Task: The constructed task instance.
    """
    result = parse_task_input(raw)
    return create_task_from_parse(result)
```

---

### Updating `cmd_add()` to Use the Parser

```python
# In taskflow/display/commands.py (or tasks.py)

from ..parser import parse_and_create, parse_task_input
from ..errors import ValidationError

def cmd_add(tasks: list) -> None:
    """Smart task add — supports full shorthand syntax."""

    print("\n  Shorthand: !! for urgent | ~daily/weekly/monthly for recurring")
    print("  Tokens: #high/#medium/#low  @category  !YYYY-MM-DD")
    print("  Example: Review PR #high @work !2025-06-01\n")

    raw = input("  Input: ").strip()
    if not raw:
        print("  ✗ Input cannot be empty.\n")
        return

    try:
        result = parse_task_input(raw)
        task   = create_task_from_parse(result)
        tasks.append(task)

        print(f"\n  ✓ {type(task).__name__} created:")
        print(f"    Title    : {task.title}")
        print(f"    Priority : {task.priority}")
        print(f"    Category : {task.category}")

        if hasattr(task, "due_date"):
            days = task.days_until_due
            print(f"    Due date : {task.due_date} "
                  f"({task.urgency_label})")
        if hasattr(task, "recurrence"):
            print(f"    Recurs   : {task.recurrence}")

        print()

    except ValidationError as e:
        print(f"\n  ✗ {e}\n")
```

---

### Deeper API Integration — 3-Day Forecast

Update `weather.py` to fetch and display a multi-day forecast:

```python
# In taskflow/integrations/weather.py — add forecast functions

def fetch_forecast(latitude: float, longitude: float,
                   location_name: str = "Your Location",
                   days: int = 3) -> list[dict] | None:
    """
    Fetch a multi-day weather forecast.

    Args:
        latitude      (float): Location latitude.
        longitude     (float): Location longitude.
        location_name (str)  : Display name.
        days          (int)  : Number of forecast days (1-7).

    Returns:
        list[dict] | None: List of daily forecast dicts, or None on failure.
    """
    params = {
        "latitude":        latitude,
        "longitude":       longitude,
        "daily":           ",".join([
                               "temperature_2m_max",
                               "temperature_2m_min",
                               "weather_code",
                               "precipitation_probability_max",
                           ]),
        "forecast_days":   days,
        "timezone":        "auto",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data   = response.json()
        daily  = data.get("daily", {})

        dates      = daily.get("time", [])
        max_temps  = daily.get("temperature_2m_max", [])
        min_temps  = daily.get("temperature_2m_min", [])
        codes      = daily.get("weather_code", [])
        rain_probs = daily.get("precipitation_probability_max", [])

        forecast = []
        for i in range(len(dates)):
            code = codes[i] if i < len(codes) else 0
            forecast.append({
                "date":      dates[i],
                "max_temp":  max_temps[i] if i < len(max_temps) else None,
                "min_temp":  min_temps[i] if i < len(min_temps) else None,
                "condition": WMO_CODES.get(code, "Unknown"),
                "emoji":     WMO_EMOJI.get(code, "🌡"),
                "rain_prob": rain_probs[i] if i < len(rain_probs) else None,
            })

        return forecast

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Forecast fetch failed: {e}")
        return None


def display_forecast(forecast: list[dict], location_name: str) -> None:
    """Display a formatted multi-day forecast table."""
    if not forecast:
        print("\n  Forecast not available.\n")
        return

    print(f"\n  ── {len(forecast)}-Day Forecast — {location_name} ─────────")

    for i, day in enumerate(forecast):
        # Parse and format the date
        try:
            dt        = datetime.datetime.strptime(day["date"], "%Y-%m-%d")
            if i == 0:
                label = "Today     "
            elif i == 1:
                label = "Tomorrow  "
            else:
                label = dt.strftime("%a %d %b ")
        except ValueError:
            label = day["date"]

        max_t = f"{day['max_temp']}°" if day["max_temp"] is not None else "N/A"
        min_t = f"{day['min_temp']}°" if day["min_temp"] is not None else "N/A"
        rain  = f"💧{day['rain_prob']}%" if day["rain_prob"] is not None else ""

        print(f"  {label:<12} {max_t:>4}/{min_t:<4}  "
              f"{day['emoji']}  {day['condition']:<20} {rain}")

    print("  " + "─" * 52)
    print()
```

---

### API Headers and Rate Limits

When consuming APIs in production, two things matter deeply:

**Always send a `User-Agent` header:**

```python
HEADERS = {
    "User-Agent": "TaskFlowAI/1.0 (github.com/udit/taskflow; udit@example.com)",
    "Accept":     "application/json",
}

response = requests.get(url, params=params, headers=HEADERS, timeout=10)
```

Many APIs block requests without a `User-Agent`. Some rate-limit anonymous requests more aggressively. A meaningful `User-Agent` identifies your app and is good internet citizenship.

**Respecting rate limits:**

```python
import time

def get_with_rate_limit_handling(url: str, params: dict,
                                  headers: dict, timeout: int = 10,
                                  max_retries: int = 3) -> dict | None:
    """
    Make a GET request, automatically retrying on 429 (Too Many Requests).
    """
    for attempt in range(1, max_retries + 1):
        response = requests.get(url, params=params,
                                headers=headers, timeout=timeout)

        if response.status_code == 429:
            # Server told us to slow down
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"  ⚠ Rate limited. Waiting {retry_after}s "
                  f"(attempt {attempt}/{max_retries})...")
            time.sleep(retry_after)
            continue

        response.raise_for_status()
        return response.json()

    print("  ✗ Max retries exceeded.")
    return None
```

The `Retry-After` header tells you exactly how many seconds to wait. Always honour it — ignoring it gets your IP banned.

---

### Regex Patterns Reference — TaskFlow Use Cases

```python
import re

# Validate email format
EMAIL = re.compile(r"^[\w.+-]+@[\w-]+\.\w{2,}$")
print(bool(EMAIL.match("udit@taskflow.ai")))   # True
print(bool(EMAIL.match("not-an-email")))        # False

# Validate date format YYYY-MM-DD
DATE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
print(bool(DATE.match("2025-06-01")))   # True
print(bool(DATE.match("2025-13-01")))   # False — month 13 invalid

# Extract all hashtags from text
HASHTAG = re.compile(r"#(\w+)")
tags = HASHTAG.findall("Working on #python and #ai today #taskflow")
print(tags)   # ['python', 'ai', 'taskflow']

# Find priority tokens
PRIORITY = re.compile(r"#(high|medium|low)", re.IGNORECASE)
print(PRIORITY.findall("Task #HIGH priority #medium effort"))
# ['HIGH', 'medium']

# Validate task ID format
TASK_ID = re.compile(r"^T-\d{4}$")
print(bool(TASK_ID.match("T-0042")))   # True
print(bool(TASK_ID.match("T42")))      # False

# Strip ANSI colour codes from terminal output
ANSI = re.compile(r"\x1b\[[0-9;]*m")
clean = ANSI.sub("", "\x1b[31mRed text\x1b[0m")
print(clean)   # "Red text"
```

---

## Exercises

**Exercise 1 — Parser stress test.**
Test `parse_task_input()` with at least 15 different inputs covering: all token combinations, missing tokens, invalid categories, invalid dates, empty input, only tokens with no title, `!!` + date conflict, `~daily` + date conflict. Print `ParseResult` for each. Fix any cases that crash or produce wrong output.

**Exercise 2 — Regex email validator.**
Write a function `validate_email(email: str) -> bool` using a compiled regex. Test it against: valid emails, emails with dots and plus signs in the local part, emails with subdomains, and clearly invalid strings. What are the edge cases your regex does not handle?

**Exercise 3 — API response explorer.**
Fetch the Open-Meteo forecast for three cities — Delhi, Mumbai, and Bengaluru. Display a comparison table showing today's max temp and condition. Use `requests` directly and navigate the JSON response manually. Then wrap it in proper error handling.

**Exercise 4 — Regex-powered search.**
Update `cmd_search()` to optionally accept a regex pattern when the user prefixes the input with `re:`:

```
> search
Keyword (or re:pattern): re:^Review.*PR$
```

Use `re.search(pattern, task.title, re.IGNORECASE)` for matching. Catch `re.error` if the user provides an invalid regex and show a helpful error message.

**Exercise 5 — Named group extraction.**
Write a `parse_structured_note(text)` function that extracts structured data from free-form notes using named groups:

```python
text = "Call client John at john@acme.com on 2025-06-15 about Project Alpha"

pattern = re.compile(
    r"(?:Call|Meet|Email)\s+(?P<contact>\w+(?:\s\w+)?)"
    r"(?:\s+at\s+(?P<email>[\w.+-]+@[\w-]+\.\w+))?"
    r"(?:\s+on\s+(?P<date>\d{4}-\d{2}-\d{2}))?"
    r"(?:\s+about\s+(?P<topic>.+))?",
    re.IGNORECASE
)
```

Return a dict of all named groups. Integrate this into a `"parse-note"` command.

**Exercise 6 (stretch) — Rate limit simulator.**
Write a `MockRateLimitedAPI` class that simulates a rate-limited API — raises a mock 429 response after N requests per minute. Use it to test your `get_with_rate_limit_handling()` function. Verify it correctly backs off and retries.

---

## Checkpoint

Before moving to Day 15:

- [ ] I understand the core regex syntax — `.`, `\d`, `\w`, `*`, `+`, `?`, `[]`, `()`
- [ ] I use named groups `(?P<name>...)` for readable extraction
- [ ] I compile patterns with `re.compile()` for reuse
- [ ] I know `re.search()`, `re.match()`, `re.findall()`, `re.sub()`
- [ ] I always use raw strings `r"pattern"` for regex patterns
- [ ] The task parser handles all shorthand tokens correctly
- [ ] `UrgentTask`, `RecurringTask`, and `DeadlineTask` are created automatically from input
- [ ] I always send a `User-Agent` header in API requests
- [ ] I handle `429 Too Many Requests` with exponential-style backoff
- [ ] The 3-day forecast is displayed alongside current weather

---

## Common Errors on Day 14

**Using a regular string instead of a raw string for regex:**

```python
re.search("\d+", text)    # ❌ \d might be interpreted as escape sequence
re.search(r"\d+", text)   # ✅ raw string — backslash is literal
```

Always use `r"..."` for regex patterns. No exceptions.

**`re.match()` vs `re.search()` confusion:**

```python
re.match(r"\d+", "abc 123")    # None — match() only checks at START
re.search(r"\d+", "abc 123")   # Match — search() finds anywhere
```

Use `re.match()` only when you expect the pattern at the very beginning. Use `re.search()` for anywhere in the string.

**Greedy vs lazy quantifiers:**

```python
text = "<b>bold</b> and <i>italic</i>"

re.findall(r"<.+>", text)    # ["<b>bold</b> and <i>italic</i>"]  greedy — too much
re.findall(r"<.+?>", text)   # ["<b>", "</b>", "<i>", "</i>"]    lazy — correct
```

Add `?` after `*` or `+` to make them lazy — they match as little as possible.

**`re.error` — invalid pattern:**

```python
try:
    re.compile(r"[unclosed")
except re.error as e:
    print(f"Invalid regex: {e}")
```

Always catch `re.error` when accepting user-supplied patterns.

**Not checking `match` before calling `.group()`:**

```python
match = re.search(r"\d+", "no numbers here")
print(match.group())   # ❌ AttributeError — match is None

if match:
    print(match.group())   # ✅ safe
```

---

## What's Coming

On **Day 15** we reach the first major milestone — TaskFlow AI v1.0. We will add `argparse` for a proper CLI interface, write the `README.md`, run the code review checklist one final time across the entire codebase, and do a full end-to-end demo of everything built across 15 days. This is the first "ship day" of the series — the moment the project becomes something you would be proud to show to another developer.
