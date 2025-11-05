FROM python:3.12-slim-trixie

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ADD . /app

RUN uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "python", "-m", "src.client"]