import logging

from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from pydantic import BaseModel
from reusable_components.auth import verify_jwt
from reusable_components.firebase import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/staff", tags=["staff"])


class StaffRequest(BaseModel):
    email: str
    role: str


class StaffUpdateRequest(BaseModel):
    role: str


@router.get("")
def list_staff(_admin: dict = Depends(verify_jwt)):
    """List all staff from brighthii_staffs collection."""
    try:
        collection = "brighthii_staffs"
        docs = db.collection(collection).stream()

        staff = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            if data.get("created_at"):
                data["created_at"] = data["created_at"].isoformat()
            staff.append(data)

        return staff
    except Exception as e:
        logger.exception("Failed to list staff")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
def add_staff(request: StaffRequest, _admin: dict = Depends(verify_jwt)):
    """Add a new staff member."""
    try:
        collection = "brighthii_staffs"
        doc_ref = db.collection(collection).document(request.email)

        if doc_ref.get().exists:
            raise HTTPException(status_code=409, detail="Staff member already exists")

        doc_ref.set({
            "email": request.email,
            "role": request.role,
            "created_at": firestore.SERVER_TIMESTAMP,
        })

        return {"message": "Staff member added", "email": request.email}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to add staff")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{email}")
def update_staff_role(email: str, request: StaffUpdateRequest, _admin: dict = Depends(verify_jwt)):
    """Update a staff member's role."""
    try:
        collection = "brighthii_staffs"
        doc_ref = db.collection(collection).document(email)

        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Staff member not found")

        doc_ref.update({"role": request.role})

        return {"message": "Role updated", "email": email, "role": request.role}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update staff role")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{email}")
def remove_staff(email: str, payload: dict = Depends(verify_jwt)):
    """Remove a staff member."""
    try:
        # Prevent self-removal
        if payload["sub"] == email:
            raise HTTPException(status_code=400, detail="Cannot remove yourself")

        collection = "brighthii_staffs"
        doc_ref = db.collection(collection).document(email)

        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Staff member not found")

        doc_ref.delete()

        return {"message": "Staff member removed", "email": email}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to remove staff")
        raise HTTPException(status_code=500, detail=str(e))
