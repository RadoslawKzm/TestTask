import typing

person: dict[str, dict[str, str | dict | typing.Any]] = {
    "deceased_person": {
        "summary": "Deceased Person",
        "description": (
            "A person who has passed away, "
            "with full details including description."
        ),
        "value": {
            "name": "John",
            "last_name": "Doe",
            "age": 84,
            "start_date": "1920-05-18T00:00:00",
            "end_date": "2005-04-02T00:00:00",
            "description": "A remarkable individual known for simplicity.",
        },
    },
    "living_person": {
        "summary": "Living Person",
        "description": (
            "A person who is still alive, " "with end_date set to null."
        ),
        "value": {
            "name": "Jane",
            "last_name": "Smith",
            "age": 30,
            "start_date": "1995-05-09T00:00:00",
            "end_date": None,
            "description": "An inspiring leader.",
        },
    },
    "minimal_request": {
        "summary": "Minimal Request",
        "description": (
            "A minimal valid request, "
            "with only required fields and no description."
        ),
        "value": {
            "name": "Alex",
            "last_name": "Brown",
            "age": 25,
            "start_date": "2000-01-15T00:00:00",
            "end_date": None,
            "description": None,
        },
    },
}
