"""
Example package: the sample code this blueprint ships with.

Delete this package (and its tests/) once you have real code to replace it
with - it exists to prove the toolchain works end to end and to show the
project layout a package built from this blueprint is expected to follow.
"""

from importlib.metadata import PackageNotFoundError, version

from example_package.core import Person, greet, is_person, parse_person

try:
    __version__ = version("python-package-blueprint")
except PackageNotFoundError:  # pragma: no cover - only if the package isn't installed
    __version__ = "0.0.0"

__all__ = ["Person", "__version__", "greet", "is_person", "parse_person"]
