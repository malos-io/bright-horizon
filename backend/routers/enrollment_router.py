import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from firebase_admin import firestore
from slowapi import Limiter
from slowapi.util import get_remote_address
from schemas.enrollment_schema import EnrollmentApplication
from reusable_components.firebase import db, get_collection_name
from reusable_components.auth import verify_jwt

limiter = Limiter(key_func=get_remote_address)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["enrollments"])


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
        logger.exception("Failed to submit enrollment")
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

        return {"message": "Enrollment submitted", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
