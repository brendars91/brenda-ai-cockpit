"""
Health Check Endpoints for Gem Trinity Genesis
Provides detailed system health information for monitoring.
"""
from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime, timezone
import os
import sys
import platform
from pathlib import Path


router = APIRouter(prefix="/api/health", tags=["Health"])


def get_disk_usage() -> Dict[str, Any]:
    """Get disk usage information."""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        return {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round((used / total) * 100, 1)
        }
    except Exception:
        return {"error": "Unable to get disk usage"}


def get_memory_usage() -> Dict[str, Any]:
    """Get memory usage if psutil available."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "percent_used": mem.percent
        }
    except ImportError:
        return {"status": "psutil not installed"}


def check_dependencies() -> Dict[str, str]:
    """Check status of key dependencies."""
    deps = {}
    
    required = [
        "fastapi", "uvicorn", "pydantic", "httpx"
    ]
    
    for dep in required:
        try:
            module = __import__(dep)
            version = getattr(module, "__version__", "installed")
            deps[dep] = version
        except ImportError:
            deps[dep] = "NOT_INSTALLED"
    
    return deps


def check_services() -> Dict[str, Dict]:
    """Check status of internal services."""
    services = {}
    
    # Check artifacts directory
    artifacts = Path("artifacts")
    services["artifacts"] = {
        "status": "healthy" if artifacts.exists() else "missing",
        "path": str(artifacts.absolute())
    }
    
    # Check resources directory
    resources = Path("resources")
    services["resources"] = {
        "status": "healthy" if resources.exists() else "missing",
        "path": str(resources.absolute())
    }
    
    # Check logs directory
    logs = Path("logs")
    services["logs"] = {
        "status": "healthy" if logs.exists() else "missing",
        "path": str(logs.absolute())
    }
    
    return services


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns simple status for load balancers.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check for Kubernetes/orchestrators.
    Checks if app is ready to receive traffic.
    """
    services = check_services()
    all_healthy = all(s["status"] == "healthy" for s in services.values())
    
    return {
        "ready": all_healthy,
        "services": services,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check for Kubernetes/orchestrators.
    Checks if app is running and responding.
    """
    return {
        "alive": True,
        "pid": os.getpid(),
        "uptime_seconds": None,  # Would need startup tracking
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }


@router.get("/detailed")
async def detailed_health() -> Dict[str, Any]:
    """
    Detailed system health information.
    For monitoring dashboards and debugging.
    """
    return {
        "status": "healthy",
        "version": "2026.2.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "system": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.machine()
        },
        "resources": {
            "disk": get_disk_usage(),
            "memory": get_memory_usage()
        },
        "dependencies": check_dependencies(),
        "services": check_services(),
        "config": {
            "debug": os.environ.get("DEBUG", "false").lower() == "true",
            "log_level": os.environ.get("LOG_LEVEL", "INFO")
        }
    }
