# taskflow/errors.py
# TaskFlow AI — Custom exception hierarchy.
# All application exceptions inherit from TaskFlowError.
#
# Hierarchy:
#   TaskFlowError
#     ├── StorageError
#     ├── WeatherError
#     ├── ValidationError
#     └── TaskNotFoundError
#
# Version history:
#   Day 10 — initial exception hierarchy
#   Day 11 — moved into package structure


class TaskFlowError(Exception):
    """
    Base exception for all TaskFlow AI errors.

    Catch this in the main loop to handle any application-level failure.
    Catch subclasses for specific, recoverable failures.
    """

    pass


class StorageError(TaskFlowError):
    """
    Raised when task persistence operations fail.

    Examples:
        - JSON file is corrupted or contains invalid JSON
        - File cannot be read due to OS permissions
        - Atomic write (temp file rename) fails
        - Storage file has unexpected structure (not a list)
    """

    pass


class WeatherError(TaskFlowError):
    """
    Raised when weather API operations fail.

    Examples:
        - No internet connection
        - API returned a non-200 status code
        - Response JSON has unexpected structure
        - Request timed out
    """

    pass


class ValidationError(TaskFlowError):
    """
    Raised when input data fails business rule validation.

    Attributes:
        field (str): The name of the field that failed validation.
        value (any): The invalid value that was provided.

    Examples:
        - Task title is empty or too long
        - Priority is not one of high/medium/low
        - Category is not a valid option
        - Due date is in an invalid format
    """

    def __init__(self, message: str, field: str = "", value=None):
        super().__init__(message)
        self.field = field
        self.value = value

    def __str__(self) -> str:
        base = super().__str__()
        if self.field:
            return f"{base} (field: '{self.field}', got: {self.value!r})"
        return base


class TaskNotFoundError(TaskFlowError):
    """
    Raised when a task with the requested ID does not exist.

    Attributes:
        task_id (int): The ID that was searched for and not found.
    """

    def __init__(self, task_id: int):
        super().__init__(f"No task found with ID {task_id}")
        self.task_id = task_id
