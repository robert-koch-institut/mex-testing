import re
import time
from typing import TYPE_CHECKING

import pyodbc  # type: ignore[import-not-found]

from mex.common.logging import logger
from mex.testing.settings import TestingSettings

if TYPE_CHECKING:
    from pathlib import Path


def connect() -> pyodbc.Connection:
    """Wait for the server to accept connections, then return a connection."""
    settings = TestingSettings.get()
    deadline = time.monotonic() + settings.sql_seed_wait_seconds
    last_error: pyodbc.Error | None = None
    while time.monotonic() < deadline:
        try:
            connection = pyodbc.connect(settings.sql_seed_dsn(), autocommit=True)
        except pyodbc.Error as error:
            last_error = error
            logger.info(
                "waiting for %s:%s ...", settings.sql_seed_host, settings.sql_seed_port
            )
            time.sleep(3)
        else:
            logger.info(
                "connected to %s:%s", settings.sql_seed_host, settings.sql_seed_port
            )
            return connection
    message = f"server not ready after {settings.sql_seed_wait_seconds}s: {last_error}"
    raise SystemExit(message)


def apply_seed(connection: pyodbc.Connection, path: Path) -> None:
    """Apply a single `.sql` file, executing each `GO`-separated batch."""
    cursor = connection.cursor()
    file_content = path.read_text(encoding="utf-8")
    batches = re.split(r"^\s*GO\s*$", file_content, flags=re.IGNORECASE | re.MULTILINE)
    for batch in batches:
        if statement := batch.strip():  # handle the last eof GO yielding an empty batch
            cursor.execute(statement)

    logger.info("applied %s", path.name)


def main() -> None:
    """Apply all bundled seeds to the target server."""
    settings = TestingSettings.get()
    seeds = sorted(settings.sql_seed_directory.glob("*.sql"))
    if not seeds:
        message = f"no *.sql seeds found in {settings.sql_seed_directory}"
        raise SystemExit(message)
    connection = connect()
    for path in seeds:
        apply_seed(connection, path)
    logger.info("seeded %s source(s)", len(seeds))
