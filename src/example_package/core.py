"""Business logic for the example package - plain functions, no I/O."""


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
