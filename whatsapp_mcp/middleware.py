"""
ASGI middleware that extracts Meta credentials from HTTP requests.

When the server runs in HTTP mode (sse / streamable-http), per-request
credentials can be supplied in two ways:

1. **Authorization header** (recommended for MCP clients):
       Authorization: Bearer <base64-encoded JSON>
   The JSON must contain: access_token, phone_number_id, waba_id.
   Optional: app_id, api_version.

   This works with ChatGPT's Responses API (`authorization` field) and
   any client that supports bearer-token auth.

2. **X-Meta-* headers** (for direct HTTP / curl / scripts):
       X-Meta-Access-Token (required)
       X-Meta-Phone-Number-Id (required)
       X-Meta-Business-Account-Id (required)
       X-Meta-App-Id (optional)
       X-Meta-Api-Version (optional, defaults to v24.0)

If neither is present, the server falls back to environment variables.
"""

import base64
import json
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from whatsapp_mcp.server import _request_credentials


class CredentialsMiddleware:
    """ASGI middleware to extract Meta credentials from HTTP requests."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        creds = self._extract_from_bearer(request) or self._extract_from_headers(request)

        if isinstance(creds, JSONResponse):
            # Validation error — send it back
            await creds(scope, receive, send)
            return

        if creds:
            token = _request_credentials.set(creds)
            try:
                await self.app(scope, receive, send)
            finally:
                _request_credentials.reset(token)
        else:
            # No per-request credentials — fall back to env vars
            await self.app(scope, receive, send)

    def _extract_from_bearer(self, request: Request) -> dict | JSONResponse | None:
        """Extract credentials from Authorization header.

        Accepts:
          - Authorization: Bearer <base64-json>
          - Authorization: <base64-json>   (some clients omit Bearer prefix)
        """
        auth = request.headers.get("authorization", "")
        if not auth:
            return None

        # Strip "Bearer " prefix if present
        if auth.lower().startswith("bearer "):
            raw_token = auth[7:].strip()
        else:
            raw_token = auth.strip()

        if not raw_token:
            return None

        try:
            decoded = base64.b64decode(raw_token).decode("utf-8")
            data = json.loads(decoded)
        except Exception:
            return JSONResponse(
                {"error": "Invalid Authorization token: expected base64-encoded JSON with Meta credentials"},
                status_code=401,
            )

        access_token = data.get("access_token", "")
        phone_number_id = data.get("phone_number_id", "")
        waba_id = data.get("waba_id", "")

        missing = []
        if not access_token:
            missing.append("access_token")
        if not phone_number_id:
            missing.append("phone_number_id")
        if not waba_id:
            missing.append("waba_id")

        if missing:
            return JSONResponse(
                {"error": f"Bearer token missing required fields: {', '.join(missing)}"},
                status_code=401,
            )

        return {
            "access_token": access_token,
            "waba_id": waba_id,
            "phone_number_id": phone_number_id,
            "app_id": data.get("app_id", ""),
            "api_version": data.get("api_version", "v24.0"),
        }

    def _extract_from_headers(self, request: Request) -> dict | JSONResponse | None:
        """Extract credentials from X-Meta-* headers."""
        access_token = request.headers.get("x-meta-access-token", "")
        phone_number_id = request.headers.get("x-meta-phone-number-id", "")
        waba_id = request.headers.get("x-meta-business-account-id", "")

        has_any = any([access_token, phone_number_id, waba_id])
        if not has_any:
            return None

        missing = []
        if not access_token:
            missing.append("X-Meta-Access-Token")
        if not phone_number_id:
            missing.append("X-Meta-Phone-Number-Id")
        if not waba_id:
            missing.append("X-Meta-Business-Account-Id")

        if missing:
            return JSONResponse(
                {"error": f"Missing required headers: {', '.join(missing)}"},
                status_code=400,
            )

        return {
            "access_token": access_token,
            "waba_id": waba_id,
            "phone_number_id": phone_number_id,
            "app_id": request.headers.get("x-meta-app-id", ""),
            "api_version": request.headers.get("x-meta-api-version", "v24.0"),
        }
