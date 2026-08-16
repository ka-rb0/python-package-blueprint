"""Tests for example_package.core."""

import json

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from example_package.core import Person, greet, is_person, parse_person

VALID_PERSON_JSON = '{"name": "Ada", "age": 36, "email": "ada@example.com"}'


def test_greet_formats_the_name() -> None:
    assert greet("Ada") == "Hello, Ada!"


def test_greet_strips_surrounding_whitespace() -> None:
    assert greet("  Bob  ") == "Hello, Bob!"


@pytest.mark.parametrize("blank", ["", "   ", "\t\n"])
def test_greet_rejects_blank_names(blank: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        greet(blank)


@given(name=st.text(min_size=1).filter(lambda s: s.strip()))
def test_greet_always_wraps_the_stripped_name(name: str) -> None:
    assert greet(name) == f"Hello, {name.strip()}!"


def test_parse_person_returns_the_model() -> None:
    person = parse_person(VALID_PERSON_JSON)
    assert person == Person(name="Ada", age=36, email="ada@example.com")


def test_parse_person_accepts_bytes() -> None:
    assert parse_person(VALID_PERSON_JSON.encode()).name == "Ada"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("age", 0),  # PositiveInt rejects zero ...
        ("age", -1),  # ... and negatives
        ("age", "old"),  # and anything non-numeric
        ("email", "not-an-email"),  # EmailStr wants a real address
        ("name", None),  # str is required, not optional
    ],
)
def test_parse_person_rejects_bad_fields(field: str, value: object) -> None:
    payload = json.loads(VALID_PERSON_JSON) | {field: value}
    with pytest.raises(ValidationError) as excinfo:
        parse_person(json.dumps(payload))
    assert excinfo.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize(
    "payload",
    [
        '{"name": "Ada", "age": 36}',  # missing email
        "{}",  # missing everything
        '["Ada", 36, "ada@example.com"]',  # right values, wrong container
        "not json at all",
    ],
)
def test_parse_person_rejects_wrong_shapes(payload: str) -> None:
    with pytest.raises(ValidationError):
        parse_person(payload)


def test_is_person_accepts_the_right_shape() -> None:
    assert is_person(VALID_PERSON_JSON) is True


@pytest.mark.parametrize(
    "payload",
    [
        '{"name": "Ada", "age": -1, "email": "ada@example.com"}',
        '{"name": "Ada", "age": 36, "email": "nope"}',
        '{"name": "Ada", "age": 36}',
        "not json at all",
    ],
)
def test_is_person_rejects_anything_else(payload: str) -> None:
    assert is_person(payload) is False
