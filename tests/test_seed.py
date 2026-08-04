from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from mex.common.settings import SETTINGS_STORE
from mex.testing.seed import connect, main
from mex.testing.settings import SeedSettings

if TYPE_CHECKING:  # pragma: no cover
    import pyodbc  # type: ignore[import-not-found]

SEEDS_PATH = Path(__file__).parent.parent / "seeds"


@pytest.fixture
def seed_settings() -> Generator[SeedSettings, None, None]:
    """Swap the settings singleton for the seeder settings, pointed at our seeds."""
    SETTINGS_STORE.reset()
    settings = SeedSettings(directory=SEEDS_PATH)
    SETTINGS_STORE.push(settings)
    yield settings
    SETTINGS_STORE.reset()


@pytest.fixture
def seeded_connection(
    seed_settings: SeedSettings,  # noqa: ARG001
) -> "pyodbc.Connection":
    """Apply all bundled seeds and return a connection to the seeded server."""
    main()
    return connect()


@pytest.mark.integration
@pytest.mark.parametrize(
    ("database", "schema"),
    [
        pytest.param("GrippeWeb", "MEx", id="grippeweb"),
        pytest.param("SurvNet3Meta", "Meta", id="ifsg"),
        pytest.param("KVIS", "Mex", id="kvis"),
    ],
)
def test_seeded_tables_are_not_empty(
    seeded_connection: "pyodbc.Connection",
    database: str,
    schema: str,
) -> None:
    cursor = seeded_connection.cursor()
    tables = [
        row.TABLE_NAME
        for row in cursor.execute(
            f"SELECT TABLE_NAME FROM {database}.INFORMATION_SCHEMA.TABLES "  # noqa: S608
            "WHERE TABLE_SCHEMA = ?",
            schema,
        ).fetchall()
    ]
    assert tables, f"no tables found in {database}.{schema}"
    counts = {
        table: cursor.execute(
            f"SELECT COUNT(*) FROM {database}.{schema}.{table}"  # noqa: S608
        ).fetchval()
        for table in tables
    }
    assert all(count > 0 for count in counts.values()), counts
