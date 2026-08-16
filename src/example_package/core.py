"""Business logic for the example package - plain functions, no I/O."""

from pydantic import BaseModel, EmailStr, PositiveInt, ValidationError


class Person(BaseModel):
    """A person record: the shape :func:`parse_person` validates against."""

    name: str
    age: PositiveInt
    email: EmailStr


def parse_person(data: str | bytes | bytearray) -> Person:
    """
    Validate a JSON document against :class:`Person` and return the model.

    Args:
        data: A JSON document (text or raw bytes) expected to be an object
            with ``name``, ``age`` and ``email`` keys.

    Returns:
        The parsed :class:`Person`, with ``age`` coerced to an ``int`` and
        ``email`` checked for syntactic validity.

    Raises:
        ValidationError: If *data* is not valid JSON, or does not match the
            :class:`Person` shape. The error lists every offending field, so
            prefer this over :func:`is_person` when you need to tell the
            caller *what* was wrong.
    """
    return Person.model_validate_json(data)


def is_person(data: str | bytes | bytearray) -> bool:
    """
    Report whether a JSON document matches the :class:`Person` shape.

    Args:
        data: A JSON document (text or raw bytes).

    Returns:
        ``True`` if *data* parses as a :class:`Person`, ``False`` otherwise.
        Use :func:`parse_person` instead when you want the parsed model or
        the reason validation failed.
    """
    try:
        parse_person(data)
    except ValidationError:
        return False
    return True


def greet(name: str) -> str:
    """
    Return a friendly greeting for *name*.

    Args:
        name: Who to greet. Leading/trailing whitespace is stripped; a name
            that is empty after stripping is rejected.

    Returns:
        A greeting string, e.g. ``"Hello, Ada!"``.

    Raises:
        ValueError: If *name* is empty or only whitespace.
    """
    name = name.strip()
    if not name:
        raise ValueError("name must not be empty")
    return f"Hello, {name}!"
