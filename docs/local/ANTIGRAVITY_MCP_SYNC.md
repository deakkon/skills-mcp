# Antigravity MCP Sync

To connect the local `skills-mcp` server to Antigravity, we must ensure it is synchronized with the canonical MCP registry.

## Automatic Sync
The canonical registry `~/.mcp/canonical.json` contains the `skills-mcp` definition.
When an Antigravity agent runs, it should dynamically discover and load this MCP server if it has a way to read `~/.mcp/canonical.json`.

Alternatively, if Antigravity has its own specific `plugins/` or `mcp/` folder (e.g. `~/.gemini/antigravity/mcp/skills-mcp/`), you should configure the tool schemas there. But since `skills-mcp` supports dynamic schema discovery via the standard MCP protocol, simply connecting Antigravity to `scripts/run-mcp-local.sh` using stdio transport is enough!

## Testing in Antigravity
If you are inside an Antigravity coding session:
1. Verify `run-mcp-local.sh` is executable.
2. The agent will have tools like `mcp_skills-mcp_skills_find_relevant`, `mcp_skills-mcp_skills_get_body`, etc.
3. If they are lazy loaded, use `call_mcp_tool` with `ServerName: skills-mcp` and `ToolName: skills_find_relevant`.
