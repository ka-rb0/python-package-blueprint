"""Tests for the `example-package` console script."""

import json

import pytest

from example_package.cli import main


def test_greet_prints_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["greet", "Ada"])

    assert exit_code == 0
    assert capsys.readouterr().out == "Hello, Ada!\n"


def test_greet_rejects_blank_name(capsys: pytest.CaptureFixture[str]) -> None:
    # capsys, not caplog: _configure_logging's force=True rebinds the root
    # handler to the live sys.stderr on every call, which drops caplog's own
    # handler - exercising that reconfigurability is the point of force=True.
    exit_code = main(["greet", "   "])

    assert exit_code == 1
    assert "name must not be empty" in capsys.readouterr().err


def test_error_is_logged_as_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LOG_FORMAT", "json")

    exit_code = main(["greet", "   "])

    assert exit_code == 1
    record = json.loads(capsys.readouterr().err.strip())
    assert record == {
        "level": "ERROR",
        "name": "example_package.cli",
        "message": "name must not be empty",
    }
