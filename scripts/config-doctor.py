#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from skill_mcp.config import settings

def main():
    errors = 0
    warnings = 0

    print("--- Config Doctor ---")

    # Check env loaded
    print(f"APP_ENV: {settings.app_env}")
    
    # Check paths
    host_skills_root = Path(settings.host_skills_root)
    if not host_skills_root.exists():
        print(f"[FAIL] HOST_SKILLS_ROOT '{host_skills_root}' does not exist on host.")
        errors += 1
    else:
        print(f"[OK] HOST_SKILLS_ROOT '{host_skills_root}' exists.")

    skills_root = Path(settings.skills_root)
    if not skills_root.exists():
        print(f"[WARN] SKILLS_ROOT '{skills_root}' does not exist (expected if running on host instead of Docker).")
        warnings += 1
    else:
        print(f"[OK] SKILLS_ROOT '{skills_root}' exists.")
        
    native_codex = Path(settings.codex_native_skills_dir)
    if native_codex.exists():
        count = len(list(native_codex.glob("**/SKILL.md")))
        if count > settings.max_native_skills_allowed:
            print(f"[FAIL] Codex native skills directory '{native_codex}' exceeds max allowed ({count} > {settings.max_native_skills_allowed}).")
            errors += 1
        else:
            print(f"[OK] Codex native skills directory '{native_codex}' is within limits ({count} skills).")
            
    native_ag = Path(settings.antigravity_native_skills_dir)
    if native_ag.exists():
        count = len(list(native_ag.glob("**/SKILL.md")))
        if count > settings.max_native_skills_allowed:
            print(f"[FAIL] Antigravity native skills directory '{native_ag}' exceeds max allowed ({count} > {settings.max_native_skills_allowed}).")
            errors += 1
        else:
            print(f"[OK] Antigravity native skills directory '{native_ag}' is within limits ({count} skills).")

    print(f"QDRANT_URL: {settings.qdrant_url}")
    print(f"OLLAMA_BASE_URL: {settings.ollama_base_url}")
    print(f"EMBEDDINGS_MODEL: {settings.embeddings_model}")
    print(f"MCP_CANONICAL_CONFIG: {settings.mcp_canonical_config}")

    if errors > 0:
        print(f"\\nDoctor completed with {errors} errors and {warnings} warnings.")
        sys.exit(1)
    else:
        print(f"\\nDoctor completed successfully with {warnings} warnings.")

if __name__ == '__main__':
    main()
