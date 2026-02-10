import logging
import time
import uuid

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile
from firebase_admin import firestore
from typing import Optional

from schemas.sponsor_schema import Sponsor
from reusable_components.firebase import db, get_collection_name
from reusable_components.auth import verify_jwt
from reusable_components.gcloud_storage_helper import upload_file, delete_file, generate_signed_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["sponsors"])

# ── 24-hour cache (same pattern as course_router._overrides_cache) ──

_sponsors_cache: list | None = None
_sponsors_cache_ts: float = 0
_SPONSORS_TTL = 86400  # 24 hours


def _get_sponsors_from_db() -> list[dict]:
    global _sponsors_cache, _sponsors_cache_ts
    now = time.monotonic()
    if _sponsors_cache is not None and (now - _sponsors_cache_ts) < _SPONSORS_TTL:
        return _sponsors_cache

    try:
        collection = get_collection_name("sponsors")
        docs = db.collection(collection).order_by("order").stream()
        result = []
        sponsor_ids = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            # Generate signed URL from gcs_path (public_url doesn't work on private buckets)
            gcs_path = data.get("gcs_path")
            if gcs_path:
                data["image"] = generate_signed_url(gcs_path, expiration_minutes=1500)
            result.append(data)
            sponsor_ids.append(doc.id)

        # Compute scholars_sponsored from actual enrollments
        if sponsor_ids:
            enrollment_col = get_collection_name("pending_enrollment_application")
            counts: dict[str, int] = {}
            # Query enrollments that have a sponsor_id assigned
            enrolled = db.collection(enrollment_col).where("sponsor_id", "!=", "").stream()
            for edoc in enrolled:
                sid = edoc.to_dict().get("sponsor_id", "")
                if sid:
                    counts[sid] = counts.get(sid, 0) + 1
            for sponsor in result:
                sponsor["scholars_sponsored"] = counts.get(sponsor["id"], 0)

        _sponsors_cache = result
        _sponsors_cache_ts = now
        return result
    except Exception as e:
        logger.warning("Failed to fetch sponsors: %s", e)
        return _sponsors_cache or []


def _invalidate_sponsors_cache():
    global _sponsors_cache, _sponsors_cache_ts
    _sponsors_cache = None
    _sponsors_cache_ts = 0


# ── Public endpoint ──

@router.get("/sponsors", response_model=list[Sponsor])
def get_sponsors():
    return _get_sponsors_from_db()


@router.get("/sponsors/{sponsor_id}/scholars")
def get_sponsor_scholars(
    sponsor_id: str,
    _admin: dict = Depends(verify_jwt),
):
    """Return enrollments linked to this sponsor (admin only)."""
    collection = get_collection_name("pending_enrollment_application")
    docs = db.collection(collection).where("sponsor_id", "==", sponsor_id).stream()
    scholars = []
    for doc in docs:
        data = doc.to_dict()
        scholars.append({
            "id": doc.id,
            "firstName": data.get("firstName", ""),
            "lastName": data.get("lastName", ""),
            "course": data.get("course", ""),
            "status": data.get("status", ""),
        })
    return scholars


# ── Admin CRUD ──

@router.post("/sponsors")
def create_sponsor(
    name: str = Form(...),
    title: str = Form(...),
    position: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    _admin: dict = Depends(verify_jwt),
):
    collection = get_collection_name("sponsors")

    # Determine next order value
    existing = list(
        db.collection(collection)
        .order_by("order", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    )
    next_order = (existing[0].to_dict().get("order", 0) + 1) if existing else 0

    image_url = None
    gcs_path = None
    if image and image.filename:
        file_bytes = image.file.read()
        content_type = image.content_type or "application/octet-stream"
        ext = ""
        if "." in image.filename:
            ext = "." + image.filename.rsplit(".", 1)[1].lower()
        filename = f"sponsors/{uuid.uuid4().hex}{ext}"
        image_url = upload_file(file_bytes, filename, content_type)
        gcs_path = filename

    sponsor_data = {
        "name": name,
        "title": title,
        "position": position,
        "message": message,
        "image": image_url,
        "gcs_path": gcs_path,
        "order": next_order,
        "created_at": firestore.SERVER_TIMESTAMP,
    }

    _, doc_ref = db.collection(collection).add(sponsor_data)
    _invalidate_sponsors_cache()
    return {"message": "Sponsor created", "id": doc_ref.id}


@router.put("/sponsors/{sponsor_id}")
def update_sponsor(
    sponsor_id: str,
    name: str = Form(...),
    title: str = Form(...),
    position: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    _admin: dict = Depends(verify_jwt),
):
    collection = get_collection_name("sponsors")
    doc_ref = db.collection(collection).document(sponsor_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Sponsor not found")

    current = doc.to_dict()
    updates = {
        "name": name,
        "title": title,
        "position": position,
        "message": message,
    }

    if image and image.filename:
        old_gcs_path = current.get("gcs_path")
        if old_gcs_path:
            try:
                delete_file(old_gcs_path)
            except Exception:
                logger.warning("Failed to delete old sponsor image: %s", old_gcs_path)

        file_bytes = image.file.read()
        content_type = image.content_type or "application/octet-stream"
        ext = ""
        if "." in image.filename:
            ext = "." + image.filename.rsplit(".", 1)[1].lower()
        filename = f"sponsors/{uuid.uuid4().hex}{ext}"
        updates["image"] = upload_file(file_bytes, filename, content_type)
        updates["gcs_path"] = filename

    doc_ref.update(updates)
    _invalidate_sponsors_cache()
    return {"message": "Sponsor updated"}


@router.delete("/sponsors/{sponsor_id}")
def delete_sponsor(
    sponsor_id: str,
    _admin: dict = Depends(verify_jwt),
):
    collection = get_collection_name("sponsors")
    doc_ref = db.collection(collection).document(sponsor_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Sponsor not found")

    gcs_path = doc.to_dict().get("gcs_path")
    if gcs_path:
        try:
            delete_file(gcs_path)
        except Exception:
            logger.warning("Failed to delete sponsor image: %s", gcs_path)

    doc_ref.delete()
    _invalidate_sponsors_cache()
    return {"message": "Sponsor deleted"}


@router.patch("/sponsors/reorder")
def reorder_sponsors(
    body: dict = Body(...),
    _admin: dict = Depends(verify_jwt),
):
    order_list = body.get("order", [])
    if not order_list or not isinstance(order_list, list):
        raise HTTPException(status_code=400, detail="'order' must be a non-empty list of sponsor IDs")

    collection = get_collection_name("sponsors")
    batch = db.batch()
    for idx, sponsor_id in enumerate(order_list):
        doc_ref = db.collection(collection).document(sponsor_id)
        batch.update(doc_ref, {"order": idx})
    batch.commit()

    _invalidate_sponsors_cache()
    return {"message": "Sponsors reordered"}
