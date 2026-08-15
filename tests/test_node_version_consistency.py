"""
Guards a promise made in .devcontainer/Dockerfile's comments.

The pinned Node base image's major version must match package.json's
`engines.node`, since scripts/lib.sh puts /opt/npm-tools' npm CLI (built
against that image) on PATH for tools installed per package-lock.json.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def test_node_major_version_matches_dockerfile() -> None:
    package_json = json.loads((REPO_ROOT / "package.json").read_text())
    engines_major = package_json["engines"]["node"].split(".")[0]

    dockerfile = (REPO_ROOT / ".devcontainer" / "Dockerfile").read_text()
    match = re.search(r"FROM node:(\d+)-slim@sha256:\w+ AS node", dockerfile)
    assert match is not None, (
        "couldn't find the pinned node base image in the Dockerfile"
    )

    assert match.group(1) == engines_major
