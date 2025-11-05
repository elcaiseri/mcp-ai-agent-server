FROM python:3.12-slim-trixie

RUN apt-get update \
    && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Confirm versions
RUN node -v && npm -v && npx -v

RUN npm install -g @modelcontextprotocol/inspector

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

VOLUME [ "/app/WORKSPACE/" ]

ADD . /app

RUN uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

# Expose port for MCP inspector
EXPOSE 3001

ENTRYPOINT ["uv", "run", "python", "-m", "src.server"]

CMD ["--sse"]