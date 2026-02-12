import logging
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from reusable_components.auth import verify_jwt
from reusable_components.firebase import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/email", tags=["email"])

ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID", "")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
ZOHO_MAIL_API = "https://mail.zoho.com/api"
ZOHO_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"


async def get_zoho_tokens(email: str) -> dict:
    """Get Zoho tokens from Firestore for the given admin email."""
    collection = "zoho_tokens"
    doc = db.collection(collection).document(email).get()
    if not doc.exists:
        raise HTTPException(status_code=401, detail="Zoho tokens not found. Please re-login.")
    return doc.to_dict()


async def refresh_zoho_access_token(email: str, refresh_token: str) -> str:
    """Use refresh token to get a new Zoho access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            ZOHO_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "client_id": ZOHO_CLIENT_ID,
                "client_secret": ZOHO_CLIENT_SECRET,
                "refresh_token": refresh_token,
            },
        )
    data = response.json()
    if "error" in data:
        raise HTTPException(status_code=401, detail="Zoho token refresh failed. Please re-login.")

    new_access_token = data["access_token"]

    # Update Firestore with new access token
    collection = "zoho_tokens"
    db.collection(collection).document(email).update({"access_token": new_access_token})

    return new_access_token


async def zoho_mail_request(method: str, url: str, access_token: str, **kwargs):
    """Make a request to Zoho Mail API with the oauthtoken header."""
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await getattr(client, method)(url, headers=headers, **kwargs)
    return response


async def zoho_request_with_refresh(method: str, url: str, email: str, tokens: dict, **kwargs):
    """Make Zoho API request, refreshing token on 401."""
    response = await zoho_mail_request(method, url, tokens["access_token"], **kwargs)

    # If unauthorized, refresh token and retry once
    if response.status_code == 401:
        new_token = await refresh_zoho_access_token(email, tokens["refresh_token"])
        response = await zoho_mail_request(method, url, new_token, **kwargs)

    return response


async def get_account_id(email: str, tokens: dict) -> str:
    """Get the Zoho Mail account ID for the authenticated user."""
    response = await zoho_request_with_refresh("get", f"{ZOHO_MAIL_API}/accounts", email, tokens)
    data = response.json()

    if not data.get("data"):
        raise HTTPException(status_code=400, detail="No Zoho Mail accounts found")

    return data["data"][0]["accountId"]


async def get_inbox_folder_id(account_id: str, email: str, tokens: dict) -> str:
    """Get the numeric folder ID for the Inbox."""
    url = f"{ZOHO_MAIL_API}/accounts/{account_id}/folders"
    response = await zoho_request_with_refresh("get", url, email, tokens)
    data = response.json()
    # Zoho may return a list directly or wrap in {"data": [...]}
    folders = data if isinstance(data, list) else data.get("data", [])
    for folder in folders:
        if not isinstance(folder, dict):
            continue
        # Check for Zoho error response
        if "code" in folder and folder["code"] != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Zoho API error: {folder.get('description', folder.get('code'))}",
            )
        if folder.get("folderName", "").lower() == "inbox":
            return folder["folderId"]

    raise HTTPException(status_code=400, detail="Inbox folder not found")


@router.get("/inbox")
async def get_inbox(limit: int = 20, start: int = 1, payload: dict = Depends(verify_jwt)):
    """Fetch inbox emails from Zoho Mail."""
    try:
        email = payload["sub"]
        tokens = await get_zoho_tokens(email)
        account_id = await get_account_id(email, tokens)

        # Get actual inbox folder ID
        tokens = await get_zoho_tokens(email)
        folder_id = await get_inbox_folder_id(account_id, email, tokens)

        tokens = await get_zoho_tokens(email)
        url = f"{ZOHO_MAIL_API}/accounts/{account_id}/messages/view"
        response = await zoho_request_with_refresh(
            "get", url, email, tokens,
            params={"limit": limit, "start": start, "folderId": folder_id},
        )

        data = response.json()
        messages = data if isinstance(data, list) else data.get("data", [])
        return messages
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch inbox")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{folder_id}/{message_id}")
async def get_message(folder_id: str, message_id: str, payload: dict = Depends(verify_jwt)):
    """Fetch a specific email's content from Zoho Mail."""
    try:
        email = payload["sub"]
        tokens = await get_zoho_tokens(email)
        account_id = await get_account_id(email, tokens)

        tokens = await get_zoho_tokens(email)

        url = f"{ZOHO_MAIL_API}/accounts/{account_id}/folders/{folder_id}/messages/{message_id}/content"
        response = await zoho_request_with_refresh("get", url, email, tokens)

        data = response.json()
        return data.get("data", {})
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch message")
        raise HTTPException(status_code=500, detail=str(e))


