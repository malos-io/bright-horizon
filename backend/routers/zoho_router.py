import logging
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from reusable_components.auth import create_jwt, refresh_jwt, verify_jwt
from reusable_components.firebase import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/zoho", tags=["zoho-auth"])

ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID", "")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
ZOHO_REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI", "")
ADMIN_FRONTEND_URL = os.getenv("ADMIN_FRONTEND_URL", "")
ZOHO_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
ZOHO_USERINFO_URL = "https://accounts.zoho.com/oauth/user/info"


@router.get("/callback")
async def zoho_callback(code: str):
    """
    Zoho redirects here after admin login.
    Exchange auth code for tokens, store in Firestore, return JWT.
    """
    try:
        # Exchange auth code for access + refresh tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                ZOHO_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": ZOHO_CLIENT_ID,
                    "client_secret": ZOHO_CLIENT_SECRET,
                    "redirect_uri": ZOHO_REDIRECT_URI,
                    "code": code,
                },
            )

        token_data = token_response.json()

        if "error" in token_data:
            logger.error("Zoho token exchange failed: %s", token_data)
            raise HTTPException(status_code=400, detail=token_data.get("error"))

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token", "")

        # Get user info from Zoho
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                ZOHO_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        user_data = user_response.json()
        email = user_data.get("Email", "")
        first_name = user_data.get("First_Name", "")
        last_name = user_data.get("Last_Name", "")

        if not email:
            raise HTTPException(status_code=400, detail="Could not retrieve user email from Zoho")

        # Check if this email is an authorized admin
        staff_doc = db.collection("brighthii_staffs").document(email).get()
        if not staff_doc.exists or staff_doc.to_dict().get("role") != "admin":
            logger.warning("Unauthorized admin login attempt: %s", email)
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=f"{ADMIN_FRONTEND_URL}/login?error=unauthorized")

        # Store Zoho tokens in Firestore (keyed by email)
        collection = "zoho_tokens"
        db.collection(collection).document(email).set({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        })

        # Create our own JWT for frontend auth
        jwt_token = create_jwt({
            "email": email,
            "name": f"{first_name} {last_name}",
        })

        # Redirect back to admin frontend with JWT
        redirect_url = f"{ADMIN_FRONTEND_URL}/auth/callback?token={jwt_token}&name={first_name}+{last_name}&email={email}"
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=redirect_url)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Zoho OAuth callback failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-token")
async def refresh_admin_token(payload: dict = Depends(verify_jwt)):
    """Sliding window: return a new JWT with refreshed expiry."""
    new_token = refresh_jwt(payload)
    return {"token": new_token}


@router.get("/me")
async def get_current_user(payload: dict = Depends(verify_jwt)):
    """Return current user info from JWT."""
    return {
        "email": payload.get("sub"),
        "name": payload.get("name"),
    }
