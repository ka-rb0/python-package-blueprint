# syntax=docker/dockerfile:1

# uv installs the locked dependencies below. A named stage rather than a
# direct COPY --from=<image>: Dependabot only bumps FROM lines.
FROM ghcr.io/astral-sh/uv:0.12.5@sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1 AS uv

# Node.js comes from the official image - digest-pinned and Dependabot-bumped
# like the other base images. The Debian release (trixie) matches the Python
# image, so the copied binary finds matching shared libraries. The major must
# match engines.node in package.json; tests/test_node_version_consistency.py
# enforces that.
FROM node:26-slim@sha256:c0753125a3789977aefe869cbebccf70e3cfd7ea84ca48547458f02e4f1d7146 AS node

# Pinned to the same Python line as requires-python in pyproject.toml;
# Dependabot bumps both tags and digests (see .github/dependabot.yml).
FROM python:3.14-slim@sha256:ce40764625a4ff50df3548277632e7f96c4e77fe75fa848aae9885476e7df5a4 AS base

COPY --from=uv /uv /uvx /usr/local/bin/

# Deliberately no `apt-get full-upgrade` here: the digest above is the single
# source of this image's package versions, so builds stay reproducible.
# Debian security patches arrive as Dependabot digest bumps (upstream rebuilds
# the Python images on base-image updates) instead of drifting in unpinned at
# build time - merge those weekly PRs promptly.

# Install the runtime Python packages ([project.dependencies], which
# --no-default-groups narrows the sync to) at the exact versions in uv.lock
# (the single source of truth) into the system interpreter - no venv
# indirection inside a container. Bind mounts (BuildKit) keep the lockfiles
# out of image layers. --inexact keeps what uv didn't install (pip). ENV,
# not ARG: child stages run uv sync against the same environment.
ENV UV_PROJECT_ENVIRONMENT=/usr/local
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-cache --inexact --no-default-groups --no-install-project

# The dev and agent stages form the desktop-development branch.
FROM base AS dev

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    nano \
    wget \
    jq \
    curl \
    fd-find \
    dos2unix \
    libatomic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js from the pinned source stage. npm/npx are standard symlinks
# into the bundled node_modules/npm and are recreated because COPY would
# dereference them.
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# npm-based lint/format tools at the exact versions in package-lock.json.
# Install to a fixed prefix rather than /workspace, which the devcontainer
# hides behind a bind mount.
COPY package.json package-lock.json /opt/npm-tools/
RUN npm ci --prefix /opt/npm-tools --no-audit --no-fund \
    && npm cache clean --force
ENV PATH="/opt/npm-tools/node_modules/.bin:${PATH}"
# Let Node-based config files resolve packages from the baked-in prefix.
ENV NODE_PATH=/opt/npm-tools/node_modules

# Install the dev Python packages (pytest, mypy, ruff, etc.) at the
# exact versions in uv.lock.
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked --no-cache --inexact --no-install-project

FROM dev AS agent

ARG DEBIAN_FRONTEND=noninteractive

# Everything in this stage floats deliberately, and it is the only stage that
# does: these tools self-update, their vendors only support the current
# release, and none of them has a lockfile Dependabot could bump. Docker caches
# RUN commands without checking whether the remote sources changed; rebuild
# with `--no-cache-filter agent` to refresh them explicitly.

# The GitHub CLI from GitHub's own apt repository rather than Debian's `gh`
# package, which the digest-pinned trixie release freezes at 2.46 (March 2024)
# while gh talks to a moving API. That breaks the dev stage's rule of tracking
# the pinned Debian release, which is why it belongs here rather than in the
# apt list above - and it keeps gh out of the distribution image, which
# branches from base.
RUN install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
       -o /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
       > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        git \
        gh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://claude.ai/install.sh | bash
RUN curl -fsSL https://chatgpt.com/codex/install.sh | sh

# Claude CLI is installed in /root/.local/bin/claude.
ENV PATH="/root/.local/bin:${PATH}"
