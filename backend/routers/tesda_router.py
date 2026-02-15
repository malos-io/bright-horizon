import logging
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from firebase_admin import firestore
from pydantic import BaseModel
from reusable_components.auth import verify_jwt
from reusable_components.firebase import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tesda", tags=["tesda"])

INSTRUCTORS_COLLECTION = "tesda_instructors"
TVIS_COLLECTION = "tesda_tvis"
SYNC_META_COLLECTION = "tesda_sync_metadata"


class UpdateTrackingRequest(BaseModel):
    status: str | None = None
    contacted: bool | None = None
    contacted_by: str | None = None
    notes: str | None = None


# ── GET endpoints ──


@router.get("/instructors")
def list_instructors(
    course: str = Query(None),
    active: bool = Query(None),
    contacted: bool = Query(None),
    _admin: dict = Depends(verify_jwt),
):
    """List TESDA instructors with optional filters."""
    try:
        ref = db.collection(INSTRUCTORS_COLLECTION)

        if course:
            ref = ref.where("course", "==", course)
        if active is not None:
            ref = ref.where("active", "==", active)
        if contacted is not None:
            ref = ref.where("contacted", "==", contacted)

        docs = ref.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            if data.get("last_synced"):
                data["last_synced"] = data["last_synced"].isoformat()
            if data.get("contacted_at"):
                data["contacted_at"] = data["contacted_at"].isoformat()
            results.append(data)

        return results
    except Exception as e:
        logger.exception("Failed to list TESDA instructors")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tvis")
def list_tvis(
    course: str = Query(None),
    active: bool = Query(None),
    contacted: bool = Query(None),
    _admin: dict = Depends(verify_jwt),
):
    """List TESDA TVIs with optional filters."""
    try:
        ref = db.collection(TVIS_COLLECTION)

        if course:
            ref = ref.where("course", "==", course)
        if active is not None:
            ref = ref.where("active", "==", active)
        if contacted is not None:
            ref = ref.where("contacted", "==", contacted)

        docs = ref.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            if data.get("last_synced"):
                data["last_synced"] = data["last_synced"].isoformat()
            if data.get("contacted_at"):
                data["contacted_at"] = data["contacted_at"].isoformat()
            results.append(data)

        return results
    except Exception as e:
        logger.exception("Failed to list TESDA TVIs")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync-status")
def get_sync_status(_admin: dict = Depends(verify_jwt)):
    """Get the latest sync metadata."""
    try:
        doc = db.collection(SYNC_META_COLLECTION).document("latest").get()
        if not doc.exists:
            return {"synced_at": None}
        data = doc.to_dict()
        if data.get("synced_at"):
            data["synced_at"] = data["synced_at"].isoformat()
        return data
    except Exception as e:
        logger.exception("Failed to get sync status")
        raise HTTPException(status_code=500, detail=str(e))


# ── PATCH endpoints ──


@router.patch("/instructors/{instructor_id}")
def update_instructor(
    instructor_id: str,
    request: UpdateTrackingRequest,
    admin: dict = Depends(verify_jwt),
):
    """Update tracking fields (status, contacted, notes) for an instructor."""
    try:
        doc_ref = db.collection(INSTRUCTORS_COLLECTION).document(instructor_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Instructor not found")

        update = {}
        if request.status is not None:
            update["status"] = request.status
        if request.contacted is not None:
            update["contacted"] = request.contacted
            if request.contacted:
                update["contacted_by"] = request.contacted_by or admin["sub"]
                update["contacted_at"] = firestore.SERVER_TIMESTAMP
        if request.notes is not None:
            update["notes"] = request.notes

        if update:
            doc_ref.update(update)

        return {"message": "Instructor updated", "id": instructor_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update instructor")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tvis/{tvi_id}")
def update_tvi(
    tvi_id: str,
    request: UpdateTrackingRequest,
    admin: dict = Depends(verify_jwt),
):
    """Update tracking fields (status, contacted, notes) for a TVI."""
    try:
        doc_ref = db.collection(TVIS_COLLECTION).document(tvi_id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="TVI not found")

        update = {}
        if request.status is not None:
            update["status"] = request.status
        if request.contacted is not None:
            update["contacted"] = request.contacted
            if request.contacted:
                update["contacted_by"] = request.contacted_by or admin["sub"]
                update["contacted_at"] = firestore.SERVER_TIMESTAMP
        if request.notes is not None:
            update["notes"] = request.notes

        if update:
            doc_ref.update(update)

        return {"message": "TVI updated", "id": tvi_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update TVI")
        raise HTTPException(status_code=500, detail=str(e))


# ── POST sync ──


@router.post("/sync")
def trigger_sync(admin: dict = Depends(verify_jwt)):
    """Trigger the TESDA scraper Cloud Run Job."""
    try:
        import google.auth
        import google.auth.transport.requests as google_requests

        credentials, project = google.auth.default()
        credentials.refresh(google_requests.Request())

        job_name = os.getenv("TESDA_SCRAPER_JOB", "tesda-scraper-staging")
        region = os.getenv("CLOUD_RUN_REGION", "asia-southeast1")

        url = f"https://{region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/{project}/jobs/{job_name}:run"

        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {credentials.token}"},
            timeout=30,
        )

        if response.status_code in (200, 202):
            return {
                "message": "Sync job triggered successfully",
                "triggered_by": admin["sub"],
            }
        else:
            logger.error(f"Failed to trigger sync job: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail=f"Failed to trigger sync job: {response.text}",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to trigger TESDA sync")
        raise HTTPException(status_code=500, detail=str(e))
