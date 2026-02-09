import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, Request, UploadFile
from firebase_admin import firestore
from slowapi import Limiter
from slowapi.util import get_remote_address
from schemas.enrollment_schema import EnrollmentApplication
from reusable_components.firebase import db, get_collection_name
from reusable_components.auth import verify_jwt, verify_applicant_jwt
from reusable_components.gcloud_storage_helper import upload_file, delete_file, get_applicant_folder, generate_signed_url

limiter = Limiter(key_func=get_remote_address)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["enrollments"])

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

REQUIRED_DOCUMENTS = {
    "birth_certificate": {"label": "Birth Certificate", "required": True},
    "educational_credentials": {"label": "Educational Credentials", "required": True},
    "id_pictures": {"label": "ID Pictures", "required": False},
    "government_id": {"label": "Government Issued ID", "required": True},
    "proof_of_name_change": {"label": "Proof of Name Change", "required": False},
}

_VALID_SOURCES = {"applicant", "official"}

ENROLLMENT_STATUSES = {
    "pending_upload", "pending_review", "documents_rejected",
    "documents_accepted", "physical_docs_required", "completed",
    "pending",  # legacy alias
}

# Statuses that auto-status can overwrite (manual overrides like physical_docs_required won't be regressed)
_AUTO_STATUSES = {"pending", "pending_upload", "pending_review", "documents_rejected"}


def _recompute_enrollment_status(doc_ref, data: dict):
    """Auto-advance enrollment status based on document review states."""
    current_status = data.get("status", "pending_upload")
    if current_status not in _AUTO_STATUSES:
        return  # Don't regress manual overrides

    documents = data.get("documents", {})
    all_required_uploaded = True
    all_required_accepted = True
    any_rejected = False

    for doc_type, info in REQUIRED_DOCUMENTS.items():
        if not info["required"]:
            continue
        doc_data = documents.get(doc_type, {})
        has_file = bool(doc_data.get("applicant_upload") or doc_data.get("official_scan"))
        review_status = doc_data.get("review", {}).get("status", "pending")

        if not has_file:
            all_required_uploaded = False
            all_required_accepted = False
        elif review_status == "rejected":
            any_rejected = True
            all_required_accepted = False
        elif review_status != "accepted":
            all_required_accepted = False

    if any_rejected:
        new_status = "documents_rejected"
    elif all_required_accepted:
        new_status = "documents_accepted"
    elif all_required_uploaded:
        new_status = "pending_review"
    else:
        new_status = "pending_upload"

    if new_status != current_status:
        doc_ref.update({"status": new_status, "updated_at": firestore.SERVER_TIMESTAMP})


def _build_birthdate(data: dict) -> str:
    """Build YYYY-MM-DD birthdate string from enrollment fields."""
    month_str = data.get("birthMonth", "")
    day_str = data.get("birthDay", "")
    year_str = data.get("birthYear", "")
    if not month_str or not day_str or not year_str:
        return ""
    try:
        m = MONTHS.index(month_str) + 1
        return f"{year_str}-{m:02d}-{int(day_str):02d}"
    except (ValueError, IndexError):
        return ""


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


def _sign_document_urls(documents: dict) -> dict:
    """Replace public file_url with time-limited signed URLs for all document slots."""
    for _doc_type, doc_data in documents.items():
        for slot_key in ("applicant_upload", "official_scan"):
            slot = doc_data.get(slot_key)
            if slot and slot.get("gcs_path"):
                slot["file_url"] = generate_signed_url(slot["gcs_path"])
    return documents


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
        doc_data["status"] = "pending_upload"
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
        if "documents" in data:
            data["documents"] = _sign_document_urls(data["documents"])
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

        # Validate status if provided
        if "status" in fields and fields["status"] not in ENROLLMENT_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status: {fields['status']}")

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


# ── Document management endpoints ──────────────────────────────────────


@router.get("/enrollments/{enrollment_id}/documents")
def get_documents(enrollment_id: str, _admin: dict = Depends(verify_jwt)):
    try:
        collection = get_collection_name("pending_enrollment_application")
        doc = db.collection(collection).document(enrollment_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        data = doc.to_dict()
        documents = _sign_document_urls(data.get("documents", {}))
        return {
            "document_types": REQUIRED_DOCUMENTS,
            "documents": documents,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch documents")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrollments/{enrollment_id}/documents/{doc_type}")
def upload_document(
    enrollment_id: str,
    doc_type: str,
    file: UploadFile = File(...),
    source: str = Query(default="official"),
    admin: dict = Depends(verify_jwt),
):
    if doc_type not in REQUIRED_DOCUMENTS:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {doc_type}")
    if source not in _VALID_SOURCES:
        raise HTTPException(status_code=400, detail="Invalid source. Must be 'applicant' or 'official'")

    try:
        collection = get_collection_name("pending_enrollment_application")
        doc_ref = db.collection(collection).document(enrollment_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        data = doc.to_dict()
        birthdate = _build_birthdate(data)
        if not birthdate:
            raise HTTPException(status_code=400, detail="Applicant birthdate is incomplete")

        folder = get_applicant_folder(
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
            birthdate=birthdate,
            middle_name=data.get("middleName", ""),
        )

        # Build filename: applicant_upload_birth_certificate.jpg or official_scan_birth_certificate.pdf
        ext = ""
        if file.filename and "." in file.filename:
            ext = file.filename.rsplit(".", 1)[1].lower()
        prefix = "applicant_upload" if source == "applicant" else "official_scan"
        gcs_filename = f"{prefix}_{doc_type}.{ext}" if ext else f"{prefix}_{doc_type}"
        gcs_path = f"{folder}/{gcs_filename}"

        file_bytes = file.file.read()
        content_type = file.content_type or "application/octet-stream"
        file_url = upload_file(file_bytes, gcs_path, content_type)

        admin_email = admin.get("sub", "unknown")
        now = datetime.now(timezone.utc).isoformat()

        slot_key = "applicant_upload" if source == "applicant" else "official_scan"
        doc_metadata = {
            "file_url": file_url,
            "file_name": file.filename or gcs_filename,
            "gcs_path": gcs_path,
            "uploaded_at": now,
            "uploaded_by": admin_email,
        }

        doc_ref.update({
            f"documents.{doc_type}.{slot_key}": doc_metadata,
            f"documents.{doc_type}.review.status": "uploaded",
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

        # Re-read and auto-advance enrollment status
        updated_data = doc_ref.get().to_dict()
        _recompute_enrollment_status(doc_ref, updated_data)

        return {"message": "Document uploaded", "slot": slot_key, "metadata": doc_metadata}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to upload document")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/enrollments/{enrollment_id}/documents/{doc_type}")
def delete_document(
    enrollment_id: str,
    doc_type: str,
    source: str = Query(default="official"),
    admin: dict = Depends(verify_jwt),
):
    if doc_type not in REQUIRED_DOCUMENTS:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {doc_type}")
    if source not in _VALID_SOURCES:
        raise HTTPException(status_code=400, detail="Invalid source. Must be 'applicant' or 'official'")

    try:
        collection = get_collection_name("pending_enrollment_application")
        doc_ref = db.collection(collection).document(enrollment_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        data = doc.to_dict()
        slot_key = "applicant_upload" if source == "applicant" else "official_scan"
        documents = data.get("documents", {})
        doc_data = documents.get(doc_type, {})
        slot_data = doc_data.get(slot_key)

        if not slot_data:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete from GCS
        gcs_path = slot_data.get("gcs_path")
        if gcs_path:
            try:
                delete_file(gcs_path)
            except Exception:
                logger.warning(f"Failed to delete GCS file: {gcs_path}")

        # Remove from Firestore
        doc_ref.update({
            f"documents.{doc_type}.{slot_key}": firestore.DELETE_FIELD,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

        # If both slots are now empty, reset review to pending
        updated_data = doc_ref.get().to_dict()
        updated_doc = updated_data.get("documents", {}).get(doc_type, {})
        if not updated_doc.get("applicant_upload") and not updated_doc.get("official_scan"):
            doc_ref.update({f"documents.{doc_type}.review": {"status": "pending"}})
            updated_data = doc_ref.get().to_dict()

        _recompute_enrollment_status(doc_ref, updated_data)

        return {"message": "Document deleted", "slot": slot_key}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete document")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrollments/{enrollment_id}/documents/{doc_type}/review")
def review_document(
    enrollment_id: str,
    doc_type: str,
    body: dict = Body(...),
    admin: dict = Depends(verify_jwt),
):
    if doc_type not in REQUIRED_DOCUMENTS:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {doc_type}")

    status = body.get("status")
    if status not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be 'accepted' or 'rejected'")

    reject_reason = body.get("reject_reason", "")
    if status == "rejected" and not reject_reason.strip():
        raise HTTPException(status_code=400, detail="Reject reason is required")

    try:
        collection = get_collection_name("pending_enrollment_application")
        doc_ref = db.collection(collection).document(enrollment_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        data = doc.to_dict()
        doc_data = data.get("documents", {}).get(doc_type, {})

        # Must have at least one file to review
        if not doc_data.get("applicant_upload") and not doc_data.get("official_scan"):
            raise HTTPException(status_code=400, detail="No file uploaded for this document")

        admin_email = admin.get("sub", "unknown")
        now = datetime.now(timezone.utc).isoformat()

        old_review = doc_data.get("review", {})
        old_status = old_review.get("status", "uploaded")

        review = {
            "status": status,
            "reviewed_by": admin_email,
            "reviewed_at": now,
        }
        if status == "rejected":
            review["reject_reason"] = reject_reason.strip()

        # Append changelog entry
        existing_changelog = data.get("changelog", [])
        changelog_entry = {
            "field": f"document_review.{doc_type}",
            "oldValue": old_status,
            "newValue": status,
            "updatedBy": admin_email,
            "updatedAt": now,
        }
        if status == "rejected":
            changelog_entry["newValue"] = f"rejected: {reject_reason.strip()}"

        doc_ref.update({
            f"documents.{doc_type}.review": review,
            "changelog": existing_changelog + [changelog_entry],
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

        # Auto-advance enrollment status
        updated_data = doc_ref.get().to_dict()
        _recompute_enrollment_status(doc_ref, updated_data)

        return {"message": f"Document {status}", "review": review}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to review document")
        raise HTTPException(status_code=500, detail=str(e))


# ── Applicant-facing endpoints (OTP-verified JWT) ─────────────────────


def _verify_enrollment_ownership(enrollment_id: str, applicant: dict):
    """Verify the applicant JWT owns the enrollment. Returns (doc_ref, data)."""
    if enrollment_id not in applicant.get("enrollment_ids", []):
        raise HTTPException(status_code=403, detail="Access denied")

    collection = get_collection_name("pending_enrollment_application")
    doc_ref = db.collection(collection).document(enrollment_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    data = doc.to_dict()
    if data.get("email", "").lower() != applicant.get("sub", "").lower():
        raise HTTPException(status_code=403, detail="Access denied")

    return doc_ref, data


@router.get("/applicant/enrollments/{enrollment_id}")
def get_applicant_enrollment(enrollment_id: str, applicant: dict = Depends(verify_applicant_jwt)):
    try:
        _doc_ref, data = _verify_enrollment_ownership(enrollment_id, applicant)
        data["id"] = enrollment_id
        data["age"] = _compute_age(data)
        if "documents" in data:
            data["documents"] = _sign_document_urls(data["documents"])
        if data.get("created_at"):
            data["created_at"] = data["created_at"].isoformat()
        if data.get("updated_at"):
            data["updated_at"] = data["updated_at"].isoformat()
        data.pop("changelog", None)
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch applicant enrollment")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applicant/enrollments/{enrollment_id}/documents")
def get_applicant_documents(enrollment_id: str, applicant: dict = Depends(verify_applicant_jwt)):
    try:
        _doc_ref, data = _verify_enrollment_ownership(enrollment_id, applicant)
        documents = _sign_document_urls(data.get("documents", {}))
        return {
            "document_types": REQUIRED_DOCUMENTS,
            "documents": documents,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch applicant documents")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applicant/enrollments/{enrollment_id}/documents/{doc_type}")
def upload_applicant_document(
    enrollment_id: str,
    doc_type: str,
    file: UploadFile = File(...),
    applicant: dict = Depends(verify_applicant_jwt),
):
    if doc_type not in REQUIRED_DOCUMENTS:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {doc_type}")

    try:
        doc_ref, data = _verify_enrollment_ownership(enrollment_id, applicant)

        birthdate = _build_birthdate(data)
        if not birthdate:
            raise HTTPException(status_code=400, detail="Applicant birthdate is incomplete")

        folder = get_applicant_folder(
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
            birthdate=birthdate,
            middle_name=data.get("middleName", ""),
        )

        ext = ""
        if file.filename and "." in file.filename:
            ext = file.filename.rsplit(".", 1)[1].lower()
        gcs_filename = f"applicant_upload_{doc_type}.{ext}" if ext else f"applicant_upload_{doc_type}"
        gcs_path = f"{folder}/{gcs_filename}"

        file_bytes = file.file.read()
        content_type = file.content_type or "application/octet-stream"
        file_url = upload_file(file_bytes, gcs_path, content_type)

        applicant_email = applicant.get("sub", "unknown")
        now = datetime.now(timezone.utc).isoformat()

        doc_metadata = {
            "file_url": file_url,
            "file_name": file.filename or gcs_filename,
            "gcs_path": gcs_path,
            "uploaded_at": now,
            "uploaded_by": applicant_email,
        }

        doc_ref.update({
            f"documents.{doc_type}.applicant_upload": doc_metadata,
            f"documents.{doc_type}.review.status": "uploaded",
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

        updated_data = doc_ref.get().to_dict()
        _recompute_enrollment_status(doc_ref, updated_data)

        return {"message": "Document uploaded", "slot": "applicant_upload", "metadata": doc_metadata}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to upload applicant document")
        raise HTTPException(status_code=500, detail=str(e))


# Fields applicants may never edit
_APPLICANT_PROTECTED_FIELDS = {
    "id", "created_at", "updated_at", "changelog", "status",
    "documents", "email", "course", "certificationAgreed",
}


@router.patch("/applicant/enrollments/{enrollment_id}")
def update_applicant_enrollment(
    enrollment_id: str,
    fields: dict = Body(...),
    applicant: dict = Depends(verify_applicant_jwt),
):
    try:
        doc_ref, data = _verify_enrollment_ownership(enrollment_id, applicant)

        # Only allow edits while pending upload
        if data.get("status", "pending_upload") not in ("pending_upload", "pending"):
            raise HTTPException(
                status_code=403,
                detail="Application can only be edited while status is 'Pending Upload of Required Documents'",
            )

        applicant_email = applicant.get("sub", "unknown")
        now = datetime.now(timezone.utc).isoformat()

        changelog_entries = []
        updates = {}

        for key, new_value in fields.items():
            if key in _APPLICANT_PROTECTED_FIELDS:
                continue
            old_value = data.get(key, "")
            if str(old_value) != str(new_value):
                changelog_entries.append({
                    "field": key,
                    "oldValue": old_value if old_value is not None else "",
                    "newValue": new_value if new_value is not None else "",
                    "updatedBy": applicant_email,
                    "updatedAt": now,
                })
                updates[key] = new_value

        if not updates:
            return {"message": "No changes detected"}

        existing_changelog = data.get("changelog", [])
        updates["changelog"] = existing_changelog + changelog_entries
        updates["updated_at"] = firestore.SERVER_TIMESTAMP

        doc_ref.update(updates)

        return {"message": f"{len(changelog_entries)} field(s) updated", "changes": changelog_entries}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update applicant enrollment")
        raise HTTPException(status_code=500, detail=str(e))
