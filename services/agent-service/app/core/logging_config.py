from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Formats every log record as a single JSON line.

    Structured fields node_name, request_id, job_id, cv_id are included when
    present on the record (injected by NodeLoggerAdapter via extra=).
    """

    _STRUCTURED_FIELDS = ("node_name", "request_id", "job_id", "cv_id")

    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for field in self._STRUCTURED_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                entry[field] = str(value)

        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(entry)


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
