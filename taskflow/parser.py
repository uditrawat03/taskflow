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
from .core.task import Task
from .core.task_types import UrgentTask, RecurringTask, DeadlineTask
from .config import VALID_PRIORITIES, VALID_CATEGORIES
from .errors import ValidationError

# ── Compiled Patterns ─────────────────────────────────────

_URGENT_PREFIX = re.compile(r"^!!\s*")
_RECURRING_PREFIX = re.compile(r"^~(daily|weekly|monthly)\s+", re.IGNORECASE)
_PRIORITY_TOKEN = re.compile(r"#(high|medium|low)", re.IGNORECASE)
_CATEGORY_TOKEN = re.compile(r"@(\w+)", re.IGNORECASE)
_DUE_DATE_TOKEN = re.compile(r"!(\d{4}-\d{2}-\d{2})")
_WHITESPACE = re.compile(r"\s{2,}")


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

    def __init__(
        self,
        title: str,
        priority: str = "medium",
        category: str = "work",
        due_date: str | None = None,
        recurrence: str | None = None,
        is_urgent: bool = False,
        raw: str = "",
    ):
        self.title = title
        self.priority = priority
        self.category = category
        self.due_date = due_date
        self.recurrence = recurrence
        self.is_urgent = is_urgent
        self.raw = raw

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
        return (
            f"ParseResult(title={self.title!r}, priority={self.priority!r}, "
            f"category={self.category!r}, task_type={self.task_type!r})"
        )


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
        raise ValidationError("Task input cannot be empty", field="input", value=text)

    is_urgent = False
    recurrence = None
    priority = "medium"
    category = "work"
    due_date = None

    # ── Detect urgent prefix (!!) ──────────────────────────
    if _URGENT_PREFIX.match(text):
        is_urgent = True
        priority = "high"
        text = _URGENT_PREFIX.sub("", text).strip()

    # ── Detect recurring prefix (~daily/weekly/monthly) ────
    rec_match = _RECURRING_PREFIX.match(text)
    if rec_match and not is_urgent:
        recurrence = rec_match.group(1).lower()
        text = text[rec_match.end() :].strip()

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
                field="category",
                value=detected,
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
                field="due_date",
                value=date_str,
            )
        text = _DUE_DATE_TOKEN.sub("", text).strip()

    # ── Clean up remaining text as the title ──────────────
    title = _WHITESPACE.sub(" ", text).strip()

    if not title:
        raise ValidationError(
            "Could not extract a title from the input. "
            "Make sure the title comes before the tokens.",
            field="title",
            value=raw,
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
