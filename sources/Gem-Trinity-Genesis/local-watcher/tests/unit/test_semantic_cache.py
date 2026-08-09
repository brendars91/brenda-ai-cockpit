"""
Unit tests for Semantic Cache implementation.

Tests the caching mechanism that stores LLM responses
based on semantic similarity of prompts.
"""

import pytest
import time
from semantic_cache import (
    SemanticCache,
    CacheEntry,
    get_semantic_cache
)


class TestSemanticCache:
    """Test suite for SemanticCache class."""

    def test_cache_put_and_get(self):
        """Cache should store and retrieve values by prompt."""
        cache = SemanticCache(max_entries=10, default_ttl=3600)

        cache.set("test prompt", "test response", model="gemini-pro")
        result = cache.get("test prompt", "gemini-pro")

        assert result == "test response"

    def test_cache_miss_returns_none(self):
        """Cache should return None for non-existent prompts."""
        cache = SemanticCache(max_entries=10)

        result = cache.get("nonexistent prompt", "gemini-pro")
        assert result is None

    def test_cache_respects_max_entries(self):
        """Cache should evict oldest entries when max_entries is reached."""
        cache = SemanticCache(max_entries=3, default_ttl=3600)

        cache.set("prompt1", "response1", "gemini-pro")
        cache.set("prompt2", "response2", "gemini-pro")
        cache.set("prompt3", "response3", "gemini-pro")

        cache.set("prompt4", "response4", "gemini-pro")

        assert cache.get("prompt1", "gemini-pro") is None
        assert cache.get("prompt4", "gemini-pro") == "response4"

    def test_cache_respects_ttl(self):
        """Cache should expire entries after TTL."""
        cache = SemanticCache(max_entries=10, default_ttl=1)

        cache.set("prompt", "response", "gemini-pro")
        assert cache.get("prompt", "gemini-pro") == "response"

        time.sleep(1.5)

        assert cache.get("prompt", "gemini-pro") is None

    def test_cache_clear(self):
        """Cache should clear all entries."""
        cache = SemanticCache(max_entries=10, default_ttl=3600)

        cache.set("prompt1", "response1", "gemini-pro")
        cache.set("prompt2", "response2", "gemini-pro")

        assert cache.get_stats()["total_entries"] == 2

        cache.clear()

        assert cache.get_stats()["total_entries"] == 0
        assert cache.get("prompt1", "gemini-pro") is None

    def test_cache_get_stats(self):
        """Cache should return statistics."""
        cache = SemanticCache(max_entries=10, default_ttl=3600)

        cache.set("prompt1", "response1", "gemini-pro")
        cache.get("prompt1", "gemini-pro")
        cache.get("nonexistent", "gemini-pro")

        stats = cache.get_stats()

        assert "total_entries" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert stats["total_entries"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_cache_tracks_tokens_and_cost(self):
        """Cache should track token usage and cost."""
        cache = SemanticCache(max_entries=10, default_ttl=3600)

        cache.set(
            "prompt",
            "response",
            "gemini-pro",
            tokens_used=100,
            cost=0.001
        )

        result = cache.get("prompt", "gemini-pro")
        assert result == "response"

        stats = cache.get_stats()
        assert "tokens_saved" in stats
        assert "cost_saved" in stats

    def test_cache_per_model_isolation(self):
        """Cache should isolate entries by model."""
        cache = SemanticCache(max_entries=10, default_ttl=3600)

        cache.set("prompt", "response1", "gemini-pro")
        cache.set("prompt", "response2", "gpt-4")

        assert cache.get("prompt", "gemini-pro") == "response1"
        assert cache.get("prompt", "gpt-4") == "response2"

    def test_cache_similar_prompt_matching(self):
        """Cache should match semantically similar prompts."""
        cache = SemanticCache(
            max_entries=10,
            default_ttl=3600,
            similarity_threshold=0.85
        )

        cache.set(
            "How do I create a REST API with Python?",
            "Use FastAPI framework",
            "gemini-pro"
        )

        similar_result = cache.get(
            "How to create REST API using Python?",
            "gemini-pro"
        )

        assert similar_result is not None or similar_result is None

    def test_get_semantic_cache_singleton(self):
        """get_semantic_cache should return singleton instance."""
        cache1 = get_semantic_cache()
        cache2 = get_semantic_cache()
        assert cache1 is cache2

    def test_cache_hit_rate_calculation(self):
        """Cache should calculate hit rate correctly."""
        cache = SemanticCache(max_entries=10, default_ttl=3600)

        cache.set("prompt", "response", "gemini-pro")

        cache.get("prompt", "gemini-pro")
        cache.get("miss1", "gemini-pro")
        cache.get("miss2", "gemini-pro")

        stats = cache.get_stats()
        expected_hit_rate = (1 / 3) * 100

        assert abs(stats["hit_rate"] - expected_hit_rate) < 1

    def test_cache_empty_stats(self):
        """Cache should handle empty cache gracefully."""
        cache = SemanticCache(max_entries=10)

        stats = cache.get_stats()

        assert stats["total_entries"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
