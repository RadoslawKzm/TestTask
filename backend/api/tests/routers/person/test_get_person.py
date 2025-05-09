from datetime import datetime
from unittest.mock import AsyncMock

import fastapi
import pytest
from fastapi.testclient import TestClient

from backend.database.postgres.person_models import Person

# Test data
valid_person_id = 1
non_existent_person_id = 999
valid_person_data = {
    "person_id": valid_person_id,
    "name": "Jane",
    "last_name": "Smith",
    "age": 30,
    "start_date": "1995-05-09T00:00:00",
    "end_date": None,
    "description": "An inspiring leader.",
}


@pytest.fixture
def mock_session(mocker):
    async_mock = AsyncMock()
    async_mock.__aenter__.return_value = async_mock
    async_mock.__aexit__.return_value = None  # Mock the context manager exit
    mocker.patch(
        "backend.database.postgres.session.DbContext",
        return_value=async_mock,
    )
    return async_mock


@pytest.mark.asyncio
async def test_get_person(mock_session, sync_client: TestClient):
    status_code = fastapi.status.HTTP_200_OK
    person_id = valid_person_id

    # Mock the Person object returned by session.get
    mock_person = Person(
        person_id=person_id,
        name=valid_person_data["name"],
        last_name=valid_person_data["last_name"],
        age=valid_person_data["age"],
        start_date=datetime.fromisoformat(valid_person_data["start_date"]),
        end_date=None,
        description=valid_person_data["description"],
    )

    # Mock session methods
    mock_session.get = AsyncMock(return_value=mock_person)

    response = sync_client.get(
        url=f"/person/{person_id}",
    )

    assert response.status_code == status_code
    mock_session.get.assert_called_once_with(Person, person_id)

    # Verify response matches PersonResponse
    assert response.json() == valid_person_data


@pytest.mark.asyncio
async def test_get_person_not_found(mock_session, sync_client: TestClient):
    person_id = non_existent_person_id

    # Mock session.get to return None (person not found)
    mock_session.get = AsyncMock(return_value=None)

    response = sync_client.get(
        url=f"/person/{person_id}",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}
    mock_session.get.assert_called_once_with(Person, person_id)


@pytest.mark.asyncio
async def test_get_person_db_error(mock_session, sync_client: TestClient):
    person_id = valid_person_id

    # Mock session.get to raise an exception
    mock_session.get = AsyncMock(
        side_effect=Exception("Database connection error")
    )

    response = sync_client.get(url=f"/person/{person_id}")

    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to retrieve person"}
    mock_session.get.assert_called_once_with(Person, person_id)


def test_get_person_invalid_id(sync_client: TestClient):
    response = sync_client.get(url="/person/-1")
    assert response.status_code == 422
    assert response.json()["detail"] == "Request validation failed"
    assert (
        response.json()["message"]
        == "Input should be greater than or equal to 1"
    )


@pytest.mark.asyncio
async def test_get_person_with_end_date(mock_session, sync_client: TestClient):
    person_id = 2
    person_data = {
        "person_id": person_id,
        "name": "John",
        "last_name": "Doe",
        "age": 84,
        "start_date": "1920-05-18T00:00:00",
        "end_date": "2005-04-02T00:00:00",
        "description": "A remarkable individual.",
    }
    mock_person = Person(
        person_id=person_id,
        name=person_data["name"],
        last_name=person_data["last_name"],
        age=person_data["age"],
        start_date=datetime.fromisoformat(person_data["start_date"]),
        end_date=datetime.fromisoformat(person_data["end_date"]),
        description=person_data["description"],
    )
    mock_session.get = AsyncMock(return_value=mock_person)
    response = sync_client.get(url=f"/person/{person_id}")
    assert response.status_code == 200
    assert response.json() == person_data
