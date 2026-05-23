"""SQLite telemetry sink for skills-mcp observability."""

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DATA_DIR = Path("data")
_DATA_DIR.mkdir(exist_ok=True)
_SQLITE_FILE = _DATA_DIR / "telemetry.db"


def _init_db() -> None:
    try:
        with sqlite3.connect(_SQLITE_FILE) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    type TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    query TEXT NOT NULL,
                    top_k INTEGER,
                    num_results INTEGER,
                    top_score REAL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS loads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    skill_id TEXT NOT NULL,
                    version TEXT,
                    has_tier3 INTEGER
                )
            ''')
            conn.commit()
    except Exception as e:
        logger.error({"error": str(e)}, "Failed to initialize telemetry database")


# Initialize on import
_init_db()


def log_to_sqlite(event_type: str, payload: dict[str, Any]) -> None:
    """Write an event to the SQLite database."""
    ts = time.time()
    try:
        with sqlite3.connect(_SQLITE_FILE) as conn:
            # Always log to events table
            conn.execute(
                "INSERT INTO events (timestamp, type, payload) VALUES (?, ?, ?)",
                (ts, event_type, json.dumps(payload))
            )
            
            # Type-specific tables
            if event_type == "query":
                conn.execute(
                    "INSERT INTO queries (timestamp, query, top_k, num_results, top_score) VALUES (?, ?, ?, ?, ?)",
                    (ts, payload.get("query", ""), payload.get("top_k", 5), payload.get("num_results", 0), payload.get("top_score", 0.0))
                )
            elif event_type == "load":
                conn.execute(
                    "INSERT INTO loads (timestamp, skill_id, version, has_tier3) VALUES (?, ?, ?, ?)",
                    (ts, payload.get("skill_id", ""), payload.get("version", ""), 1 if payload.get("has_tier3") else 0)
                )
                
            conn.commit()
    except Exception as e:
        logger.error({"error": str(e)}, "Failed to write SQLite telemetry")
