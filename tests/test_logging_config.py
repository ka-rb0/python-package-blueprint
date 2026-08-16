"""Tests for example_package.logging_config."""

import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from example_package.logging_config import JsonFormatter, configure_logging


def make_record(
    msg: object = "hello",
    args: tuple[object, ...] | None = None,
    *,
    level: int = logging.INFO,
    exc_info: Any = None,
    stack_info: str | None = None,
    extra: Mapping[str, object] | None = None,
) -> logging.LogRecord:
    """Build a LogRecord the way logging.Logger.makeRecord would."""
    record = logging.LogRecord(
        name="tests.example",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=exc_info,
        sinfo=stack_info,
    )
    record.__dict__.update(extra or {})
    return record


def render(record: logging.LogRecord) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(JsonFormatter().format(record))
    return payload


def test_renders_the_documented_fields() -> None:
    payload = render(make_record())
    payload.pop("timestamp")  # covered by its own test below

    assert payload == {
        "level": "INFO",
        "logger": "tests.example",
        "message": "hello",
    }


def test_json_metacharacters_do_not_break_the_line() -> None:
    # The regression this formatter exists for: string interpolation produced
    # `{"message": "bad "quoted" value\with backslash"}`, which is not JSON.
    message = 'bad "quoted" value\\with backslash\nand a newline'

    assert render(make_record(message))["message"] == message


@given(message=st.text())
def test_any_message_survives_the_round_trip(message: str) -> None:
    assert render(make_record(message))["message"] == message


def test_deferred_arguments_are_interpolated() -> None:
    assert render(make_record("greeting %s %d", ("Ada", 1)))["message"] == (
        "greeting Ada 1"
    )


def test_timestamp_is_rfc3339_utc() -> None:
    record = make_record()

    timestamp = datetime.fromisoformat(render(record)["timestamp"])

    assert timestamp.tzinfo == UTC
    # Truncated to milliseconds, so it trails record.created by under one.
    assert 0 <= record.created - timestamp.timestamp() < 0.001


def test_exception_is_included_when_present() -> None:
    try:
        raise ValueError("boom")
    except ValueError as exc:
        record = make_record(exc_info=(type(exc), exc, exc.__traceback__))

    assert "ValueError: boom" in render(record)["exception"]


def test_stack_is_included_when_present() -> None:
    assert render(make_record(stack_info="Stack (most recent call last):"))[
        "stack"
    ].startswith("Stack")


def test_extra_fields_are_nested_under_extra() -> None:
    record = make_record(extra={"request_id": "abc123", "attempt": 2})

    assert render(record)["extra"] == {"request_id": "abc123", "attempt": 2}


def test_extra_cannot_shadow_a_standard_field() -> None:
    # logging.Logger.makeRecord already rejects an `extra` key that collides
    # with a LogRecord attribute, so the only names left to defend are this
    # formatter's own - which is why extras get nested instead of merged.
    shadows = {"timestamp": "nope", "level": "nope", "logger": "nope"}

    payload = render(make_record(extra=shadows))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "tests.example"
    assert payload["timestamp"] != "nope"
    assert payload["extra"] == shadows


def test_unencodable_extra_falls_back_to_its_string_form() -> None:
    record = make_record(extra={"opaque": object.__new__(object)})

    assert render(record)["extra"]["opaque"].startswith("<object object at")


def test_text_format_is_the_default(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging()

    logging.getLogger("tests.example").info("plain")

    assert capsys.readouterr().err == "INFO tests.example: plain\n"


def test_json_format_is_selected_by_the_env_var(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LOG_FORMAT", "JSON")  # case-insensitive

    configure_logging()
    logging.getLogger("tests.example").info("structured")

    assert json.loads(capsys.readouterr().err)["message"] == "structured"


def test_level_comes_from_the_env_var(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LOG_LEVEL", "debug")  # case-insensitive

    configure_logging()
    logging.getLogger("tests.example").debug("chatty")

    assert "chatty" in capsys.readouterr().err


def test_unknown_level_warns_and_falls_back(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LOG_LEVEL", "verbose")

    configure_logging()
    logging.getLogger("tests.example").debug("dropped at INFO")

    stderr = capsys.readouterr().err
    assert "unknown LOG_LEVEL 'VERBOSE' - using INFO" in stderr
    assert "dropped at INFO" not in stderr


def test_unknown_format_warns_and_falls_back(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LOG_FORMAT", "logfmt")

    configure_logging()

    assert capsys.readouterr().err == (
        "WARNING example_package.logging_config: unknown LOG_FORMAT 'logfmt' - "
        "using text\n"
    )
