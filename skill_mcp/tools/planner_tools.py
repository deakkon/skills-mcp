"""Planner tools for skill-mcp.

These tools allow the agent to map tasks or full implementation plans to 
specific skills, using OpenRouter for semantic routing if configured.
If OpenRouter is not configured, it falls back to basic semantic search.
"""

import json
import logging
from typing import Annotated, Any

from pydantic import Field

from skill_mcp.config import settings
from skill_mcp.db.embedder import embedder
from skill_mcp.db.qdrant_manager import qdrant_manager
from skill_mcp.telemetry import log_event

logger = logging.getLogger(__name__)

# Basic fallback logic for when OpenRouter isn't available
def _fallback_skills_for_task(task_description: str, top_k: int = 3) -> list[dict[str, Any]]:
    vector = embedder.embed(task_description)
    results = qdrant_manager.search_frontmatter(vector, top_k=top_k)
    return [
        {
            "skill_id": r.skill_id,
            "name": r.name,
            "score": getattr(r, "score", 0.0),
            "description": r.description,
        }
        for r in results if getattr(r, "score", 0.0) > 0.4
    ]

# Try to use OpenRouter if key is available
def _openrouter_skills_for_task(task_description: str) -> list[dict[str, Any]]:
    from openrouter import OpenRouter
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    
    try:
        with OpenRouter(
            api_key=settings.openrouter_api_key,
        ) as client:
            
            # --- STAGE 1: Query Expansion & Filter Extraction ---
            expansion_prompt = f"""You are a search expert. Extract semantic search queries and platform filters from the task.
Task: {task_description}

Return ONLY a raw JSON object with this exact schema (no markdown, no backticks):
{{
  "queries": ["1-3 highly targeted short phrases for semantic search"],
  "exclude_platforms": ["any platforms explicitly excluded or fundamentally incompatible, e.g., azure, aws, gcp"]
}}"""
            expansion_response = client.chat.send(
                model=settings.planner_model,
                messages=[{"role": "user", "content": expansion_prompt}],
                temperature=0.0
            )
            
            content1 = expansion_response.choices[0].message.content.strip()
            if content1.startswith("```json"):
                content1 = content1[7:-3].strip()
            
            try:
                expansion_data = json.loads(content1)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse query expansion JSON: {content1}")
                expansion_data = {"queries": [task_description[:100]], "exclude_platforms": []}
                
            queries = expansion_data.get("queries", [])
            if not queries:
                queries = [task_description[:100]]
                
            exclude_platforms = expansion_data.get("exclude_platforms", [])
            
            # Build Qdrant filter
            must_not = []
            if isinstance(exclude_platforms, list):
                for p in exclude_platforms:
                    if isinstance(p, str) and p.strip():
                        must_not.append(FieldCondition(key="platforms", match=MatchValue(value=p.strip().lower())))
            
            query_filter = Filter(must_not=must_not) if must_not else None
            
            # --- STAGE 2: Vector Search & Pooling ---
            pooled_candidates = {}
            for query in queries:
                vector = embedder.embed(query)
                # Use a larger top_k to ensure we get enough unique candidates across all queries
                hits = qdrant_manager.search_frontmatter(vector, top_k=20, query_filter=query_filter)
                for hit in hits:
                    if hit.skill_id not in pooled_candidates:
                        pooled_candidates[hit.skill_id] = hit

            candidates = list(pooled_candidates.values())
            
            # If no candidates found, return early
            if not candidates:
                return []
                
            candidate_context = "\n".join([
                f"- ID: {c.skill_id}\n  Description: {c.description}" 
                for c in candidates
            ])
            
            # --- STAGE 3: LLM Selection & Reasoning ---
            selection_prompt = f"""You are a senior coding agent architect. 
Given a task description, select the most appropriate skills from the candidate list below.
Return ONLY a JSON array of objects with 'skill_id' and a short 'reason' why it is relevant. 
Do not include markdown formatting or explanations.

Task:
{task_description}

Candidates:
{candidate_context}
"""  # nosec B608
            selection_response = client.chat.send(
                model=settings.planner_model,
                messages=[{"role": "user", "content": selection_prompt}],
                temperature=0.0
            )
            
            content2 = selection_response.choices[0].message.content.strip()
            if content2.startswith("```json"):
                content2 = content2[7:-3].strip()
                
            parsed = json.loads(content2)
            
            selected_map = {}
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and "skill_id" in item:
                        selected_map[item["skill_id"]] = item.get("reason", "Selected by planner")
                    elif isinstance(item, str):
                        selected_map[item] = "Selected by planner"
            elif isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict) and "skill_id" in item:
                                selected_map[item["skill_id"]] = item.get("reason", "Selected by planner")
                            elif isinstance(item, str):
                                selected_map[item] = "Selected by planner"
                        
            # Filter and return full info for selected IDs
            selected_skills = []
            for c in candidates:
                if c.skill_id in selected_map:
                    selected_skills.append({
                        "skill_id": c.skill_id,
                        "name": c.name,
                        "score": getattr(c, "score", 0.0),
                        "description": c.description,
                        "recommended_by_planner": True,
                        "reason": selected_map[c.skill_id]
                    })
                    
            return selected_skills
            
    except Exception as e:
        logger.warning(f"OpenRouter planner failed: {e}. Falling back to semantic search.")
        return _fallback_skills_for_task(task_description)


def skills_for_task(task_description: str) -> str:
    """Recommend skills for a single atomic task."""
    if settings.openrouter_api_key:
        skills = _openrouter_skills_for_task(task_description)
    else:
        skills = _fallback_skills_for_task(task_description)
        
    log_event("planner", {
        "type": "skills_for_task",
        "task_length": len(task_description),
        "num_recommended": len(skills),
        "used_openrouter": bool(settings.openrouter_api_key)
    })
    
    if not skills:
        return json.dumps({
            "message": "No relevant skills found for this task.",
            "skills": []
        })
        
    return json.dumps({
        "message": f"Found {len(skills)} recommended skills. Call skills_get_body(skill_id) to load them.",
        "skills": skills
    }, indent=2)

def skills_plan_with_skills(plan: str) -> str:
    """Analyze a full implementation plan and recommend a skill pack."""
    # For now, treat the whole plan as one large task description,
    # or rely on OpenRouter to parse it. 
    # Fallback uses basic search.
    if settings.openrouter_api_key:
        skills = _openrouter_skills_for_task(plan)
    else:
        skills = _fallback_skills_for_task(plan, top_k=5)
        
    log_event("planner", {
        "type": "skills_plan_with_skills",
        "plan_length": len(plan),
        "num_recommended": len(skills),
        "used_openrouter": bool(settings.openrouter_api_key)
    })
    
    if not skills:
        return json.dumps({
            "message": "No relevant skills found for this plan.",
            "skills": []
        })
        
    return json.dumps({
        "message": f"Found {len(skills)} recommended skills for your plan. Call skills_get_body(skill_id) for each.",
        "skills": skills
    }, indent=2)
