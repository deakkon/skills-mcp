"""Simple JSONL observability sink for skills-mcp."""

import json
import logging
import time
from pathlib import Path
from typing import Any

from skill_mcp.config import settings
from skill_mcp.db.sqlite_telemetry import log_to_sqlite

logger = logging.getLogger(__name__)

# Ensure data directory exists
_DATA_DIR = Path("data")
_DATA_DIR.mkdir(exist_ok=True)
_EVENTS_FILE = _DATA_DIR / "events.jsonl"


def log_event(event_type: str, payload: dict[str, Any]) -> None:
    """Write an event as a JSON line to the observability log."""
    event = {
        "timestamp": time.time(),
        "type": event_type,
        "payload": payload,
    }
    
    # Also log to standard logger for container logs
    # Low-cardinality logging as requested
    logger.info({"type": event_type, **payload}, f"Telemetry event: {event_type}")

    try:
        with open(_EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.error({"error": str(e)}, "Failed to write telemetry event")
        
    log_to_sqlite(event_type, payload)
