class TaskFlowError(Exception):
    """
    Base exception for all TaskFlow AI errors.

    Catch this in the main loop to handle any app-level failure.
    Catch subclasses for specific, recoverable failures.
    """
    pass


class StorageError(TaskFlowError):
    """
    Raised when task persistence operations fail.

    Examples:
        - JSON file is corrupted
        - File cannot be read or written
        - Storage file has unexpected structure
    """
    pass


class WeatherError(TaskFlowError):
    """
    Raised when weather API operations fail.

    Examples:
        - No internet connection
        - API returned unexpected response
        - Request timed out
    """
    pass


class ValidationError(TaskFlowError):
    """
    Raised when input data fails business rule validation.

    Examples:
        - Task title is empty
        - Priority is not one of the valid options
        - Task ID is not a positive integer

    Attributes:
        field   (str): The name of the field that failed validation.
        value   (any): The invalid value that was provided.
    """
    def __init__(self, message: str, field: str = "", value=None):
        super().__init__(message)
        self.field = field
        self.value = value

    def __str__(self):
        base = super().__str__()
        if self.field:
            return f"{base} (field: '{self.field}', got: {self.value!r})"
        return base


class TaskNotFoundError(TaskFlowError):
    """
    Raised when a task with the requested ID does not exist.

    Attributes:
        task_id (int): The ID that was not found.
    """
    def __init__(self, task_id: int):
        super().__init__(f"No task found with ID {task_id}")
        self.task_id = task_id