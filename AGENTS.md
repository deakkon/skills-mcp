# AGENTS.md

## Purpose

This repo provides a local MCP skill registry for coding agents.

The full skill library lives outside this repo at the host path configured by `HOST_SKILLS_ROOT` in `.env`.

Inside Docker, the same skill library is mounted read-only at `SKILLS_ROOT`, usually `/skills`.

Do not put the full skill library into native global skill folders.

## Central settings

Runtime settings come from `.env`.

Use `.env.example` as the versioned template.

Important settings:
- `HOST_SKILLS_ROOT` points to the passive skill library on the host.
- `SKILLS_ROOT` points to the passive skill library inside Docker.
- `QDRANT_URL` points to Qdrant inside Docker.
- `QDRANT_HOST_URL` points to Qdrant from the host.
- `OLLAMA_BASE_URL` points from Docker to local host Ollama.
- `OLLAMA_HOST_URL` points to Ollama from the host.
- `EMBEDDINGS_MODEL` configures embeddings.
- `OPENROUTER_API_KEY` and `PLANNER_MODEL` configure optional planning.
- `OBSERVABILITY_*` configures traces and logs.
- `MCP_CANONICAL_CONFIG` points to the canonical MCP registry.

Do not hard-code these values in source code.

## Docker policy

Use Docker Compose for Qdrant and skills-mcp runtime helpers.

Ollama runs locally on the host and should not be containerized here.

The skill library must be mounted into the skills-mcp container read-only.

Qdrant data must persist in a Docker volume.

## MCP configuration policy

The canonical MCP server registry is:

/Users/jurica/.mcp/canonical.json

When adding, updating, or validating the skills-mcp server registration, update that file.

Do not treat Antigravity-specific MCP config as the source of truth.

Runtime settings for the skills-mcp server come from:

/Users/jurica/Code/skills-mcp/.env

Do not hard-code runtime settings in MCP config. The MCP config should launch the wrapper script and pass ENV_FILE only.

Required canonical MCP server name:

skills-mcp

## Native skill folder guardrail

These folders must stay empty or tiny:
- `/Users/jurica/.agents/skills`
- `/Users/jurica/.gemini/antigravity/skills`

Never symlink `/Users/jurica/agent-skill-library/skills` into either folder.

## Skill-aware planning policy

When asked to plan, design, refactor, implement, debug, review, or create atomic tasks, use the skills MCP workflow automatically.

Planning rules:
1. If available, call `skills_plan_with_skills`.
2. If unavailable, create atomic tasks, then call `skills_for_tasks`.
3. If unavailable, call `skills_find_relevant` once per atomic task.
4. Every atomic task must include relevant skill IDs, reasons, and load timing.
5. During planning, do not bulk-load full `SKILL.md` bodies.
6. During execution, load only the skills attached to the current task.
7. Load references, assets, or scripts only when needed.
8. Never scan `SKILLS_ROOT` directly from an agent.

Relevant skills format:
- `<skill_id>`, load: `before_execution | before_tests | before_review | if_needed`
  Reason: one sentence.

## Development workflow

- Inspect existing code before changing it.
- Make small atomic changes.
- Add smoke tests for provider changes.
- Update `docs/local/adaptation-notes.md` after each milestone.
- Do not copy code from unrelated local projects.
- Do not delete user data.
- Do not index all real skills until the one-skill smoke test works.
