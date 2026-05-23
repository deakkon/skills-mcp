import asyncio
import os
import sys
import json
import yaml
from pathlib import Path
import httpx
from dotenv import load_dotenv

# Load env
load_dotenv("/Users/jurica/Code/skills-mcp/.env")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PLANNER_MODEL = os.getenv("PLANNER_MODEL", "deepseek/deepseek-v4-flash")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

async def process_skill(path: Path, client: httpx.AsyncClient, sem: asyncio.Semaphore):
    async with sem:
        text = path.read_text(encoding='utf-8')
        parts = text.split('---', 2)
        if len(parts) < 3:
            return False
            
        try:
            fm = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            return False
            
        # Skip if already enriched
        metadata = fm.get("metadata") or {}
        if metadata.get("tags") and metadata.get("platforms"):
            return True
            
        body = parts[2].strip()
        
        # Prompt LLM
        prompt = f"""You are a technical cataloging expert. Read the skill instructions and extract appropriate metadata.
Return ONLY a raw JSON object (no markdown formatting, no backticks).
Schema:
{{
  "tags": ["list of 2-5 technical tags, e.g. python, frontend, react, database"],
  "platforms": ["list of platforms required, e.g. aws, docker, kubernetes, macos, gcp, azure, github. Leave empty if general"],
  "use_cases": ["list of 1-3 primary use cases, e.g. deploying web apps, debugging css"]
}}

Instructions:
{body[:2000]} # truncate to avoid context limit if massive
"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    f"{BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                    json={
                        "model": PLANNER_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.0
                    },
                    timeout=20.0
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"].strip()
                
                if content.startswith("```json"):
                    content = content[7:-3].strip()
                    
                data = json.loads(content)
                
                # Update frontmatter
                if "metadata" not in fm:
                    fm["metadata"] = {}
                    
                fm["metadata"]["tags"] = data.get("tags", [])
                fm["metadata"]["platforms"] = data.get("platforms", [])
                fm["metadata"]["use_cases"] = data.get("use_cases", [])
                
                # Write back
                new_fm_str = yaml.safe_dump(fm, default_flow_style=False, sort_keys=False)
                new_content = f"---\n{new_fm_str}---\n{parts[2]}"
                path.write_text(new_content, encoding="utf-8")
                
                print(f"Enriched: {path.parent.name}")
                return True
                
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed {path.parent.name}: {str(e)[:100]}")
                    return False
                await asyncio.sleep(2 * (attempt + 1))

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        limit = 5
    else:
        limit = None
        
    skills_dir = Path('/Users/jurica/agent-skill-library/skills')
    skill_files = list(skills_dir.glob('*/SKILL.md'))
    
    if limit:
        skill_files = skill_files[:limit]
        
    print(f"Processing {len(skill_files)} files...")
    
    sem = asyncio.Semaphore(15) # rate limit protection
    limits = httpx.Limits(max_connections=50, max_keepalive_connections=20)
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [process_skill(path, client, sem) for path in skill_files]
        await asyncio.gather(*tasks)
        
if __name__ == "__main__":
    asyncio.run(main())
