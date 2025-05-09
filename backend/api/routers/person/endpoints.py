import typing

from fastapi import APIRouter, Body, HTTPException, Path, status
from loguru import logger

from backend.api.routers.person.models import request_models, response_models
from backend.api.routers.person.swagger_examples import (
    request_examples,
    response_examples,
)
from backend.database import postgres as db_model
from backend.database.postgres.session import DBSessionDep

router = APIRouter(prefix="/person", tags=["person"])


@router.get(
    "/{person_id}",
    status_code=status.HTTP_200_OK,
    response_model=response_models.PersonResponse,
    responses={
        200: {
            "description": "Person Retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "person_id": 1,
                        "name": "Jane",
                        "last_name": "Smith",
                        "age": 30,
                        "start_date": "1995-05-09T00:00:00+00:00",
                        "end_date": None,
                        "description": "An inspiring leader.",
                    }
                }
            },
        },
        404: {
            "description": "Person Not Found",
            "content": {
                "application/json": {"example": {"detail": "Person not found"}}
            },
        },
        400: {
            "description": "Invalid Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve person"}
                }
            },
        },
    },
)
async def get_person(
    session: DBSessionDep,
    person_id: typing.Annotated[
        int,
        Path(
            ...,
            ge=1,
            description="Unique identifier of the person to retrieve.",
            openapi_examples=response_examples.person_id_examples,
        ),
    ],
) -> response_models.PersonResponse:
    """
    Retrieve a person by ID.

    :param session: Database session dependency.
    :type session: DBSessionDep
    :param person_id: Unique identifier of the person to retrieve.
    :type person_id: int
    :return: Details of the retrieved person.
    :rtype: PersonResponse
    :raises HTTPException:
        - 400: Invalid request or database error.
        - 404: Person not found.
    """
    try:
        db_person = await session.get(db_model.person_models.Person, person_id)
    except Exception as exc_info:
        logger.error(f"Error deleting person: {str(exc_info)}")
        raise HTTPException(
            status_code=400,
            detail="Failed to retrieve person",
        )
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    logger.debug(f"Retrieved person with ID: {person_id}")
    return db_person


@router.delete(
    "/{person_id}",
    status_code=status.HTTP_200_OK,
    response_model=response_models.PersonDeleteResponse,
    responses={
        200: {
            "description": "Person Deleted",
            "content": {"application/json": {"example": {"person_id": 1}}},
        },
        404: {
            "description": "Person Not Found",
            "content": {
                "application/json": {"example": {"detail": "Person not found"}}
            },
        },
    },
)
async def delete_person(
    session: DBSessionDep,
    person_id: typing.Annotated[
        int,
        Path(
            ...,
            ge=1,
            description="Unique identifier of the person to delete.",
            openapi_examples=response_examples.person_id_examples,
        ),
    ],
) -> response_models.PersonDeleteResponse:
    """
    Delete a person by ID.

    :param session: Database session dependency.
    :type session: DBSessionDep
    :param person_id: Unique identifier of the person to delete.
    :type person_id: int
    :return: ID of the deleted person.
    :rtype: PersonDeleteResponse
    :raises HTTPException:
        - 400: Invalid request or database error.
        - 404: Person not found.
    """
    db_person = await session.get(db_model.person_models.Person, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    await session.delete(db_person)
    try:
        await session.commit()
    except Exception as exc_info:
        logger.error(f"Error deleting person: {str(exc_info)}")
        raise HTTPException(status_code=400, detail="Failed to delete person")
    await session.flush()
    logger.debug(f"Deleted person with ID: {person_id}")
    return response_models.PersonDeleteResponse.model_validate(db_person)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Person Created",
            "content": {
                "application/json": {
                    "example": {
                        "person_id": 1,
                        "name": "Jane",
                        "last_name": "Smith",
                        "age": 30,
                        "start_date": "1995-05-09T00:00:00+00:00",
                        "description": "An inspiring leader.",
                    }
                }
            },
        },
        404: {
            "description": "Person Not Found",
            "content": {
                "application/json": {"example": {"detail": "Person not found"}}
            },
        },
    },
)
async def create_person(
    session: DBSessionDep,
    person: typing.Annotated[
        request_models.PersonCreate,
        Body(
            ...,
            openapi_examples=request_examples.person,
        ),
    ],
) -> response_models.PersonResponse:
    """
    Create a new person.

    :param session: The database session dependency used to interact with db.
    :type session: DBSessionDep
    :param person: The person data to create.
    :type person: PersonCreate
    :return: A JSON response containing the ID of the created person.
    :rtype: PersonResponse
    :raises HTTPException:
        - 400: If any parameters are invalid.
        - 422: If validation fails.
    """
    db_person = db_model.person_models.Person(
        name=person.name,
        last_name=person.last_name,
        age=person.age,
        start_date=person.start_date,
        end_date=person.end_date,
        description=person.description,
    )
    await session.add(db_person)
    try:
        await session.commit()
    except Exception as exc_info:
        await session.rollback()
        logger.error(f"Error creating person: {str(exc_info)}")
        raise HTTPException(status_code=400, detail="Failed to create person")
    await session.refresh(db_person)

    logger.debug(f"Created person: {db_person.model_dump()}")
    return db_person
