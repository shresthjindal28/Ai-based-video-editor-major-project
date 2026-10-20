class DomainError(Exception):
    def __init__(
        self, code: str, message: str, status: int = 400, *, details: object | None = None
    ):
        self.code = code
        self.message = message
        self.status = status
        self.details = details
        super().__init__(message)


class ProcessError(DomainError):
    """A safe, actionable failure from an external media process."""


class RetryableError(Exception):
    """Transient task error eligible for bounded Celery retry."""
