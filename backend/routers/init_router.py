"""
Initialization endpoint for bootstrapping new environments.
Creates default admin user when brighthii_staffs collection is empty.
"""

import logging
from fastapi import APIRouter, HTTPException
from reusable_components.firebase import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/init", tags=["initialization"])


@router.post("/admin")
async def initialize_first_admin():
    """
    Create the default admin user (admin@brighthii.com) when no admins exist.

    This endpoint is only available when brighthii_staffs collection is empty.
    Once at least one admin exists, this endpoint will reject requests.

    This solves the bootstrapping problem for dev/staging/prod environments.
    """
    try:
        staffs_collection = db.collection("brighthii_staffs")

        # SECURITY: Check if any staffs already exist
        existing_staffs = list(staffs_collection.limit(1).stream())

        if existing_staffs:
            logger.warning("Initialize admin rejected: staffs already exist")
            raise HTTPException(
                status_code=403,
                detail="Initialization not allowed: admin users already exist. "
                       "This endpoint only works when no admins exist yet."
            )

        # Create the default admin
        default_admin = {
            "email": "admin@brighthii.com",
            "role": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "created_via": "initialization_endpoint"
        }

        staffs_collection.document("admin@brighthii.com").set(default_admin)

        logger.info("Default admin created: admin@brighthii.com")

        return {
            "success": True,
            "message": "Default admin created successfully",
            "admin_email": "admin@brighthii.com",
            "next_step": "You can now log in via Zoho OAuth with this email"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to initialize admin")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def check_initialization_status():
    """
    Check if the system needs initialization.
    Returns whether any admin users exist.
    """
    try:
        staffs_collection = db.collection("brighthii_staffs")
        existing_staffs = list(staffs_collection.limit(1).stream())

        needs_init = len(existing_staffs) == 0

        return {
            "needs_initialization": needs_init,
            "admin_count": 0 if needs_init else "1+",
            "message": "No admins exist. Call POST /api/init/admin to create default admin."
                      if needs_init
                      else "System already initialized with admin users."
        }

    except Exception as e:
        logger.exception("Failed to check initialization status")
        raise HTTPException(status_code=500, detail=str(e))
