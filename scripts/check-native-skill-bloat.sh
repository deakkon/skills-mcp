#!/usr/bin/env bash
set -e

# Load settings from .env if present
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

CODEX_DIR="${CODEX_NATIVE_SKILLS_DIR:-/Users/jurica/.agents/skills}"
AG_DIR="${ANTIGRAVITY_NATIVE_SKILLS_DIR:-/Users/jurica/.gemini/antigravity/skills}"
MAX_ALLOWED="${MAX_NATIVE_SKILLS_ALLOWED:-20}"

check_dir() {
    local dir=$1
    if [ -d "$dir" ]; then
        count=$(find "$dir" -maxdepth 2 -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$count" -gt "$MAX_ALLOWED" ]; then
            echo "[FAIL] Native skill directory $dir has $count skills, which exceeds the maximum allowed ($MAX_ALLOWED)."
            exit 1
        else
            echo "[OK] Native skill directory $dir has $count skills."
        fi
    else
        echo "[OK] Native skill directory $dir does not exist."
    fi
}

echo "--- Native Skill Bloat Guard ---"
check_dir "$CODEX_DIR"
check_dir "$AG_DIR"
echo "Check completed successfully."
