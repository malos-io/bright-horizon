import logging
import random
import string
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from reusable_components.email_notification_helper import send_email
from reusable_components.auth import create_applicant_jwt
from reusable_components.firebase import db, get_collection_name
from email_templates.otp_verification import get_otp_email_html

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/otp", tags=["otp"])

OTP_EXPIRY_MINUTES = 10
MAX_ATTEMPTS = 5


class OtpSendRequest(BaseModel):
    email: EmailStr


class OtpVerifyRequest(BaseModel):
    email: EmailStr
    code: str


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


@router.post("/send")
async def send_otp(request: OtpSendRequest):
    """Send OTP verification code to applicant's email."""
    email = request.email.lower().strip()

    # Check if an enrollment exists for this email
    collection = get_collection_name("pending_enrollment_application")
    docs = db.collection(collection).where("email", "==", email).limit(1).stream()
    enrollment = None
    for doc in docs:
        enrollment = doc.to_dict()
        break

    if not enrollment:
        raise HTTPException(status_code=404, detail="No application found for this email address.")

    # Rate limit: check if OTP was sent recently (within 60 seconds)
    otp_collection = get_collection_name("otp_codes")
    existing_doc = db.collection(otp_collection).document(email).get()
    if existing_doc.exists:
        existing_data = existing_doc.to_dict()
        created_at = existing_data.get("created_at")
        if created_at and (datetime.now(timezone.utc) - created_at.replace(tzinfo=timezone.utc)) < timedelta(seconds=60):
            raise HTTPException(status_code=429, detail="Please wait before requesting another code.")

    # Generate and store OTP
    code = generate_otp()
    db.collection(otp_collection).document(email).set({
        "code": code,
        "email": email,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
        "attempts": 0,
    })

    # Send OTP email
    name = enrollment.get("firstName", "Applicant")
    html = get_otp_email_html(code, name)
    try:
        await send_email(
            to=email,
            subject="Your Verification Code - Bright Horizons Institute",
            html_content=html,
        )
    except Exception as e:
        logger.exception("Failed to send OTP email to %s", email)
        raise HTTPException(status_code=500, detail="Failed to send verification email. Please try again.")

    return {"message": "Verification code sent to your email."}


@router.post("/verify")
async def verify_otp(request: OtpVerifyRequest):
    """Verify OTP code and return application data."""
    email = request.email.lower().strip()
    code = request.code.strip()

    # Lookup OTP
    otp_collection = get_collection_name("otp_codes")
    otp_doc = db.collection(otp_collection).document(email).get()

    if not otp_doc.exists:
        raise HTTPException(status_code=400, detail="No verification code found. Please request a new one.")

    otp_data = otp_doc.to_dict()

    # Check expiry
    expires_at = otp_data["expires_at"]
    if isinstance(expires_at, datetime):
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            db.collection(otp_collection).document(email).delete()
            raise HTTPException(status_code=400, detail="Verification code has expired. Please request a new one.")

    # Check attempts
    attempts = otp_data.get("attempts", 0)
    if attempts >= MAX_ATTEMPTS:
        db.collection(otp_collection).document(email).delete()
        raise HTTPException(status_code=400, detail="Too many failed attempts. Please request a new code.")

    # Verify code
    if otp_data["code"] != code:
        db.collection(otp_collection).document(email).update({"attempts": attempts + 1})
        remaining = MAX_ATTEMPTS - attempts - 1
        raise HTTPException(status_code=400, detail=f"Invalid code. {remaining} attempts remaining.")

    # Code is valid — delete OTP and fetch enrollment
    db.collection(otp_collection).document(email).delete()

    enrollment_collection = get_collection_name("pending_enrollment_application")
    docs = db.collection(enrollment_collection).where("email", "==", email).stream()

    applications = []
    for doc in docs:
        data = doc.to_dict()
        created_at = data.get("created_at")
        if created_at and hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat()
        applications.append({
            "id": doc.id,
            "firstName": data.get("firstName", ""),
            "lastName": data.get("lastName", ""),
            "middleName": data.get("middleName", ""),
            "course": data.get("course", ""),
            "status": data.get("status", "pending"),
            "created_at": created_at,
            "email": data.get("email", ""),
        })

    # Issue short-lived applicant JWT for authenticated access
    enrollment_ids = [app["id"] for app in applications]
    name = applications[0]["firstName"] if applications else ""
    token = create_applicant_jwt(email, name, enrollment_ids)

    return {"applications": applications, "token": token}
