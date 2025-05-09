from datetime import datetime
from unittest.mock import AsyncMock

import fastapi
import pytest
from fastapi.testclient import TestClient

from backend.database.postgres.person_models import Person

# Test data
valid_person_id = 1
non_existent_person_id = 999


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
async def test_delete_person(mock_session, mocker, sync_client: TestClient):
    status_code = fastapi.status.HTTP_200_OK
    person_id = valid_person_id

    # Mock the Person object returned by session.get
    mock_person = Person(
        person_id=person_id,
        name="Jane",
        lastname="Smith",
        age=30,
        start_date=datetime(1995, 5, 9),
        end_date=None,
        description="An inspiring leader.",
    )

    # Mock session methods
    mock_session.get = AsyncMock(return_value=mock_person)
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.flush = AsyncMock()

    response = sync_client.delete(
        url=f"/person/{person_id}",
    )

    assert response.status_code == status_code
    mock_session.get.assert_called_once_with(Person, person_id)
    mock_session.delete.assert_called_once_with(mock_person)
    mock_session.commit.assert_called_once()
    mock_session.flush.assert_called_once()

    # Verify response matches PersonDeleteResponse
    assert response.json() == {"person_id": person_id}


@pytest.mark.asyncio
async def test_delete_person_not_found(mock_session, sync_client: TestClient):
    person_id = non_existent_person_id

    # Mock session.get to return None (person not found)
    mock_session.get = AsyncMock(return_value=None)

    response = sync_client.delete(
        url=f"/person/{person_id}",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}
    mock_session.get.assert_called_once_with(Person, person_id)
    # Ensure no delete, commit, or flush calls were made
    assert (
        not hasattr(mock_session, "delete") or not mock_session.delete.called
    )
    assert (
        not hasattr(mock_session, "commit") or not mock_session.commit.called
    )
    assert not hasattr(mock_session, "flush") or not mock_session.flush.called


@pytest.mark.asyncio
async def test_delete_person_db_error(mock_session, sync_client: TestClient):
    person_id = valid_person_id
    mock_person = Person(
        person_id=person_id,
        name="Jane",
        lastname="Smith",
        age=30,
        start_date=datetime.now(),
    )
    mock_session.get = AsyncMock(return_value=mock_person)
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock(
        side_effect=Exception("Foreign key constraint")
    )
    response = sync_client.delete(url=f"/person/{person_id}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to delete person"}
    mock_session.get.assert_called_once_with(Person, person_id)
    mock_session.delete.assert_called_once_with(mock_person)
    mock_session.commit.assert_called_once()


def test_delete_person_invalid_id(sync_client: TestClient):
    response = sync_client.delete(url="/person/-1")
    assert response.status_code == 422  # Assuming middleware validates ge=1
    assert response.json()["detail"] == "Request validation failed"
    assert (
        response.json()["message"]
        == "Input should be greater than or equal to 1"
    )
