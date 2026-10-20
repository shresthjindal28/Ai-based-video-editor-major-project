import json
import logging
import traceback
from contextvars import ContextVar
from datetime import UTC, datetime

request_id: ContextVar[str] = ContextVar("request_id", default="")


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "time": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "request_id": request_id.get(),
                "correlation_id": request_id.get(),
                **({"exception_type": type(record.exc_info[1]).__name__,
                    "traceback": traceback.format_tb(record.exc_info[2])} if record.exc_info else {}),
                **{
                    k: getattr(record, k)
                    for k in (
                        "job_id",
                        "project_id",
                        "operation",
                        "duration",
                        "outcome",
                        "error_code",
                    )
                    if hasattr(record, k)
                },
            },
            default=str,
        )


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)
