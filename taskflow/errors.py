class TaskFlowError(Exception):
    """Base exception for all TaskFlow AI errors."""
    pass

class StorageError(TaskFlowError):
    """Raised when task persistence operations fail."""
    pass

class WeatherError(TaskFlowError):
    """Raised when weather API operations fail."""
    pass

class ValidationError(TaskFlowError):
    """Raised when input data fails business rule validation."""
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
    """Raised when a task with the requested ID does not exist."""
    def __init__(self, task_id: int):
        super().__init__(f"No task found with ID {task_id}")
        self.task_id = task_id