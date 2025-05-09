from datetime import datetime
from typing import Optional

from sqlmodel import Field, Index, SQLModel


class Person(SQLModel, table=True):
    person_id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(max_length=32, nullable=False, index=True)
    last_name: str = Field(max_length=32, nullable=False, index=True)
    age: int = Field(default=0, nullable=False)
    start_date: datetime = Field(nullable=False)
    end_date: datetime = Field(nullable=True)
    description: Optional[str] = Field(nullable=True, default=None)

    __table_args__ = (Index("ix_person_name_lastname", "name", "last_name"),)
