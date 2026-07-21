"""Apply every bundled ``seeds/*.sql`` file to a target SQL Server.

The seeder image bundles one ``.sql`` file per primary source (e.g.
``grippeweb.sql``). Each file is self-contained and idempotent and uses ``GO`` batch
separators. This entrypoint waits for the target server to accept connections, then
applies all seeds using pyodbc (the same client stack as the mex-extractors
connectors).
"""

import time
from pathlib import Path

import pyodbc  # type: ignore[import-not-found]

from mex.common.logging import logger
from mex.testing.settings import SeedSettings


def connect() -> pyodbc.Connection:
    """Wait for the server to accept connections, then return a connection."""
    settings = SeedSettings.get()
    deadline = time.monotonic() + settings.wait_seconds
    last_error: pyodbc.Error | None = None
    while time.monotonic() < deadline:
        try:
            connection = pyodbc.connect(settings.dsn(), autocommit=True)
        except pyodbc.Error as error:
            last_error = error
            logger.info("waiting for %s:%s ...", settings.host, settings.port)
            time.sleep(3)
        else:
            logger.info("connected to %s:%s", settings.host, settings.port)
            return connection
    message = f"server not ready after {settings.wait_seconds}s: {last_error}"
    raise SystemExit(message)


def apply_seed(connection: pyodbc.Connection, path: Path) -> None:
    """Apply a single ``.sql`` file, executing each ``GO``-separated batch."""
    batch: list[str] = []
    cursor = connection.cursor()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().upper() == "GO":
            statement = "\n".join(batch).strip()
            if statement:
                cursor.execute(statement)
            batch = []
        else:
            batch.append(line)
    statement = "\n".join(batch).strip()
    if statement:
        cursor.execute(statement)
    logger.info("applied %s", path.name)


def main() -> None:
    """Apply all bundled seeds to the target server."""
    settings = SeedSettings.get()
    seeds = sorted(settings.directory.glob("*.sql"))
    if not seeds:
        message = f"no *.sql seeds found in {settings.directory}"
        raise SystemExit(message)
    connection = connect()
    for path in seeds:
        apply_seed(connection, path)
    logger.info("seeded %s source(s)", len(seeds))
