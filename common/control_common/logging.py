"""Структурированное логирование в stdout для контейнеров."""

import json
import logging
import sys
from datetime import UTC, datetime


class JsonLogFormatter(logging.Formatter):
    """Форматтер JSON-логов, удобных для `docker compose logs` и grep."""

    def format(self, record: logging.LogRecord) -> str:
        """Преобразовать запись лога в одну JSON-строку."""

        payload = {
            "time": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: int = logging.INFO) -> None:
    """Включить JSON-логирование в stdout для Docker-контейнера."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
