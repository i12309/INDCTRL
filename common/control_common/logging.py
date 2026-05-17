"""Настройка логирования для контейнеров."""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Включить простой формат логов, удобный для `docker compose logs`."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
