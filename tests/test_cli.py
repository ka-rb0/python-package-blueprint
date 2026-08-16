"""Tests for the `example-package` console script."""

import json

import pytest

from example_package.cli import main


def test_greet_prints_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["greet", "Ada"])

    assert exit_code == 0
    assert capsys.readouterr().out == "Hello, Ada!\n"


def test_greet_rejects_blank_name(capsys: pytest.CaptureFixture[str]) -> None:
    # capsys, not caplog: configure_logging's force=True rebinds the root
    # handler to the live sys.stderr on every call, which drops caplog's own
    # handler - exercising that reconfigurability is the point of force=True.
    exit_code = main(["greet", "   "])

    assert exit_code == 1
    assert "name must not be empty" in capsys.readouterr().err


def test_errors_reach_stderr_as_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The formatter has its own tests (tests/test_logging_config.py); this one
    # only checks that the CLI wires LOG_FORMAT through to it.
    monkeypatch.setenv("LOG_FORMAT", "json")

    exit_code = main(["greet", "   "])

    assert exit_code == 1
    record = json.loads(capsys.readouterr().err)
    assert record["level"] == "ERROR"
    assert record["logger"] == "example_package.cli"
    assert record["message"] == "name must not be empty"
