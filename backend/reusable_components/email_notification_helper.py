import logging
import os

import httpx

logger = logging.getLogger(__name__)

ZOHO_MAIL_CLIENT_ID = os.getenv("ZOHO_MAIL_SELF_CLIENT_ID", "")
ZOHO_MAIL_CLIENT_SECRET = os.getenv("ZOHO_MAIL_SELF_SECRET_ID", "")
ZOHO_MAIL_REFRESH_TOKEN = os.getenv("ZOHO_MAIL_REFRESH_TOKEN", "")

ZOHO_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
ZOHO_MAIL_API = "https://mail.zoho.com/api"

# In-memory cache (lives for Cloud Run instance lifetime)
_access_token: str | None = None
_account_id: str | None = None


async def _refresh_access_token() -> str:
    """Exchange refresh token for a new access token."""
    global _access_token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            ZOHO_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "client_id": ZOHO_MAIL_CLIENT_ID,
                "client_secret": ZOHO_MAIL_CLIENT_SECRET,
                "refresh_token": ZOHO_MAIL_REFRESH_TOKEN,
            },
        )
    data = response.json()
    if "error" in data:
        logger.error("Zoho token refresh failed: %s", data)
        raise RuntimeError(f"Zoho token refresh failed: {data.get('error')}")

    _access_token = data["access_token"]
    return _access_token


async def _get_account_id() -> str:
    """Fetch and cache the Zoho Mail account ID."""
    global _account_id
    if _account_id:
        return _account_id

    token = await _get_access_token()
    response = await _make_request("get", f"{ZOHO_MAIL_API}/accounts", token=token)
    data = response.json()

    accounts = data if isinstance(data, list) else data.get("data", [])
    if not accounts:
        raise RuntimeError("No Zoho Mail accounts found")

    _account_id = accounts[0]["accountId"]
    return _account_id


async def _get_access_token() -> str:
    """Return cached access token or refresh it."""
    if _access_token:
        return _access_token
    return await _refresh_access_token()


async def _make_request(method: str, url: str, token: str | None = None, **kwargs) -> httpx.Response:
    """Make a Zoho Mail API request with auto-retry on 401."""
    if not token:
        token = await _get_access_token()

    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    async with httpx.AsyncClient() as client:
        response = await getattr(client, method)(url, headers=headers, **kwargs)

    if response.status_code == 401:
        new_token = await _refresh_access_token()
        headers = {"Authorization": f"Zoho-oauthtoken {new_token}"}
        async with httpx.AsyncClient() as client:
            response = await getattr(client, method)(url, headers=headers, **kwargs)

    return response


async def send_email(to: str, subject: str, html_content: str, from_email: str = "noreply@brighthii.com") -> dict:
    """
    Send an email via Zoho Mail API.

    Args:
        to: Recipient email address
        subject: Email subject line
        html_content: HTML body content

    Returns:
        Zoho API response data

    Raises:
        RuntimeError: If sending fails
    """
    account_id = await _get_account_id()
    url = f"{ZOHO_MAIL_API}/accounts/{account_id}/messages"

    response = await _make_request(
        "post",
        url,
        json={
            "fromAddress": from_email,
            "toAddress": to,
            "subject": subject,
            "content": html_content,
            "mailFormat": "html",
            "askReceipt": "no",
        },
    )

    data = response.json()
    if response.status_code != 200:
        logger.error("Zoho send email failed: %s", data)
        raise RuntimeError(f"Failed to send email: {data}")

    logger.info("Email sent to %s: %s", to, subject)
    return data
