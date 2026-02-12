import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from firebase_admin import firestore
from reusable_components.firebase import db
from reusable_components.auth import verify_jwt
from reusable_components.gcloud_storage_helper import generate_signed_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["students"])


@router.get("/students")
def get_students(_admin: dict = Depends(verify_jwt)):
    """List all student_users with role 'student'."""
    try:
        collection = "student_users"
        docs = db.collection(collection).where("role", "==", "student").stream()

        students = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            if data.get("created_at") and hasattr(data["created_at"], "isoformat"):
                data["created_at"] = data["created_at"].isoformat()
            if data.get("updated_at") and hasattr(data["updated_at"], "isoformat"):
                data["updated_at"] = data["updated_at"].isoformat()
            students.append(data)

        return students
    except Exception as e:
        logger.exception("Failed to fetch students")
        raise HTTPException(status_code=500, detail=str(e))


def _sign_doc_urls(documents: dict) -> dict:
    """Replace GCS paths with time-limited signed URLs."""
    for _doc_type, doc_data in documents.items():
        for slot_key in ("applicant_upload", "official_scan"):
            slot = doc_data.get(slot_key)
            if slot and slot.get("gcs_path"):
                slot["file_url"] = generate_signed_url(slot["gcs_path"])
    return documents


@router.get("/students/{student_id}")
def get_student_detail(student_id: str, _admin: dict = Depends(verify_jwt)):
    """Get student info, enrollment history, and latest documents."""
    try:
        # Get student record by document ID
        student_collection = "student_users"
        student_doc = db.collection(student_collection).document(student_id).get()
        if not student_doc.exists:
            raise HTTPException(status_code=404, detail="Student not found")

        student = student_doc.to_dict()
        student["id"] = student_doc.id
        for ts_field in ("created_at", "updated_at"):
            if student.get(ts_field) and hasattr(student[ts_field], "isoformat"):
                student[ts_field] = student[ts_field].isoformat()

        # Get all enrollments for this student's email
        student_email = student.get("email", "")
        enrollment_collection = "pending_enrollment_application"
        enrollment_docs = (
            db.collection(enrollment_collection)
            .where("email", "==", student_email)
            .stream()
        )

        enrollments = []
        latest_documents = {}
        for doc in enrollment_docs:
            data = doc.to_dict()
            data["id"] = doc.id
            for ts_field in ("created_at", "updated_at"):
                if data.get(ts_field) and hasattr(data[ts_field], "isoformat"):
                    data[ts_field] = data[ts_field].isoformat()
            for entry in data.get("changelog", []):
                if hasattr(entry.get("updatedAt"), "isoformat"):
                    entry["updatedAt"] = entry["updatedAt"].isoformat()

            enrollments.append({
                "id": data["id"],
                "course": data.get("course", ""),
                "status": data.get("status", ""),
                "created_at": data.get("created_at"),
            })

            # Collect latest documents across all enrollments
            docs_data = data.get("documents", {})
            for doc_type, doc_info in docs_data.items():
                # Keep the most recent version of each document type
                if doc_type not in latest_documents:
                    latest_documents[doc_type] = doc_info
                else:
                    # Prefer official_scan, then check upload dates
                    existing = latest_documents[doc_type]
                    new_has_official = bool(doc_info.get("official_scan"))
                    old_has_official = bool(existing.get("official_scan"))
                    if new_has_official and not old_has_official:
                        latest_documents[doc_type] = doc_info

        # Sort enrollments by date descending
        enrollments.sort(key=lambda e: e.get("created_at") or "", reverse=True)

        # Sign URLs for documents
        if latest_documents:
            latest_documents = _sign_doc_urls(latest_documents)

        return {
            "student": student,
            "enrollments": enrollments,
            "documents": latest_documents,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch student detail")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/students/{student_id}/email")
def update_student_email(
    student_id: str,
    body: dict = Body(...),
    admin: dict = Depends(verify_jwt),
):
    """Change a student's email. Updates student_users and all linked enrollments."""
    new_email = (body.get("new_email") or "").strip().lower()
    if not new_email or "@" not in new_email:
        raise HTTPException(status_code=400, detail="A valid email address is required.")

    try:
        student_collection = "student_users"
        student_ref = db.collection(student_collection).document(student_id)
        student_doc = student_ref.get()
        if not student_doc.exists:
            raise HTTPException(status_code=404, detail="Student not found")

        student_data = student_doc.to_dict()
        old_email = student_data.get("email", "")

        if old_email.lower() == new_email:
            return {"message": "Email is already the same. No changes made."}

        # Check if new email is already taken by another student
        existing = list(
            db.collection(student_collection)
            .where("email", "==", new_email)
            .limit(1)
            .stream()
        )
        if existing and existing[0].id != student_id:
            raise HTTPException(
                status_code=409,
                detail="This email is already associated with another student account.",
            )

        admin_email = admin.get("sub", "unknown")
        now = datetime.now(timezone.utc).isoformat()

        # Update student_users record
        student_ref.update({
            "email": new_email,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

        # Update all enrollment applications that used the old email
        enrollment_collection = "pending_enrollment_application"
        enrollment_docs = list(
            db.collection(enrollment_collection)
            .where("email", "==", old_email)
            .stream()
        )

        updated_count = 0
        for edoc in enrollment_docs:
            edata = edoc.to_dict()
            existing_changelog = edata.get("changelog", [])
            edoc.reference.update({
                "email": new_email,
                "updated_at": firestore.SERVER_TIMESTAMP,
                "changelog": existing_changelog + [{
                    "field": "email",
                    "oldValue": old_email,
                    "newValue": new_email,
                    "updatedBy": admin_email,
                    "updatedAt": now,
                    "note": "Student email changed by admin (identity verified)",
                }],
            })
            updated_count += 1

        return {
            "message": f"Email updated from {old_email} to {new_email}. {updated_count} enrollment(s) updated.",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update student email")
        raise HTTPException(status_code=500, detail=str(e))
