"""
ASGI middleware that extracts Meta credentials from HTTP headers.

When the server runs in streamable-http mode, users pass their own
Meta API credentials via request headers. This middleware reads
those headers and stores them in a context var so _get_api() can
create a per-request MetaAPI client.

Headers:
    X-Meta-Access-Token (required)
    X-Meta-Phone-Number-Id (required)
    X-Meta-Business-Account-Id (required)
    X-Meta-App-Id (optional)
    X-Meta-Api-Version (optional, defaults to v24.0)
"""

import json
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from whatsapp_mcp.server import _request_credentials


class CredentialsMiddleware:
    """ASGI middleware to extract Meta credentials from HTTP headers."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        access_token = request.headers.get("x-meta-access-token", "")
        phone_number_id = request.headers.get("x-meta-phone-number-id", "")
        waba_id = request.headers.get("x-meta-business-account-id", "")

        # If any credential header is present, validate all required ones
        has_any = any([access_token, phone_number_id, waba_id])
        if has_any:
            missing = []
            if not access_token:
                missing.append("X-Meta-Access-Token")
            if not phone_number_id:
                missing.append("X-Meta-Phone-Number-Id")
            if not waba_id:
                missing.append("X-Meta-Business-Account-Id")

            if missing:
                response = JSONResponse(
                    {"error": f"Missing required headers: {', '.join(missing)}"},
                    status_code=400,
                )
                await response(scope, receive, send)
                return

            token = _request_credentials.set({
                "access_token": access_token,
                "waba_id": waba_id,
                "phone_number_id": phone_number_id,
                "app_id": request.headers.get("x-meta-app-id", ""),
                "api_version": request.headers.get("x-meta-api-version", "v24.0"),
            })
            try:
                await self.app(scope, receive, send)
            finally:
                _request_credentials.reset(token)
        else:
            await self.app(scope, receive, send)
