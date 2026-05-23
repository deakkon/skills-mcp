import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Load .env file explicitly if ENV_FILE is set, otherwise default to .env in project root
project_root = os.path.dirname(os.path.dirname(__file__))
env_file = os.getenv("ENV_FILE", os.path.join(project_root, ".env"))
load_dotenv(dotenv_path=env_file)

class Settings(BaseSettings):
    # App
    app_env: str = "local"
    log_level: str = "INFO"
    
    # Skills source
    skills_root: str = "/skills"
    host_skills_root: str = "/Users/jurica/agent-skill-library/skills"
    
    # Native folders
    codex_native_skills_dir: str = "/Users/jurica/.agents/skills"
    antigravity_native_skills_dir: str = "/Users/jurica/.gemini/antigravity/skills"
    max_native_skills_allowed: int = 20
    
    # Qdrant
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_skills: str = "skills_mcp_skills_v1"
    qdrant_recreate_collection: bool = False
    qdrant_host_url: str = "http://localhost:6335"
    
    # Embeddings
    embeddings_provider: str = "ollama"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_host_url: str = "http://localhost:11434"
    embeddings_model: str = "nomic-embed-text"
    embeddings_dimensions: int = 768
    embeddings_keep_alive: str = "10m"
    embeddings_batch_size: int = 32
    
    # Planner
    planner_provider: str = "openrouter"
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    planner_model: str = "deepseek/deepseek-v4-flash"
    planner_fallback_model: str = "openai/gpt-4o-mini"
    planner_temperature: float = 0.0
    planner_max_lanes: int = 6
    planner_max_total_skills: int = 12
    
    # Skill-aware planning
    skill_planning_enabled: bool = True
    skill_planning_max_tasks: int = 20
    skill_planning_max_skills_per_task: int = 5
    skill_planning_load_policy: str = "defer_bodies"
    
    # Observability
    observability_enabled: bool = True
    observability_jsonl_path: str = "/app/data/events.jsonl"
    observability_sqlite_path: str = "/app/data/skills_mcp.sqlite"
    observability_capture_candidates: bool = True
    observability_redact_secrets: bool = True
    
    # Docker
    compose_project_name: str = "skills-mcp"
    docker_qdrant_volume: str = "skills_mcp_qdrant_storage"
    
    # MCP runtime metadata
    mcp_transport: str = "stdio"
    mcp_server_name: str = "skills-mcp"
    mcp_canonical_config: str = "/Users/jurica/.mcp/canonical.json"
    mcp_run_script: str = "/Users/jurica/Code/skills-mcp/scripts/run-mcp-local.sh"

    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
