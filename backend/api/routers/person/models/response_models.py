from datetime import datetime

from pydantic import BaseModel, Field


class PersonResponse(BaseModel):
    person_id: int
    name: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Name of the person (max 32 characters).",
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Last name of the person (max 32 characters).",
    )
    age: int = Field(
        ..., ge=0, le=999, description="Age of the person (0-999)."
    )
    start_date: datetime = Field(
        ..., description="Date of birth in ISO 8601 format."
    )
    end_date: datetime | None = Field(
        None,
        description="Date of decease in ISO 8601 format, or None if alive.",
    )
    description: str | None = Field(
        None,
        max_length=100,
        description="Optional description (max 100 characters).",
    )


class PersonDeleteResponse(BaseModel):
    person_id: int = Field(
        ...,
        description="Unique identifier of the deleted person",
    )

    model_config = {"from_attributes": True}
