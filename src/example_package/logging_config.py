"""
Logging setup - one text format for humans, one JSON format for pipelines.

`configure_logging` reads LOG_LEVEL and LOG_FORMAT (the env vars
.devcontainer/docker-compose.yml already sets) and points the root logger at
stderr. Nothing here writes to stdout: that stream belongs to whatever the
command actually outputs, so `example-package greet Ada` stays pipeable.
"""

import json
import logging
import os
import sys
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import Any, Final

_DEFAULT_LEVEL: Final = "INFO"
_DEFAULT_FORMAT: Final = "text"

# No timestamp: text logs are for a terminal that is already showing "now",
# and for a container whose collector stamps each line on capture anyway.
# JSON records carry their own - see JsonFormatter - because they outlive the
# stream they were written to.
_TEXT_FORMAT: Final = "%(levelname)s %(name)s: %(message)s"

# Every attribute a LogRecord already carries, probed from a throwaway record
# so the set tracks the running interpreter rather than drifting as CPython
# adds fields (`taskName` arrived in 3.12). `message` and `asctime` are not on
# a fresh record - logging.Formatter adds them - so they are named here.
# Anything on a record outside this set came from a caller's
# `logger.info(..., extra={...})`.
_RESERVED_ATTRS: Final = frozenset(
    logging.LogRecord("", logging.NOTSET, "", 0, "", None, None).__dict__
) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    """
    Render each record as one JSON object on one line.

    Always emits `timestamp` (RFC 3339, UTC), `level`, `logger` and `message`;
    adds `exception` and `stack` when the record carries them, and `extra` for
    anything passed as `logger.info(..., extra={...})`. Extras are nested
    under one key rather than merged into the top level so that a caller's
    stray `extra={"level": ...}` cannot shadow a field a log query relies on.

    Building a dict and handing it to `json.dumps` - rather than interpolating
    values into a format string - is the whole point: a message containing a
    quote, a backslash or a newline stays valid JSON.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "logger": record.name,
            # getMessage(), not record.msg: applies the `logger.info("%s", x)`
            # arguments that lazy formatting deferred until now.
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        extra = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _RESERVED_ATTRS
        }
        if extra:
            payload["extra"] = extra
        # default=str: an exception raised in here is swallowed by logging and
        # reported as a handler error, losing the record - so stringify an
        # extra that json can't encode instead of failing on it.
        # ensure_ascii stays on (the default): \uXXXX escapes decode back to
        # the original text and keep the line writable on a non-UTF-8 stream.
        return json.dumps(payload, default=str)


_FORMATTERS: Final[Mapping[str, Callable[[], logging.Formatter]]] = {
    "text": lambda: logging.Formatter(_TEXT_FORMAT),
    "json": JsonFormatter,
}

logger = logging.getLogger(__name__)

# Our handler on the root logger is tagged with this so a later call can find
# and replace exactly the one we installed - see configure_logging.
HANDLER_NAME: Final = "example_package"


def configure_logging() -> None:
    """
    Send the root logger to stderr, shaped by LOG_LEVEL and LOG_FORMAT.

    An unrecognized value in either variable falls back to the default and
    logs a warning saying so - a typo shouldn't take the command down with a
    traceback, nor pass silently and leave someone reading logs at the wrong
    level or in the wrong shape.

    Safe to call more than once per process: each call replaces the handler
    the previous one installed, rebinding to the current sys.stderr.

    Deliberately not `logging.basicConfig(force=True)`. That closes every
    handler already on the root logger, including ones this package did not
    install, and a closed handler is not merely detached - a `mode="w"`
    FileHandler refuses to reopen, so it silently drops every record from
    then on. Anything importing this module (a host application, a test
    runner) would lose its own logging with no error. Own only what you
    installed.
    """
    levels = logging.getLevelNamesMapping()
    level_name = os.environ.get("LOG_LEVEL", _DEFAULT_LEVEL).upper()
    format_name = os.environ.get("LOG_FORMAT", _DEFAULT_FORMAT).lower()

    root = logging.getLogger()
    for installed in root.handlers[:]:
        if installed.name == HANDLER_NAME:
            root.removeHandler(installed)
            installed.close()

    handler = logging.StreamHandler(sys.stderr)
    handler.set_name(HANDLER_NAME)
    handler.setFormatter(_FORMATTERS.get(format_name, _FORMATTERS[_DEFAULT_FORMAT])())
    root.addHandler(handler)
    root.setLevel(levels.get(level_name, levels[_DEFAULT_LEVEL]))

    # After the handler is installed, so these go through it.
    if level_name not in levels:
        logger.warning("unknown LOG_LEVEL %r - using %s", level_name, _DEFAULT_LEVEL)
    if format_name not in _FORMATTERS:
        logger.warning("unknown LOG_FORMAT %r - using %s", format_name, _DEFAULT_FORMAT)
