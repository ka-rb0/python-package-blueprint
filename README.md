# Python Package Blueprint (with an Agent-Ready Development Environment)

A template for starting a new Python package: `src/`-layout packaging with
[hatchling](https://hatch.pypa.io/) and git-tag-derived versions, `uv` for
dependency locking, `ruff` + `mypy --strict` + a 100%-coverage `pytest` gate,
and a devcontainer with the same tools baked in for both humans and coding
agents. Every piece is wired up and exercised end to end - see
[`src/example_package/`](src/example_package/) and
[`tests/`](tests/) for a working (if trivial) example.

## What's included

- **Packaging**: `pyproject.toml` builds a real sdist/wheel (`uv build`) via
  hatchling; the version comes from git tags (`hatch-vcs`), not a
  hand-maintained field. `src/example_package/py.typed` ships type info
  downstream (PEP 561).
- **Dependency management**: `uv.lock` pins exact versions for both runtime
  (`[project.dependencies]`) and dev tooling (`[dependency-groups]`, PEP
  735). `package-lock.json` does the same for the npm-based formatters.
- **Quality gates**: `ruff` (lint + format), `mypy --strict`, `codespell`,
  `pytest` with a 100% coverage floor, `prettier`, and `markdownlint-cli2` -
  see `scripts/` below.
- **Security**: `pip-audit` and `npm audit` check locked dependencies
  against advisory databases; `zizmor` lints the GitHub Actions workflows.
  `.github/workflows/audit.yml` reruns them weekly; `.github/dependabot.yml`
  keeps every pin (Python, npm, the Dockerfile's base images, Actions)
  current.
- **CI**: `.github/workflows/ci.yml` runs the same gates on every push/PR,
  plus a build job that verifies the built wheel actually installs and runs.
- **Local gates**: `.githooks/pre-push` runs lint + test before every push
  (activated automatically inside the devcontainer).
- **Devcontainer**: `.devcontainer/` gives both a human's editor and coding
  agents (Claude Code, Codex) an identical, tool-complete environment.

## Quickstart

Open the repo in the devcontainer (VS Code's "Reopen in Container", or any
[Dev Containers](https://containers.dev/)-compatible tool) - everything
below is pre-installed there. Outside the devcontainer:

```sh
uv sync    # Python runtime + dev tooling, from uv.lock
npm ci     # prettier / markdownlint-cli2, from package-lock.json
```

## Everyday commands

| Command         | What it does                                              |
| --------------- | --------------------------------------------------------- |
| `scripts/lint`  | Every read-only check (ruff, mypy, codespell, ...).       |
| `scripts/fix`   | Auto-fixes the fixable subset of `scripts/lint`.          |
| `scripts/test`  | The test suite, with coverage enforced (`--offline` skips |
|                 | tests marked `online`).                                   |
| `scripts/audit` | Security audits that need network access.                 |

## Special commands

### For local simulation (manual, by-hand checks)

- `scripts/dev_local_simulation`
  - Builds the package and publishes it to the local pypiserver in `.devcontainer/docker-compose.yml`, then installs and runs that build - a manual, by-hand check.

## Using this as a template

1. Rename `src/example_package/` to your real package name and delete the
   sample code and tests inside it (`tests/test_core.py`,
   `tests/test_cli.py`) - keep `tests/test_node_version_consistency.py`.
2. Update `[project]` in `pyproject.toml`: `name`, `description`, the
   `packages` path under `[tool.hatch.build.targets.wheel]`, and
   `[project.scripts]` if you don't want a console script.
3. Add your runtime dependencies to `[project.dependencies]`.
4. Update this README.

## License

MIT - see [LICENSE](LICENSE).
