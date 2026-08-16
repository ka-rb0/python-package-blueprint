"""
Console-script entry point - see `[project.scripts]` in pyproject.toml.

Configures logging (see logging_config) and prints the greeting - the
command's actual output - to stdout. The two stay separate on purpose so
`example-package greet Ada` stays pipeable and diagnostics don't pollute it.
"""

import argparse
import logging
import sys

from example_package.core import greet
from example_package.logging_config import configure_logging

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="example-package")
    subparsers = parser.add_subparsers(dest="command", required=True)

    greet_parser = subparsers.add_parser("greet", help="print a greeting")
    greet_parser.add_argument("name", help="who to greet")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point installed as the `example-package` console script."""
    configure_logging()
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
