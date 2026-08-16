"""Fixtures shared by the whole suite - pytest picks this file up by name."""

import logging
from collections.abc import Iterator

import pytest

from example_package.logging_config import HANDLER_NAME


@pytest.fixture(autouse=True)
def reset_logging() -> Iterator[None]:
    """
    Undo what a test's `configure_logging()` call left on the root logger.

    Its handler holds the `sys.stderr` capsys swapped in for that one test, and
    the root level it set would otherwise decide what later tests log. Only
    handlers this package installed are touched - pytest's own (caplog,
    `--log-file`) are left alone, so both keep working.
    """
    root = logging.getLogger()
    level = root.level
    yield
    for handler in root.handlers[:]:
        if handler.name == HANDLER_NAME:
            root.removeHandler(handler)
            handler.close()
    root.setLevel(level)
