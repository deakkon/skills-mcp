#!/bin/bash
set -e

# Run the local skills-mcp server using uv
# This script is meant to be called by MCP clients (like Claude Code or Cursor)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR/.."

# Activate uv venv if it exists, otherwise just use uv run
export MCP_TRANSPORT="stdio"
export PYTHONPATH="$PWD"

# Pipe stderr to a log file so we can debug MCP client crashes
exec uv run python -m skill_mcp.server 2>> /tmp/mcp_debug.log
