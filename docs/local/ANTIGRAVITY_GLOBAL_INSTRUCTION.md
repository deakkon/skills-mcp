# Antigravity Global Instruction

To ensure Antigravity uses the `skills-mcp` effectively, ensure your global agent instructions (e.g. `user_global` rule) contain the following directive:

## Skill-Aware Planning Policy

```markdown
## Skill Activation
For every task, scan available skills via the `skills-mcp` MCP server and automatically activate any skill whose description matches the current task. If no specific skill matches but the task involves coding, default to core engineering capabilities.

When asked to plan, design, refactor, implement, debug, review, or create atomic tasks, use the skills MCP workflow automatically:
1. Call `skills_plan_with_skills` to analyze the full plan.
2. For specific tasks, call `skills_for_task` or `skills_find_relevant`.
3. Load the full skill body via `skills_get_body` for any skill with a relevance score > 0.6.
4. If a skill's body instructs you to fetch a reference file or script, use `skills_get_reference` or `skills_run_script` respectively.
```

By appending this to your prompt, Antigravity will naturally route skill resolution to the local Qdrant + Ollama setup hosted by `skills-mcp`.
