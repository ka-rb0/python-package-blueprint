# syntax=docker/dockerfile:1

FROM python:slim AS dev

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    nano \
    wget \
    jq \
    curl \
    fd-find \
    dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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
