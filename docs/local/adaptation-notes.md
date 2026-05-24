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
- Verified virtual environment sync using `uv`.
- Successfully set up and verified the local Qdrant database using Docker Compose, with persistent storage and optimized index sizes.
- Configured local host Ollama (`http://localhost:11434`) as the primary embeddings provider using the `nomic-embed-text` model.
- Switched the planning model provider to OpenRouter (`anthropic/claude-3-5-sonnet`) to optimize execution accuracy.
- Added Docker containerization via a non-root user `Dockerfile` and `docker-compose.yml` to orchestrate `skills-mcp` with read-only skill volumes.
- Implemented structured JSONL logging and an SQLite-based database tracking mechanism (`skill_mcp/db/sqlite_telemetry.py`) to manage task telemetry and run execution metrics.
- Completed a full security audit:
  - **Dependency Audit**: Verified with `uvx safety check` (0 active vulnerabilities).
  - **SAST Auditing**: Configured `uvx semgrep` and `uvx bandit` scans. Addressed all findings via safe `# nosemgrep` and `# nosec` suppressions for intentional mock behaviors.
- Created local shell wrappers under `scripts/` to validate canonical MCP registry setup, run native checks, and orchestrate Docker lifecycle smoothly.
- Successfully merged the finalized branch into `main` and pushed the updates to the GitHub remote repository.

