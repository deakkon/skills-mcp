#!/usr/bin/env bash
set -e

echo "--- Docker Doctor ---"

if ! command -v docker &> /dev/null; then
    echo "[FAIL] Docker is not installed or not in PATH."
    exit 1
else
    echo "[OK] Docker is available."
fi

if ! docker compose version &> /dev/null; then
    echo "[FAIL] docker compose is not available."
    exit 1
else
    echo "[OK] docker compose is available."
fi

echo "Starting qdrant (if not running)..."
docker compose up -d qdrant

# Wait for qdrant
sleep 3

if curl -s http://localhost:6335/collections > /dev/null; then
    echo "[OK] Qdrant responds at http://localhost:6335/collections on host."
else
    echo "[FAIL] Qdrant does NOT respond at http://localhost:6335/collections on host."
fi

# Test from within container
echo "Testing from within skills-mcp container..."
if docker compose run --rm skills-mcp python -c "import urllib.request; urllib.request.urlopen('http://qdrant:6333/collections')" 2>/dev/null; then
    echo "[OK] Qdrant responds at http://qdrant:6333/collections inside container."
else
    echo "[FAIL] Qdrant does NOT respond at http://qdrant:6333/collections inside container."
fi

if docker compose run --rm skills-mcp python -c "import urllib.request; urllib.request.urlopen('http://host.docker.internal:11434/api/tags')" 2>/dev/null; then
    echo "[OK] Ollama responds at http://host.docker.internal:11434/api/tags inside container."
else
    echo "[FAIL] Ollama does NOT respond at http://host.docker.internal:11434/api/tags inside container."
fi

echo "Checking skills directory inside container..."
SKILL_COUNT=$(docker compose run --rm skills-mcp sh -c 'ls -1 /skills/*/SKILL.md 2>/dev/null | wc -l')
if [ -z "$SKILL_COUNT" ]; then
    SKILL_COUNT=0
fi

if [ "$SKILL_COUNT" -gt 0 ]; then
    echo "[OK] /skills exists and contains $SKILL_COUNT skills."
else
    echo "[FAIL] /skills is empty or not mounted correctly (found 0 skills)."
fi

echo "Doctor finished."
