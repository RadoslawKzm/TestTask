from datetime import datetime

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field, model_validator

from backend.api.routers.person.swagger_examples import request_examples


class PersonCreate(BaseModel):
    name: str = Field(
        ...,
        pattern=r"^[A-Za-z\s-]+$",
        min_length=1,
        max_length=32,
        description="Name of the person (max 32 characters).",
    )
    last_name: str = Field(
        ...,
        pattern=r"^[A-Za-z\s-]+$",
        min_length=1,
        max_length=32,
        description="Last name of the person (max 32 characters).",
    )
    age: int = Field(
        ..., ge=0, le=150, description="Age of the person (0-999)."
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

    model_config = {
        "json_schema_extra": {"examples": [request_examples.person]},
    }

    @model_validator(mode="after")
    def validate_dates_and_age(cls, values):
        name = values.name.strip()
        last_name = values.last_name.strip()
        start_date = values.start_date
        end_date = values.end_date
        age = values.age
        description = values.description

        if not name:
            raise ValueError(
                "Name cannot be empty or consist only of whitespace."
            )
        if not last_name:
            raise ValueError(
                "Name cannot be empty or consist only of whitespace."
            )

        # Ensure start_date is not in the future
        if start_date > datetime.now():
            raise ValueError("start_date cannot be in the future")

        # Validate end_date if provided
        if end_date is not None:
            if end_date < start_date:
                raise ValueError("end_date cannot be before start_date")
            if end_date > datetime.now():
                raise ValueError("end_date cannot be in the future")

        # Calculate age
        reference_date = end_date if end_date is not None else datetime.now()
        precise_years = relativedelta(reference_date, start_date).years
        if precise_years != age:
            raise ValueError(
                f"Age ({age}) does not match the difference between end_date"
                f" (or current date) and start_date ({precise_years} years)"
            )

        if description is not None:
            values.description = values.description.strip()
            if not values.description:
                raise ValueError("Description cannot be empty or whitespace")
        return values
