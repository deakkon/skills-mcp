FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Security: run as non-root
RUN groupadd --gid 1001 skillmcp && \
    useradd --uid 1001 --gid skillmcp --no-create-home --shell /sbin/nologin skillmcp

WORKDIR /app
RUN chown -R skillmcp:skillmcp /app

USER skillmcp

ENV UV_CACHE_DIR=/tmp/uv-cache

# Copy dependency files first
COPY --chown=skillmcp:skillmcp pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy application source
COPY --chown=skillmcp:skillmcp skill_mcp/ ./skill_mcp/
COPY --chown=skillmcp:skillmcp scripts/ ./scripts/

# MCP server configuration via environment variables
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

EXPOSE 8000

# Default command
CMD ["uv", "run", "python", "-m", "skill_mcp.server"]
