import time
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pyodbc  # type: ignore[import-not-found]
import pytest

from mex.common.settings import SETTINGS_STORE
from mex.testing.seed import apply_seed, connect, main
from mex.testing.settings import TestingSettings

if TYPE_CHECKING:
    from pathlib import Path

NUMBERS = """
USE tempdb;
GO
DROP TABLE IF EXISTS dbo.SeedNumbers;
CREATE TABLE dbo.SeedNumbers (Id INT, Big BIGINT, Amount DECIMAL(9, 2), Ratio FLOAT, Flag BIT);
GO
INSERT INTO dbo.SeedNumbers (Id, Big, Amount, Ratio, Flag)
VALUES (1, 9223372036854775807, 123.45, 0.5, 1),
       (2, -9223372036854775808, -0.99, -1.5, 0);
GO
"""

TEXTS = """
USE tempdb;
GO
DROP TABLE IF EXISTS dbo.SeedTexts;
CREATE TABLE dbo.SeedTexts (Id INT, Label NVARCHAR(50), Code VARCHAR(10));
GO
INSERT INTO dbo.SeedTexts (Id, Label, Code)
VALUES (1, N'Grüße & Ümläute', 'ABC-123'),
       (2, N'it''s quoted', 'z');
GO
"""

DATES_AND_BLOBS = """
USE tempdb;
GO
DROP TABLE IF EXISTS dbo.SeedStamps;
CREATE TABLE dbo.SeedStamps (Id INT, ValidFrom DATE, RecordedAt DATETIME2(6), Reference UNIQUEIDENTIFIER, Payload VARBINARY(8));
GO
INSERT INTO dbo.SeedStamps (Id, ValidFrom, RecordedAt, Reference, Payload)
VALUES (1, '2024-01-31', '2024-01-31 12:34:56.123456', '6F9619FF-8B86-D011-B42D-00C04FC964FF', 0x0102030405060708);
GO
"""

NULLS = """
USE tempdb;
GO
DROP TABLE IF EXISTS dbo.SeedNulls;
CREATE TABLE dbo.SeedNulls (Id INT, Label NVARCHAR(50) NULL, Amount DECIMAL(9, 2) NULL);
GO
INSERT INTO dbo.SeedNulls (Id, Label, Amount) VALUES (1, NULL, NULL), (2, N'set', 1.00);
GO
"""

TWO_TABLES = """
USE tempdb;
GO
DROP TABLE IF EXISTS dbo.SeedChild;
DROP TABLE IF EXISTS dbo.SeedParent;
GO
CREATE TABLE dbo.SeedParent (IdParent INT PRIMARY KEY, Name NVARCHAR(50));
CREATE TABLE dbo.SeedChild (IdChild INT PRIMARY KEY, IdParent INT REFERENCES dbo.SeedParent (IdParent));
GO
INSERT INTO dbo.SeedParent (IdParent, Name) VALUES (1, N'parent');
INSERT INTO dbo.SeedChild (IdChild, IdParent) VALUES (10, 1), (20, 1);
GO
"""


class StubConnection:
    """Connection that records the statements executed on its cursor."""

    def __init__(self) -> None:
        self.statements: list[str] = []

    def cursor(self) -> StubConnection:
        return self

    def execute(self, statement: str) -> None:
        self.statements.append(statement)


def push_seed_settings(**overrides: Any) -> TestingSettings:  # noqa: ANN401
    """Swap the settings singleton for `TestingSettings` with the given overrides."""
    # the autouse `settings` fixture pushes `TestingSettings`, which would make
    # `TestingSettings.get()` inside the seeder raise, so we replace it for the test
    settings = TestingSettings(**overrides)
    SETTINGS_STORE.reset()
    SETTINGS_STORE.push(settings)
    return settings


def test_connect_retries_until_the_server_accepts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    push_seed_settings()
    attempts = []

    def fake_connect(dsn: str, autocommit: bool) -> str:  # noqa: ARG001, FBT001
        attempts.append(dsn)
        if len(attempts) < 3:
            error = "server not ready yet"
            raise pyodbc.Error(error)
        return "connection"

    monkeypatch.setattr(pyodbc, "connect", fake_connect)
    monkeypatch.setattr(time, "sleep", lambda _: None)
    assert connect() == "connection"
    assert len(attempts) == 3


def test_connect_gives_up_after_the_deadline() -> None:
    push_seed_settings(wait_seconds=0)
    with pytest.raises(SystemExit, match="server not ready after 0s"):
        connect()


def test_apply_seed_executes_go_separated_batches(tmp_path: Path) -> None:
    path = tmp_path / "batches.sql"
    path.write_text(
        "SELECT 'GOODBYE';\nGO\n\nSELECT 2;\ngo\n  GO  \nSELECT 3;\n",
        encoding="utf-8",
    )
    connection = StubConnection()
    apply_seed(connection, path)
    # separators may be lower-case, indented or repeated, and a trailing separator
    # must not produce an empty statement, which the driver would reject
    assert connection.statements == ["SELECT 'GOODBYE';", "SELECT 2;", "SELECT 3;"]


def test_main_without_seeds_exits(tmp_path: Path) -> None:
    push_seed_settings(directory=tmp_path)
    with pytest.raises(SystemExit, match=r"no \*\.sql seeds found"):
        main()


@pytest.mark.integration
@pytest.mark.parametrize(
    ("statements", "query", "expected_rows"),
    [
        pytest.param(
            NUMBERS,
            "SELECT * FROM tempdb.dbo.SeedNumbers ORDER BY Id",
            [
                (1, 9223372036854775807, Decimal("123.45"), 0.5, True),
                (2, -9223372036854775808, Decimal("-0.99"), -1.5, False),
            ],
            id="numbers",
        ),
        pytest.param(
            TEXTS,
            "SELECT * FROM tempdb.dbo.SeedTexts ORDER BY Id",
            [
                (1, "Grüße & Ümläute", "ABC-123"),
                (2, "it's quoted", "z"),
            ],
            id="texts",
        ),
        pytest.param(
            DATES_AND_BLOBS,
            "SELECT * FROM tempdb.dbo.SeedStamps",
            [
                (
                    1,
                    date(2024, 1, 31),
                    datetime(2024, 1, 31, 12, 34, 56, 123456),  # noqa: DTZ001
                    "6F9619FF-8B86-D011-B42D-00C04FC964FF",
                    b"\x01\x02\x03\x04\x05\x06\x07\x08",
                )
            ],
            id="dates_and_blobs",
        ),
        pytest.param(
            NULLS,
            "SELECT * FROM tempdb.dbo.SeedNulls ORDER BY Id",
            [(1, None, None), (2, "set", Decimal("1.00"))],
            id="nulls",
        ),
        pytest.param(
            TWO_TABLES,
            "SELECT p.Name, c.IdChild FROM tempdb.dbo.SeedParent p "
            "JOIN tempdb.dbo.SeedChild c ON c.IdParent = p.IdParent ORDER BY c.IdChild",
            [("parent", 10), ("parent", 20)],
            id="two_tables",
        ),
    ],
)
def test_seeded_statements_land_in_the_database(
    statements: str,
    query: str,
    expected_rows: list[tuple[Any, ...]],
    tmp_path: Path,
) -> None:
    (tmp_path / "test.sql").write_text(statements, encoding="utf-8")
    push_seed_settings(directory=tmp_path)
    main()
    cursor = connect().cursor()
    assert [tuple(row) for row in cursor.execute(query).fetchall()] == expected_rows
