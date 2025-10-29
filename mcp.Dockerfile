FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Confirm versions
RUN node -v && npm -v && npx -v

RUN npm install -g @modelcontextprotocol/inspector

WORKDIR /app

ADD . /app

RUN uv sync --no-cache

ENV PATH="/app/.venv/bin:$PATH"

# Expose port for MCP inspector
EXPOSE 6274

CMD ["uv", "run", "python", "-m", "src.server"]