import time

from fastapi import APIRouter

from runtime import system_collector, error_tracker

router = APIRouter()


@router.get("/api/health/detailed")
async def get_detailed_health():
    system_metrics = system_collector.collect()

    health_status = "healthy"
    issues = []

    if system_metrics.get("cpu_percent", 0) > 90:
        health_status = "degraded"
        issues.append("High CPU usage")

    if system_metrics.get("memory_percent", 0) > 85:
        health_status = "degraded"
        issues.append("High memory usage")

    if system_metrics.get("disk_percent", 0) > 90:
        health_status = "degraded"
        issues.append("High disk usage")

    error_rate = error_tracker.get_error_rate(component="api_server")
    if error_rate > 10:
        health_status = "degraded"
        issues.append(f"High error rate: {error_rate:.1f}/min")

    return {
        "status": health_status,
        "issues": issues,
        "system_metrics": system_metrics,
        "error_rate_per_5min": round(error_rate, 2),
        "timestamp": time.time()
    }
