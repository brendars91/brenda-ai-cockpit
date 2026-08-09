import pytest
import asyncio
import httpx
import time
import os
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_load_rate_limiter():
    """
    Simulate high load to trigger rate limiter.
    Goal: Send 70 requests in < 1 minute (Limit is 60).
    """
    if os.getenv("RUN_LOAD_TESTS") != "1":
        pytest.skip("Load tests require RUN_LOAD_TESTS=1 and a running server")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Warmup
        resp = await client.get("/api/health/")
        assert resp.status_code == 200
        
        print("\n--- Starting Load Test (70 reqs) ---")
        start_time = time.time()
        
        tasks = []
        for i in range(70):
            tasks.append(client.get("/api/metrics"))
            
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        status_codes = [r.status_code for r in responses if isinstance(r, httpx.Response)]
        success = status_codes.count(200)
        rate_limited = status_codes.count(429)
        
        print(f"Time: {duration:.2f}s | Success: {success} | Rate Limited: {rate_limited}")
        
        # Verify functionality
        assert success > 0, "Should have some successful requests"
        assert rate_limited > 0, "Should trigger rate limiter (>60 requests)"
        assert success + rate_limited == 70

@pytest.mark.asyncio
async def test_concurrent_health_checks():
    """Test concurrent health checks don't crash server."""
    if os.getenv("RUN_LOAD_TESTS") != "1":
        pytest.skip("Load tests require RUN_LOAD_TESTS=1 and a running server")
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        tasks = [client.get("/api/health/detailed") for _ in range(20)]
        responses = await asyncio.gather(*tasks)
        
        for r in responses:
            assert r.status_code in [200, 429], f"Unexpected status {r.status_code}"
            if r.status_code == 200:
                assert r.json()["status"] == "healthy"
