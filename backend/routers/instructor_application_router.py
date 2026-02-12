import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from firebase_admin import firestore
from slowapi import Limiter
from slowapi.util import get_remote_address
from schemas.instructor_application_schema import InstructorApplication
from reusable_components.firebase import db
from reusable_components.auth import verify_jwt
from reusable_components.email_notification_helper import send_email
from email_templates.admin_new_instructor_application import get_admin_new_instructor_application_email_html

NOTIFICATION_FROM = "notifications@brighthii.com"
ADMISSIONS_EMAIL = "admissions@brighthii.com"

limiter = Limiter(key_func=get_remote_address)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["instructor-applications"])

STATUSES = {"new", "reviewed", "contacted", "archived"}


@router.post("/instructor-applications")
@limiter.limit("5/minute")
async def submit_instructor_application(request: Request, application: InstructorApplication):
    try:
        collection = "instructor_applications"
        doc_data = application.model_dump()
        doc_data["status"] = "new"
        doc_data["created_at"] = firestore.SERVER_TIMESTAMP

        doc_ref = db.collection(collection).add(doc_data)
        doc_id = doc_ref[1].id

        # Notify admissions team
        try:
            applicant_name = f"{application.firstName} {application.lastName}"
            subject = f"New Instructor Application: {applicant_name}"
            html = get_admin_new_instructor_application_email_html(
                applicant_name=applicant_name,
                email=application.email,
                contact_no=application.contactNo,
                courses_interested=application.coursesInterested,
                other_courses=application.otherCourses or "",
                application_id=doc_id,
            )
            await send_email(
                to=ADMISSIONS_EMAIL,
                subject=subject,
                html_content=html,
                from_email=NOTIFICATION_FROM,
            )
        except Exception as email_err:
            logger.warning("Failed to send instructor application admin email: %s", email_err)

        return {"message": "Application submitted successfully", "id": doc_id}
    except Exception as e:
        logger.exception("Failed to submit instructor application")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instructor-applications")
def get_instructor_applications(_admin: dict = Depends(verify_jwt)):
    try:
        collection = "instructor_applications"
        docs = db.collection(collection).order_by(
            "created_at", direction=firestore.Query.DESCENDING
        ).stream()

        applications = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            if data.get("created_at"):
                data["created_at"] = data["created_at"].isoformat()
            if data.get("updated_at"):
                data["updated_at"] = data["updated_at"].isoformat()
            applications.append(data)

        return applications
    except Exception as e:
        logger.exception("Failed to fetch instructor applications")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instructor-applications/{application_id}")
def get_instructor_application(application_id: str, _admin: dict = Depends(verify_jwt)):
    try:
        collection = "instructor_applications"
        doc = db.collection(collection).document(application_id).get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Application not found")

        data = doc.to_dict()
        data["id"] = doc.id
        if data.get("created_at"):
            data["created_at"] = data["created_at"].isoformat()
        if data.get("updated_at"):
            data["updated_at"] = data["updated_at"].isoformat()
        for entry in data.get("changelog", []):
            if hasattr(entry.get("updatedAt"), "isoformat"):
                entry["updatedAt"] = entry["updatedAt"].isoformat()

        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch instructor application")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/instructor-applications/{application_id}")
def update_instructor_application(
    application_id: str,
    fields: dict = Body(...),
    admin: dict = Depends(verify_jwt),
):
    try:
        collection = "instructor_applications"
        doc_ref = db.collection(collection).document(application_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Application not found")

        current = doc.to_dict()
        admin_email = admin.get("sub", "unknown")
        now = datetime.now(timezone.utc).isoformat()

        if "status" in fields and fields["status"] not in STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status: {fields['status']}")

        changelog_entries = []
        updates = {}
        protected = {"id", "created_at", "updated_at", "changelog"}

        for key, new_value in fields.items():
            if key in protected:
                continue
            old_value = current.get(key, "")
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

        existing_changelog = current.get("changelog", [])
        updates["changelog"] = existing_changelog + changelog_entries
        updates["updated_at"] = firestore.SERVER_TIMESTAMP

        doc_ref.update(updates)

        return {"message": f"{len(changelog_entries)} field(s) updated", "changes": changelog_entries}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update instructor application")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/instructor-applications/{application_id}")
def delete_instructor_application(application_id: str, _admin: dict = Depends(verify_jwt)):
    try:
        collection = "instructor_applications"
        doc_ref = db.collection(collection).document(application_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Application not found")

        doc_ref.delete()

        return {"message": "Application deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete instructor application")
        raise HTTPException(status_code=500, detail=str(e))
