import re
import datetime

from .core.task import Task
from .core.task_types import UrgentTask, RecurringTask, DeadlineTask
from .config import VALID_PRIORITIES, VALID_CATEGORIES
from .errors import ValidationError

__all__ = [
    "parse_task_input",
    "create_task_from_parse",
    "parse_and_create",
    "ParseResult",
]

#  Compiled patterns ─
_URGENT_PREFIX = re.compile(r"^!!\s*")
_RECURRING_PREFIX = re.compile(r"^~(daily|weekly|monthly)\s+", re.IGNORECASE)
_PRIORITY_TOKEN = re.compile(r"#(high|medium|low)", re.IGNORECASE)
_CATEGORY_TOKEN = re.compile(r"@(\w+)", re.IGNORECASE)
_DUE_DATE_TOKEN = re.compile(r"!(\d{4}-\d{2}-\d{2})")
_EXTRA_SPACES = re.compile(r"\s{2,}")


class ParseResult:
    """
    Structured output from parse_task_input().

    Attributes:
        title      (str)       : Cleaned task title.
        priority   (str)       : Detected or default priority.
        category   (str)       : Detected or default category.
        due_date   (str|None)  : YYYY-MM-DD string, or None.
        recurrence (str|None)  : 'daily'/'weekly'/'monthly', or None.
        is_urgent  (bool)      : True if '!!' prefix was detected.
        task_type  (str)       : 'urgent' | 'recurring' | 'deadline' | 'standard'.
        raw        (str)       : Original unmodified input.
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

    Args:
        raw (str): Raw user input.

    Returns:
        ParseResult: All extracted task attributes.

    Raises:
        ValidationError: If input is empty, title cannot be extracted,
                         or a token value is invalid.
    """
    text = raw.strip()
    if not text:
        raise ValidationError("Task input cannot be empty.", field="input", value=text)

    is_urgent = False
    recurrence = None
    priority = "medium"
    category = "work"
    due_date = None

    #  Detect !! (urgent) 
    if _URGENT_PREFIX.match(text):
        is_urgent = True
        priority = "high"
        text = _URGENT_PREFIX.sub("", text).strip()

    #  Detect ~recurrence 
    if not is_urgent:
        m = _RECURRING_PREFIX.match(text)
        if m:
            recurrence = m.group(1).lower()
            text = text[m.end() :].strip()

    #  Extract #priority ─
    m = _PRIORITY_TOKEN.search(text)
    if m:
        detected = m.group(1).lower()
        if detected in VALID_PRIORITIES:
            priority = detected
        text = _PRIORITY_TOKEN.sub("", text).strip()

    #  Extract @category ─
    m = _CATEGORY_TOKEN.search(text)
    if m:
        detected = m.group(1).lower()
        if detected in VALID_CATEGORIES:
            category = detected
        else:
            raise ValidationError(
                f"Unknown category '@{detected}'. "
                f"Valid: {', '.join(sorted(VALID_CATEGORIES))}",
                field="category",
                value=detected,
            )
        text = _CATEGORY_TOKEN.sub("", text).strip()

    #  Extract !YYYY-MM-DD (only for non-urgent, non-recurring) 
    if not is_urgent and not recurrence:
        m = _DUE_DATE_TOKEN.search(text)
        if m:
            date_str = m.group(1)
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

    #  Clean remaining text → title ─
    title = _EXTRA_SPACES.sub(" ", text).strip()
    if not title:
        raise ValidationError(
            "Could not extract a title from input. "
            "Write the title before or after the tokens.",
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
    Instantiate the appropriate Task subclass from a ParseResult.

    Args:
        result (ParseResult): Output from parse_task_input().

    Returns:
        Task: A fully constructed Task (or subclass) instance.
    """
    if result.task_type == "urgent":
        return UrgentTask(title=result.title, category=result.category)

    if result.task_type == "recurring":
        return RecurringTask(
            title=result.title,
            priority=result.priority,
            category=result.category,
            recurrence=result.recurrence,
        )

    if result.task_type == "deadline":
        return DeadlineTask(
            title=result.title,
            priority=result.priority,
            category=result.category,
            due_date=result.due_date,
        )

    return Task(
        title=result.title,
        priority=result.priority,
        category=result.category,
    )


def parse_and_create(raw: str) -> Task:
    """
    Convenience wrapper: parse raw input and return a Task.

    Args:
        raw (str): Raw user input string.

    Returns:
        Task: The constructed Task instance.

    Raises:
        ValidationError: If parsing or construction fails.
    """
    return create_task_from_parse(parse_task_input(raw))
