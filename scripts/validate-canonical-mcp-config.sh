#!/bin/bash
set -e

CANONICAL_FILE="$HOME/.mcp/canonical.json"

echo "Validating $CANONICAL_FILE..."

if [ ! -f "$CANONICAL_FILE" ]; then
    echo "ERROR: File not found: $CANONICAL_FILE"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "WARNING: jq is not installed. Skipping JSON structure validation."
else
    if ! jq empty "$CANONICAL_FILE" 2>/dev/null; then
        echo "ERROR: Invalid JSON in $CANONICAL_FILE"
        exit 1
    fi
    
    HAS_SKILLS=$(jq -r '.mcpServers | has("skills-mcp")' "$CANONICAL_FILE")
    if [ "$HAS_SKILLS" != "true" ]; then
        echo "ERROR: skills-mcp is not registered in $CANONICAL_FILE"
        exit 1
    fi
    
    COMMAND=$(jq -r '.mcpServers["skills-mcp"].command' "$CANONICAL_FILE")
    if [ ! -x "$COMMAND" ]; then
        echo "ERROR: Command '$COMMAND' is not executable or does not exist."
        exit 1
    fi
fi

echo "SUCCESS: Canonical MCP configuration is valid."
exit 0
