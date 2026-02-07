"""
OAuth2 integration with Microsoft Entra ID (Azure AD).
Handles authorization URL generation, token exchange, and user info extraction.
"""

import json
import base64
import httpx
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class EntraAuthClient:
    """Client for Entra ID OAuth2 flow."""

    def __init__(self):
        self.authority = f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}"
        self.token_url = f"{self.authority}/oauth2/v2.0/token"
        self.authorize_url = f"{self.authority}/oauth2/v2.0/authorize"

    def get_authorization_url(self, state: str, code_challenge: str) -> str:
        """
        Generate the Entra ID authorization URL for user login.
        Uses PKCE for enhanced security.
        """
        params = {
            "client_id": settings.ENTRA_CLIENT_ID,
            "redirect_uri": settings.ENTRA_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid profile email",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "prompt": "select_account",  # Always show account selection
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.authorize_url}?{query_string}"

    async def exchange_code_for_token(
        self, code: str, code_verifier: str
    ) -> dict:
        """
        Exchange authorization code for access and ID tokens.
        """
        payload = {
            "client_id": settings.ENTRA_CLIENT_ID,
            "client_secret": settings.ENTRA_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.ENTRA_REDIRECT_URI,
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
            "scope": "openid profile email",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=payload)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def extract_user_info(id_token_claims: dict) -> dict:
        """
        Extract user info from Entra ID token claims.
        Returns: {user_id, email, name, role}
        """
        email = id_token_claims.get("email") or id_token_claims.get("preferred_username")
        
        # Determine role from email domain or groups
        # For now: assume @aub.edu.lb is student, you can add other logic
        role = "student"
        if email and "professor" in email.lower():
            role = "professor"
        
        return {
            "user_id": id_token_claims.get("oid"),  # Object ID
            "email": email,
            "name": id_token_claims.get("name"),
            "role": role,
            "tenant_id": id_token_claims.get("tid"),
        }


entra_client = EntraAuthClient()


def decode_id_token(id_token: str) -> dict:
    """
    Decode JWT ID token without verification (we trust Microsoft's signature).
    Returns the claims payload.
    """
    try:
        # JWT format: header.payload.signature
        parts = id_token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        
        # Decode payload (add padding if needed)
        payload = parts[1]
        # Add padding
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        logger.error(f"Failed to decode ID token: {e}")
        raise
