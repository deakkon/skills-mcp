# Canonical MCP Configuration

This project registers itself as a global MCP tool named `skills-mcp` across multiple coding agent platforms.

To ensure consistency and avoid overwriting other MCP tools, we maintain a canonical configuration file at:
`~/.mcp/canonical.json`

## Updating

Do not manually edit agent-specific config files (e.g. `claude_desktop_config.json`, `cursor_config.json`).
Instead, run:
```bash
python3 scripts/update-canonical-mcp.py
```
This script will safely inject or update the `skills-mcp` entry in `~/.mcp/canonical.json`.

## Validation

You can validate the configuration by running:
```bash
./scripts/validate-canonical-mcp-config.sh
```

## How it works

The canonical configuration points to `scripts/run-mcp-local.sh`. 
When an agent starts the MCP server:
1. It executes `run-mcp-local.sh`
2. The script runs `uv run python -m skill_mcp.server` using the local virtual environment
3. Environment variables like `ENV_FILE` are passed correctly to load `.env` runtime settings

This ensures the `skills-mcp` server runs fully locally with access to your Python dependencies and local Docker Qdrant endpoint.
