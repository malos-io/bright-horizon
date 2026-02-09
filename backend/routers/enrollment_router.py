import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from firebase_admin import firestore
from slowapi import Limiter
from slowapi.util import get_remote_address
from schemas.enrollment_schema import EnrollmentApplication
from reusable_components.firebase import db, get_collection_name
from reusable_components.auth import verify_jwt

limiter = Limiter(key_func=get_remote_address)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["enrollments"])

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _compute_age(data: dict) -> str:
    """Compute age from birthMonth, birthDay, birthYear fields."""
    month_str = data.get("birthMonth", "")
    day_str = data.get("birthDay", "")
    year_str = data.get("birthYear", "")
    if not month_str or not day_str or not year_str:
        return ""
    try:
        m = MONTHS.index(month_str)
        d = int(day_str)
        y = int(year_str)
    except (ValueError, IndexError):
        return ""
    today = datetime.now().date()
    age = today.year - y
    if (today.month, today.day) < (m + 1, d):
        age -= 1
    return str(age) if age >= 0 else ""


@router.get("/enrollments")
def get_enrollments(_admin: dict = Depends(verify_jwt)):
    try:
        collection = get_collection_name("pending_enrollment_application")
        docs = db.collection(collection).order_by(
            "created_at", direction=firestore.Query.DESCENDING
        ).stream()

        enrollments = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            # Convert Firestore timestamp to ISO string
            if data.get("created_at"):
                data["created_at"] = data["created_at"].isoformat()
            enrollments.append(data)

        return enrollments
    except Exception as e:
        logger.exception("Failed to fetch enrollments")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enrollments")
@limiter.limit("5/minute")
def submit_enrollment(request: Request, application: EnrollmentApplication):
    try:
        collection = get_collection_name("pending_enrollment_application")
        doc_data = application.model_dump()
        doc_data["status"] = "pending"
        doc_data["created_at"] = firestore.SERVER_TIMESTAMP

        doc_ref = db.collection(collection).add(doc_data)
        doc_id = doc_ref[1].id

        # Create student_users record with 'applicant' role
        student_collection = get_collection_name("student_users")
        student_doc = db.collection(student_collection).document(application.email).get()
        if not student_doc.exists:
            db.collection(student_collection).document(application.email).set({
                "email": application.email,
                "firstName": application.firstName,
                "lastName": application.lastName,
                "role": "applicant",
                "created_at": firestore.SERVER_TIMESTAMP,
            })

        return {"message": "Application submitted successfully", "id": doc_id}
    except Exception as e:
        logger.exception("Failed to submit enrollment")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/enrollments/{enrollment_id}")
def get_enrollment(enrollment_id: str, _admin: dict = Depends(verify_jwt)):
    try:
        collection = get_collection_name("pending_enrollment_application")
        doc = db.collection(collection).document(enrollment_id).get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        data = doc.to_dict()
        data["id"] = doc.id
        data["age"] = _compute_age(data)
        if data.get("created_at"):
            data["created_at"] = data["created_at"].isoformat()
        if data.get("updated_at"):
            data["updated_at"] = data["updated_at"].isoformat()
        # Convert changelog timestamps
        for entry in data.get("changelog", []):
            if hasattr(entry.get("updatedAt"), "isoformat"):
                entry["updatedAt"] = entry["updatedAt"].isoformat()

        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch enrollment")
        raise HTTPException(status_code=500, detail=str(e))


# Fields that should not be editable by admin
_PROTECTED_FIELDS = {"id", "created_at", "updated_at", "changelog"}


@router.patch("/enrollments/{enrollment_id}")
def update_enrollment(
    enrollment_id: str,
    fields: dict = Body(...),
    admin: dict = Depends(verify_jwt),
):
    try:
        collection = get_collection_name("pending_enrollment_application")
        doc_ref = db.collection(collection).document(enrollment_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        current = doc.to_dict()
        admin_email = admin.get("sub", "unknown")
        now = datetime.now(timezone.utc).isoformat()

        # Build changelog entries and update dict
        changelog_entries = []
        updates = {}

        for key, new_value in fields.items():
            if key in _PROTECTED_FIELDS:
                continue
            old_value = current.get(key, "")
            # Normalize for comparison
            if str(old_value) != str(new_value):
                changelog_entries.append({
                    "field": key,
                    "oldValue": old_value if old_value is not None else "",
                    "newValue": new_value if new_value is not None else "",
                    "updatedBy": admin_email,
                    "updatedAt": now,
                })
                updates[key] = new_value

        if not updates:
            return {"message": "No changes detected"}

        # Append changelog entries
        existing_changelog = current.get("changelog", [])
        updates["changelog"] = existing_changelog + changelog_entries
        updates["updated_at"] = firestore.SERVER_TIMESTAMP

        doc_ref.update(updates)

        return {"message": f"{len(changelog_entries)} field(s) updated", "changes": changelog_entries}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update enrollment")
        raise HTTPException(status_code=500, detail=str(e))
