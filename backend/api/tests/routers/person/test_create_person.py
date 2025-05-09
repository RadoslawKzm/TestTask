from unittest.mock import AsyncMock, Mock

import fastapi
import pytest
from fastapi.testclient import TestClient

# Test data
valid_person_data = {
    "name": "Jane",
    "last_name": "Smith",
    "age": 30,
    "start_date": "1995-05-09T00:00:00",
    "end_date": None,
    "description": "An inspiring leader.",
}

invalid_person_data = {
    "name": "NameOver32CharactersForTestingStuffLong",
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
    async_mock.__aexit__.return_value = None
    mocker.patch(
        "backend.database.postgres.session.DbContext",
        return_value=async_mock,
    )
    return async_mock


@pytest.mark.asyncio
async def test_create_person(mock_session, mocker, sync_client: TestClient):
    status_code = fastapi.status.HTTP_201_CREATED
    person_id = 1

    mock_session.add = Mock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock(
        side_effect=lambda obj: setattr(obj, "person_id", person_id)
    )

    response = sync_client.post(
        url="/person/",
        json=valid_person_data,
    )

    assert response.status_code == status_code
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

    assert response.json() == {
        "person_id": person_id,
        "name": valid_person_data["name"],
        "last_name": valid_person_data["last_name"],
        "age": valid_person_data["age"],
        "start_date": valid_person_data["start_date"],
        "end_date": None,
        "description": valid_person_data["description"],
    }


def test_create_person_name_too_long(sync_client: TestClient):
    response = sync_client.post(
        url="/person/",
        json=invalid_person_data,
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Request validation failed",
        "message": "String should have at most 32 characters",
    }


def test_create_person_invalid_age(sync_client: TestClient):
    invalid_data = valid_person_data.copy()
    invalid_data["age"] = -1
    response = sync_client.post(url="/person/", json=invalid_data)
    assert response.status_code == 422
    assert response.json()["detail"] == "Request validation failed"
    assert (
        response.json()["message"]
        == "Input should be greater than or equal to 0"
    )


def test_create_person_future_start_date(sync_client: TestClient):
    invalid_data = valid_person_data.copy()
    invalid_data["start_date"] = "2026-01-01T00:00:00"
    response = sync_client.post(url="/person/", json=invalid_data)
    assert response.status_code == 422
    assert response.json()["detail"] == "Request validation failed"
    assert (
        response.json()["message"]
        == "Value error, start_date cannot be in the future"
    )


@pytest.mark.asyncio
async def test_create_person_db_error(mock_session, sync_client: TestClient):
    mock_session.add = Mock()
    mock_session.commit = AsyncMock(side_effect=Exception("Database error"))
    response = sync_client.post(url="/person/", json=valid_person_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to create person"}


@pytest.mark.asyncio
async def test_create_person_invalid_input(sync_client: TestClient):
    invalid_person = {
        "name": "",  # Empty name
        "last_name": "Smith",
        "age": 30,
        "start_date": "2026-01-01T00:00:00+00:00",  # Future date
        "end_date": None,
        "description": "Invalid input",
    }
    response = sync_client.post("/person/", json=invalid_person)
    assert response.status_code == 422
    assert "detail" in response.json()
