from fastapi import APIRouter

from operation_tracker import get_metrics
from runtime import metrics_collector, system_collector

router = APIRouter()


@router.get("/api/metrics")
async def get_operation_metrics():
    metrics = get_metrics()
    return {
        "total_operations": metrics["total_operations"],
        "determinism_percentage": metrics["deterministic_pct"],
        "llm_percentage": metrics["llm_pct"],
        "breakdown": metrics["by_category"],
        "philosophy": {
            "target_determinism": 75,
            "target_llm": 25,
            "status": "healthy" if metrics["deterministic_pct"] >= 70 else "needs_optimization"
        }
    }


@router.get("/api/metrics/dashboard")
async def get_metrics_dashboard():
    metrics = get_metrics()
    det_pct = metrics["deterministic_pct"]
    llm_pct = metrics["llm_pct"]

    bar_det = "#" * int(det_pct / 5)
    bar_det = bar_det.ljust(20, ".")
    bar_llm = "#" * int(llm_pct / 5)
    bar_llm = bar_llm.ljust(20, ".")

    return {
        "ascii_dashboard": f"""
+-------------------------------+
| Metrics Dashboard             |
+-------------------------------+
| Determinism: {bar_det} {det_pct}%
| LLM:         {bar_llm} {llm_pct}%
+-------------------------------+
""",
        "metrics": metrics
    }


@router.get("/api/metrics/prometheus")
async def get_prometheus_metrics():
    return {
        "content": metrics_collector.get_prometheus_export(),
        "content_type": "text/plain"
    }


@router.get("/api/metrics/stats")
async def get_metrics_stats():
    return {
        "collector": metrics_collector.get_stats_summary(),
        "system": system_collector.collect()
    }


@router.get("/api/metrics/system")
async def get_system_metrics():
    return system_collector.collect()
