from typing import TYPE_CHECKING

from starlette import status

if TYPE_CHECKING:  # pragma: no cover
    from fastapi.testclient import TestClient


def test_get_wikidata_entities_single(client: TestClient) -> None:
    response = client.get(
        "/v0/wikidata/w/api.php",
        params={"action": "wbgetentities", "format": "json", "ids": "Q42"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {
        "entities": {
            "Q42": {
                "id": "Q42",
                "labels": {"en": {"language": "en", "value": "Robert Koch"}},
            }
        }
    }


def test_get_wikidata_entities_batch_with_missing(client: TestClient) -> None:
    response = client.get("/v0/wikidata/w/api.php", params={"ids": "Q42|Q1|../Q42"})
    assert response.status_code == status.HTTP_200_OK, response.text
    entities = response.json()["entities"]
    assert list(entities) == ["Q42", "Q1", "../Q42"]
    assert entities["Q1"] == {"id": "Q1", "missing": ""}
    assert entities["../Q42"] == {"id": "../Q42", "missing": ""}


def test_get_wikidata_entities_without_ids(client: TestClient) -> None:
    response = client.get(
        "/v0/wikidata/w/api.php", params={"action": "wbgetentities", "format": "json"}
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {"entities": {}}
