"""Fixtures shared by the whole suite - pytest picks this file up by name."""

import logging
from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def restore_root_logger() -> Iterator[None]:
    """
    Undo whatever a test did to the root logger.

    `configure_logging` calls `logging.basicConfig(force=True)`, which closes
    and drops every existing root handler - including the one pytest's own
    logging plugin installs for caplog. Without this, the first test to
    configure logging would quietly change how every later test sees log
    output, and the order tests happen to run in would start to matter.
    """
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield
    root.handlers[:] = handlers
    root.setLevel(level)
