from typing import Optional

from fastapi import APIRouter

from error_tracker import ErrorSeverity, ErrorCategory, get_error_stats
from runtime import error_tracker

router = APIRouter()


@router.get("/api/errors/recent")
async def get_recent_errors(
    limit: int = 50,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    component: Optional[str] = None
):
    severity_enum = ErrorSeverity(severity) if severity else None
    category_enum = ErrorCategory(category) if category else None

    errors = error_tracker.get_recent_errors(
        limit=limit,
        severity=severity_enum,
        category=category_enum,
        component=component
    )
    return {"errors": errors}


@router.get("/api/errors/stats")
async def get_error_stats_route():
    return get_error_stats()
