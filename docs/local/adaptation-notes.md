# Local adaptation notes

Goal:
- Use skills-mcp as the base codebase.
- Passive skills source: /Users/jurica/agent-skill-library/skills
- Qdrant: Docker Compose service
- skills-mcp: Docker Compose service where feasible
- Ollama: host-local at http://localhost:11434
- Embeddings: Ollama
- Planner: OpenRouter
- Observability: JSONL and SQLite
- MCP registry: /Users/jurica/.mcp/canonical.json
- MCP client: Antigravity and other coding agents
- Planning workflow: automatically attach relevant skills to every atomic task

Do not put the full skill library into native skills folders.

## Task 0.3 Findings
- Package manager: Python with `uv` (as evidenced by `pyproject.toml` and `uv.lock`).
- Runtime: Python
- README: `README.md`
- env examples: `.env.example`
- Docker files: `Dockerfile`, `docker-compose.yml`

## Task 0.4 Findings
- MCP server entrypoint: `skill_mcp/server.py` using FastMCP.
- Tools identified: `skills_find_relevant`, `skills_get_body`, `skills_get_reference`, `skills_get_asset`, `skills_run_script`, `skills_list_all`, `skills_get_options`. All 5 required tools are present.

## Task 0.5 Findings
- Qdrant initialization: `skill_mcp/db/qdrant_client.py` and `qdrant_manager.py`.
- Collection names: `FRONTMATTER_COLLECTION`, `BODY_COLLECTION`, `OPTIONS_COLLECTION`, `REFERENCES_COLLECTION`, `SCRIPTS_COLLECTION`, `ASSETS_COLLECTION` configured in `qdrant_manager.py`.
- Vector size: `384` hardcoded currently in `skill_mcp/db/qdrant_manager.py`.
- Payload structure: Various schemas located in `skill_mcp/models/skill.py`.
- Original embedding provider: Cloudflare Workers AI in `skill_mcp/db/embedder.py`.

## Task 0.6 Findings
- (To be updated after running `uv sync` and tests)
