"""Tests for example_package.core."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from example_package.core import greet


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
