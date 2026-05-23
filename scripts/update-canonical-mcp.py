#!/usr/bin/env python3
"""Programmatically update ~/.mcp/canonical.json with skills-mcp."""

import json
import os
import sys
from pathlib import Path


def update_canonical_mcp() -> None:
    canonical_path = Path(os.path.expanduser("~/.mcp/canonical.json"))
    
    # Ensure directory exists
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create empty
    if canonical_path.exists():
        try:
            with open(canonical_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {canonical_path} contains invalid JSON. Aborting.", file=sys.stderr)
            sys.exit(1)
    else:
        data = {}
        
    if "mcpServers" not in data:
        data["mcpServers"] = {}
        
    # Set the path to the runner script
    project_root = Path(__file__).resolve().parent.parent
    runner_script = project_root / "scripts" / "run-mcp-local.sh"
    
    data["mcpServers"]["skills-mcp"] = {
        "command": str(runner_script),
        "env": {
            "ENV_FILE": str(project_root / ".env")
        }
    }
    
    # Write back
    with open(canonical_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully registered skills-mcp in {canonical_path}")


if __name__ == "__main__":
    update_canonical_mcp()
