"""
Semantic Cache v2.0 - Smart LLM Response Caching
Caches LLM responses using semantic similarity to minimize API calls.
"""
import hashlib
import json
import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cached LLM response with metadata"""
    prompt_hash: str
    prompt_text: str
    response: str
    model: str
    created_at: float
    last_accessed: float
    access_count: int
    embedding: Optional[List[float]] = None  # For semantic similarity
    tokens_used: int = 0
    cost_estimate: float = 0.0

    @property
    def age_seconds(self) -> float:
        """Age of cache entry in seconds"""
        return time.time() - self.created_at

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "prompt_hash": self.prompt_hash,
            "prompt_text": self.prompt_text[:200] + "..." if len(self.prompt_text) > 200 else self.prompt_text,
            "response_length": len(self.response),
            "model": self.model,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "tokens_used": self.tokens_used,
            "cost_estimate": self.cost_estimate,
            "age_seconds": self.age_seconds
        }

class SemanticCache:
    """
    Semantic cache for LLM responses.

    Features:
    - Hash-based exact matching (fast path)
    - Semantic similarity matching (using embeddings)
    - TTL-based expiration
    - LRU eviction when full
    - Statistics tracking
    - Persistent storage
    """

    def __init__(
        self,
        max_entries: int = 1000,
        default_ttl: int = 86400,  # 24 hours
        similarity_threshold: float = 0.85,
        cache_file: Optional[Path] = None
    ):
        """
        Initialize semantic cache.

        Args:
            max_entries: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
            similarity_threshold: Threshold for semantic similarity (0-1)
            cache_file: Path to persistent cache storage
        """
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self.similarity_threshold = similarity_threshold
        self.cache_file = cache_file or Path("artifacts/semantic_cache.json")

        # Cache storage: {prompt_hash: CacheEntry}
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.Lock()

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "semantic_hits": 0,
            "evictions": 0,
            "tokens_saved": 0,
            "cost_saved": 0.0
        }

        # Load from disk
        self._load_cache()

    def _load_cache(self):
        """Load cache from disk"""
        if not self.cache_file.exists():
            return

        try:
            data = json.loads(self.cache_file.read_text(encoding="utf-8"))

            for entry_data in data.get("entries", []):
                entry = CacheEntry(
                    prompt_hash=entry_data["prompt_hash"],
                    prompt_text=entry_data["prompt_text"],
                    response=entry_data["response"],
                    model=entry_data["model"],
                    created_at=entry_data["created_at"],
                    last_accessed=entry_data["last_accessed"],
                    access_count=entry_data["access_count"],
                    embedding=entry_data.get("embedding"),
                    tokens_used=entry_data.get("tokens_used", 0),
                    cost_estimate=entry_data.get("cost_estimate", 0.0)
                )

                # Skip expired entries
                if entry.age_seconds < self.default_ttl:
                    self.cache[entry.prompt_hash] = entry

            logger.info(f"[SemanticCache] Loaded {len(self.cache)} entries from disk")

        except Exception as e:
            logger.error(f"[SemanticCache] Failed to load cache: {e}")

    def _save_cache(self):
        """Save cache to disk"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "version": "2.0",
                "saved_at": time.time(),
                "entries": [
                    {
                        "prompt_hash": entry.prompt_hash,
                        "prompt_text": entry.prompt_text,
                        "response": entry.response,
                        "model": entry.model,
                        "created_at": entry.created_at,
                        "last_accessed": entry.last_accessed,
                        "access_count": entry.access_count,
                        "embedding": entry.embedding,
                        "tokens_used": entry.tokens_used,
                        "cost_estimate": entry.cost_estimate
                    }
                    for entry in self.cache.values()
                ]
            }

            self.cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

        except Exception as e:
            logger.error(f"[SemanticCache] Failed to save cache: {e}")

    def _compute_hash(self, text: str) -> str:
        """Compute hash of text for exact matching"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _normalize_prompt(self, prompt: str) -> str:
        """Normalize prompt for better matching"""
        # Remove extra whitespace
        prompt = " ".join(prompt.split())

        # Convert to lowercase for case-insensitive matching
        # (optional - comment out if case matters)
        # prompt = prompt.lower()

        return prompt

    def get(self, prompt: str, model: str) -> Optional[str]:
        """
        Get cached response for prompt.

        Args:
            prompt: Input prompt
            model: Model name

        Returns:
            Cached response if found and valid, None otherwise
        """
        normalized = self._normalize_prompt(prompt)
        prompt_hash = self._compute_hash(f"{model}:{normalized}")

        with self.lock:
            # Exact match (fast path)
            if prompt_hash in self.cache:
                entry = self.cache[prompt_hash]

                # Check TTL
                if entry.age_seconds < self.default_ttl:
                    entry.last_accessed = time.time()
                    entry.access_count += 1
                    self.stats["hits"] += 1
                    self.stats["tokens_saved"] += entry.tokens_used
                    self.stats["cost_saved"] += entry.cost_estimate

                    logger.debug(f"[SemanticCache] HIT (exact): {entry.prompt_text[:50]}...")
                    return entry.response
                else:
                    # Expired, remove it
                    del self.cache[prompt_hash]
                    self.stats["evictions"] += 1

            # Semantic similarity match (slower path)
            # This is a simplified implementation using cosine similarity on character n-grams
            # For production, use actual embeddings from sentence-transformers or OpenAI
            most_similar = self._find_most_similar(normalized, model)

            if most_similar and most_similar[0] >= self.similarity_threshold:
                entry = most_similar[1]

                # Check TTL
                if entry.age_seconds < self.default_ttl:
                    entry.last_accessed = time.time()
                    entry.access_count += 1
                    self.stats["semantic_hits"] += 1
                    self.stats["tokens_saved"] += entry.tokens_used
                    self.stats["cost_saved"] += entry.cost_estimate

                    logger.debug(f"[SemanticCache] HIT (semantic, similarity={most_similar[0]:.2f})")
                    return entry.response

            # Cache miss
            self.stats["misses"] += 1
            return None

    def set(self, prompt: str, response: str, model: str, tokens_used: int = 0, cost: float = 0.0):
        """
        Store response in cache.

        Args:
            prompt: Input prompt
            response: LLM response
            model: Model name
            tokens_used: Number of tokens used
            cost: Estimated cost of API call
        """
        normalized = self._normalize_prompt(prompt)
        prompt_hash = self._compute_hash(f"{model}:{normalized}")

        with self.lock:
            # Check if cache is full
            if len(self.cache) >= self.max_entries:
                self._evict_lru()

            entry = CacheEntry(
                prompt_hash=prompt_hash,
                prompt_text=normalized,  # Store normalized to save space
                response=response,
                model=model,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                tokens_used=tokens_used,
                cost_estimate=cost
            )

            self.cache[prompt_hash] = entry

            # Periodically save to disk
            if len(self.cache) % 50 == 0:
                self._save_cache()

            logger.debug(f"[SemanticCache] STORED: {normalized[:50]}...")

    def _find_most_similar(self, prompt: str, model: str) -> Optional[Tuple[float, CacheEntry]]:
        """
        Find most similar cached prompt using n-gram similarity.

        This is a simplified approach. For production, use actual embeddings.

        Args:
            prompt: Input prompt
            model: Model name

        Returns:
            Tuple of (similarity_score, CacheEntry) or None
        """
        best_similarity = 0.0
        best_entry = None

        # Generate character n-grams for input
        prompt_ngrams = self._get_ngrams(prompt, n=3)

        if not prompt_ngrams:
            return None

        for entry in self.cache.values():
            if entry.model != model:
                continue

            # Check if already expired
            if entry.age_seconds >= self.default_ttl:
                continue

            # Generate n-grams for cached prompt
            cached_ngrams = self._get_ngrams(entry.prompt_text, n=3)

            if not cached_ngrams:
                continue

            # Calculate cosine similarity
            similarity = self._cosine_similarity(prompt_ngrams, cached_ngrams)

            if similarity > best_similarity:
                best_similarity = similarity
                best_entry = entry

        if best_entry:
            return (best_similarity, best_entry)
        return None

    def _get_ngrams(self, text: str, n: int = 3) -> Dict[str, int]:
        """Generate character n-grams from text"""
        ngrams = {}
        for i in range(len(text) - n + 1):
            ngram = text[i:i+n]
            ngrams[ngram] = ngrams.get(ngram, 0) + 1
        return ngrams

    def _cosine_similarity(self, vec1: Dict[str, int], vec2: Dict[str, int]) -> float:
        """Calculate cosine similarity between two n-gram vectors"""
        # Dot product
        dot = 0
        for ngram, count1 in vec1.items():
            count2 = vec2.get(ngram, 0)
            dot += count1 * count2

        # Magnitudes
        mag1 = sum(count ** 2 for count in vec1.values()) ** 0.5
        mag2 = sum(count ** 2 for count in vec2.values()) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot / (mag1 * mag2)

    def _evict_lru(self):
        """Evict least recently used entries"""
        # Sort entries by last_accessed
        entries = sorted(self.cache.items(), key=lambda x: x[1].last_accessed)

        # Remove oldest 10% of entries
        to_remove = max(1, len(entries) // 10)

        for prompt_hash, _ in entries[:to_remove]:
            del self.cache[prompt_hash]
            self.stats["evictions"] += 1

        logger.info(f"[SemanticCache] Evicted {to_remove} LRU entries")

    def invalidate(self, prompt: str, model: str):
        """Invalidate cache entry for specific prompt"""
        normalized = self._normalize_prompt(prompt)
        prompt_hash = self._compute_hash(f"{model}:{normalized}")

        with self.lock:
            if prompt_hash in self.cache:
                del self.cache[prompt_hash]
                logger.debug(f"[SemanticCache] INVALIDATED: {prompt[:50]}...")

    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.stats = {
                "hits": 0,
                "misses": 0,
                "semantic_hits": 0,
                "evictions": 0,
                "tokens_saved": 0,
                "cost_saved": 0.0
            }
            logger.info("[SemanticCache] Cache cleared")

    def cleanup_expired(self):
        """Remove expired entries from cache"""
        with self.lock:
            to_remove = [
                prompt_hash for prompt_hash, entry in self.cache.items()
                if entry.age_seconds >= self.default_ttl
            ]

            for prompt_hash in to_remove:
                del self.cache[prompt_hash]
                self.stats["evictions"] += 1

            if to_remove:
                logger.info(f"[SemanticCache] Cleaned up {len(to_remove)} expired entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0

            return {
                **self.stats,
                "total_entries": len(self.cache),
                "max_entries": self.max_entries,
                "hit_rate": round(hit_rate * 100, 1),
                "avg_entry_age": sum(e.age_seconds for e in self.cache.values()) / len(self.cache) if self.cache else 0,
                "similarity_threshold": self.similarity_threshold,
                "default_ttl_hours": self.default_ttl / 3600
            }

    def get_entries(self, limit: int = 20) -> List[Dict]:
        """Get cache entries for inspection"""
        with self.lock:
            entries = sorted(self.cache.values(), key=lambda e: e.created_at, reverse=True)
            return [entry.to_dict() for entry in entries[:limit]]

    def save_and_shutdown(self):
        """Save cache to disk before shutdown"""
        self._save_cache()
        logger.info(f"[SemanticCache] Saved {len(self.cache)} entries to disk")

# Singleton instance
_cache: Optional[SemanticCache] = None

def get_semantic_cache() -> SemanticCache:
    """Get singleton semantic cache instance"""
    global _cache
    if _cache is None:
        _cache = SemanticCache()
    return _cache
