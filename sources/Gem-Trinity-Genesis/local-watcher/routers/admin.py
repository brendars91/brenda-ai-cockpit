import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Depends

from operation_tracker import LOG_PATH
from structured_logger import get_logger

router = APIRouter()
logger = get_logger("admin")

# Simple admin secret for personal use
# Set ADMIN_SECRET in .env file to protect admin endpoints
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "change-me-in-production")


async def verify_admin(x_admin_secret: Optional[str] = Header(None)) -> None:
    """
    Verify admin secret for sensitive endpoints.

    For personal use, this provides basic protection against accidental triggers.
    Set ADMIN_SECRET environment variable to your preferred secret.

    Example with curl:
    curl -X DELETE http://localhost:8000/api/admin/wipe -H "X-Admin-Secret: your-secret-here"
    """
    if not ADMIN_SECRET or ADMIN_SECRET == "change-me-in-production":
        logger.warning("ADMIN: Admin endpoint called but ADMIN_SECRET not configured!")
        raise HTTPException(
            status_code=503,
            detail="Admin secret not configured. Set ADMIN_SECRET in .env file."
        )

    if x_admin_secret != ADMIN_SECRET:
        logger.warning(f"ADMIN: Failed auth attempt with secret: {x_admin_secret}")
        raise HTTPException(
            status_code=401,
            detail="Unauthorized. Invalid admin secret."
        )


@router.delete("/api/admin/wipe", dependencies=[Depends(verify_admin)])
async def wipe_all_data():
    try:
        projects_dir = Path("../projects")
        if projects_dir.exists():
            for item in projects_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

        if LOG_PATH.exists():
            LOG_PATH.unlink()

        logger.warning("ADMIN: System WIPE executed. All projects deleted.")

        return {
            "status": "success",
            "message": "System wiped successfully. All projects deleted and metrics reset.",
            "projects_deleted": True,
            "metrics_reset": True
        }
    except Exception as e:
        logger.error(f"Wipe failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
