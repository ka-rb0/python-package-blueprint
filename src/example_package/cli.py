"""
Console-script entry point - see `[project.scripts]` in pyproject.toml.

Configures logging from LOG_LEVEL / LOG_FORMAT (the env vars
.devcontainer/docker-compose.yml already sets) and prints the greeting - the
command's actual output - to stdout. The two stay separate on purpose so
`example-package greet Ada` stays pipeable and diagnostics don't pollute it.
"""

import argparse
import logging
import os
import sys

from example_package.core import greet

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    fmt = os.environ.get("LOG_FORMAT", "text").lower()
    if fmt == "json":
        message_format = (
            '{"level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
        )
    else:
        message_format = "%(levelname)s %(name)s: %(message)s"
    # force=True: safe to call more than once per process (e.g. in tests),
    # each call rebinds the handler to the current sys.stderr.
    logging.basicConfig(
        level=level, format=message_format, stream=sys.stderr, force=True
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="example-package")
    subparsers = parser.add_subparsers(dest="command", required=True)

    greet_parser = subparsers.add_parser("greet", help="print a greeting")
    greet_parser.add_argument("name", help="who to greet")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point installed as the `example-package` console script."""
    _configure_logging()
    args = _build_parser().parse_args(argv)

    if args.command == "greet":
        try:
            message = greet(args.name)
        except ValueError as exc:
            logger.error("%s", exc)
            return 1
        print(message)  # noqa: T201 - stdout *is* this command's output
        return 0

    return 1  # pragma: no cover - unreachable, argparse enforces `command`


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
