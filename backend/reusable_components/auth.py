import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 60  # 1 hour sliding window
APPLICANT_JWT_EXPIRY_MINUTES = 480  # 8 hours


def create_jwt(user_data: dict) -> str:
    payload = {
        "sub": user_data["email"],
        "name": user_data.get("name", ""),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_applicant_jwt(email: str, name: str = "", enrollment_ids: list = None) -> str:
    """Create a short-lived JWT for an OTP-verified applicant."""
    payload = {
        "sub": email,
        "name": name,
        "role": "applicant",
        "enrollment_ids": enrollment_ids or [],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=APPLICANT_JWT_EXPIRY_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("role") == "applicant":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Applicant tokens cannot access admin endpoints",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def verify_applicant_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify a JWT and ensure it has the 'applicant' role."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("role") != "applicant":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not an applicant token",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def refresh_jwt(payload: dict) -> str:
    """Create a new JWT with refreshed expiry (sliding window)."""
    new_payload = {
        "sub": payload["sub"],
        "name": payload.get("name", ""),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(new_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
