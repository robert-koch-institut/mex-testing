import json
import re
from typing import Annotated, Any, cast

from fastapi import APIRouter, Query

from mex.testing.settings import TestingSettings

router = APIRouter()

_WIKIDATA_QID_PATTERN = re.compile(r"Q[1-9][0-9]*")


def _load_entity(qid: str) -> dict[str, Any]:
    """Load one mocked entity, or return a wikidata-style `missing` marker."""
    settings = TestingSettings.get()
    entity_file = (
        settings.http_server_test_data_directory / "wikidata" / "entities" / qid
    ).with_suffix(".json")
    # only well-formed QIDs may touch the file system, guarding against traversal
    if _WIKIDATA_QID_PATTERN.fullmatch(qid) and entity_file.is_file():
        return cast("dict[str, Any]", json.loads(entity_file.read_text("utf-8")))
    return {"id": qid, "missing": ""}


@router.get("/wikidata/w/api.php", tags=["wikidata"])
def get_wikidata_entities(
    ids: Annotated[str | None, Query()] = None,
) -> dict[str, Any]:
    """Mock the wikidata `wbgetentities` action, one asset file per entity.

    The `ids` parameter holds one or more `|`-separated QIDs, each served from
    `wikidata/entities/{QID}.json`. All other parameters are ignored.
    """
    if not ids:
        return {"entities": {}}
    return {"entities": {qid: _load_entity(qid) for qid in ids.split("|")}}
