"""Ollama embedding client with TTL cache.

Uses the local Ollama instance specified in config.py
"""

from __future__ import annotations

import os
import requests

from .cache import TTLCache
from skill_mcp.config import settings

_CACHE_TTL = float(os.getenv("CACHE_TTL_SECONDS", "300"))
_CACHE_MAX = int(os.getenv("CACHE_MAX_SIZE", "1000"))

DIMENSION = settings.embeddings_dimensions


class Embedder:
    """Ollama embedding client with TTL cache."""

    DIMENSION: int = DIMENSION

    def __init__(self) -> None:
        self._cache: TTLCache = TTLCache(ttl=_CACHE_TTL, max_size=_CACHE_MAX)

    # ── Public API ─────────────────────────────────────────────────────────────

    def load(self) -> None:
        """No-op - Ollama loads models on demand."""

    @property
    def is_loaded(self) -> bool:
        """Always True for the purpose of the API. Ollama handles actual loading."""
        return True

    def embed(self, text: str) -> list[float]:
        """Embed a single text string, with TTL cache."""
        cached = self._cache.get(text)
        if cached is not None:
            return cached
        vec = self._call_api_batch([text])[0]
        self._cache.set(text, vec)
        return vec

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in a single Ollama API call (cache-aware)."""
        if not texts:
            return []

        results: list[list[float] | None] = [None] * len(texts)
        uncached_indices: list[int] = []
        uncached_texts: list[str] = []

        for i, text in enumerate(texts):
            cached = self._cache.get(text)
            if cached is not None:
                results[i] = cached
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        if uncached_texts:
            # Batch size limits could be implemented here if needed.
            # Ollama handles reasonable batch sizes natively.
            batch_size = settings.embeddings_batch_size
            for i in range(0, len(uncached_texts), batch_size):
                batch_texts = uncached_texts[i:i + batch_size]
                batch_indices = uncached_indices[i:i + batch_size]
                
                vectors = self._call_api_batch(batch_texts)
                for idx, vec in zip(batch_indices, vectors):
                    self._cache.set(texts[idx], vec)
                    results[idx] = vec

        return results  # type: ignore[return-value]  # all slots filled above

    # ── Internal ───────────────────────────────────────────────────────────────

    def _call_api_batch(self, texts: list[str]) -> list[list[float]]:
        """Send texts to Ollama in one HTTP round-trip, return all vectors."""
        base_url = settings.ollama_base_url
        model = settings.embeddings_model
        
        # fallback to host URL if running outside docker but configured for docker
        if base_url == "http://host.docker.internal:11434" and not os.path.exists("/.dockerenv"):
            base_url = settings.ollama_host_url

        url = f"{base_url.rstrip('/')}/api/embed"
        resp = requests.post(
            url,
            json={"model": model, "input": texts, "keep_alive": settings.embeddings_keep_alive},
            timeout=120,
        )
        
        if resp.status_code != 200:
            raise RuntimeError(f"Ollama embedding failed: {resp.text}")
            
        result = resp.json()
        vectors: list[list[float]] = result.get("embeddings", [])
        
        if len(vectors) != len(texts):
            raise RuntimeError(
                f"Ollama returned {len(vectors)} vectors for {len(texts)} texts"
            )
        return vectors


# Module-level singleton used by find_skills.py and the local server
embedder = Embedder()
