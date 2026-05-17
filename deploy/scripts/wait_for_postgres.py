"""Ожидание доступности TCP-порта PostgreSQL перед служебными командами."""

from __future__ import annotations

import os
import socket
import time


def main() -> None:
    """Дождаться открытия порта PostgreSQL."""

    host = os.getenv("POSTGRES_HOST", "postgres")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    deadline = time.monotonic() + 60

    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=3):
                return
        except OSError:
            time.sleep(2)

    raise TimeoutError(f"PostgreSQL is not available at {host}:{port}")


if __name__ == "__main__":
    main()
