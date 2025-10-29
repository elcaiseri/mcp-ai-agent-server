FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD . /app

RUN uv sync --no-cache

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "python", "-m", "src.agent"]