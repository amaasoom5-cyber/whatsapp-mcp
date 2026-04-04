"""
Meta Graph API Client for WhatsApp Business API.

Async httpx client that handles template CRUD and message sending.
"""

import copy
import logging
from typing import Any, Optional

import httpx
from pydantic import ValidationError

from whatsapp_mcp.validators.create import VALIDATOR_MAP
from whatsapp_mcp.validators.send import SEND_VALIDATOR_MAP

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30.0


class MetaAPIError(Exception):
    """Raised when Meta Graph API returns an error."""

    def __init__(self, message: str, code: int | None = None, raw: dict | None = None):
        self.code = code
        self.raw = raw or {}
        super().__init__(message)


class MetaAPI:
    """
    Async client for Meta's WhatsApp Business Graph API.

    Handles template management (create, list, status, delete) and
    message sending (template messages).
    """

    BASE_URL = "https://graph.facebook.com/"

    def __init__(
        self,
        access_token: str,
        waba_id: str,
        phone_number_id: str,
        app_id: str = "",
        api_version: str = "v24.0",
    ):
        self.access_token = access_token
        self.waba_id = waba_id
        self.phone_number_id = phone_number_id
        self.app_id = app_id
        self.api_version = api_version
        self._client: httpx.AsyncClient | None = None

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    @property
    def _base(self) -> str:
        return f"{self.BASE_URL}{self.api_version}/"

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=DEFAULT_TIMEOUT,
                headers=self._headers,
            )
        return self._client

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ── Internal helpers ──────────────────────────────────────────────

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> dict:
        """Make an HTTP request and handle Meta API errors."""
        client = await self._get_client()
        resp = await client.request(method, url, **kwargs)

        try:
            data = resp.json()
        except Exception:
            resp.raise_for_status()
            return {}

        if "error" in data:
            err = data["error"]
            raise MetaAPIError(
                message=err.get("message", str(err)),
                code=err.get("code"),
                raw=data,
            )

        return data

    def _get_create_validator(self, category: str, template_type: str, is_lto: bool = False, buttons: list | None = None):
        """Pick the correct creation validator based on category/type."""
        ttype = (template_type or "").upper()
        cat = (category or "").upper()

        # Special types get their own validator
        if ttype == "CAROUSEL":
            return VALIDATOR_MAP.get("CAROUSEL")
        if ttype == "CATALOG":
            return VALIDATOR_MAP.get("CATALOG")
        if ttype == "ORDER_DETAILS":
            return VALIDATOR_MAP.get("ORDER_DETAILS")
        if is_lto:
            return VALIDATOR_MAP.get("LTO")

        # Check for coupon code (copy_code button)
        if buttons:
            for btn in buttons:
                if isinstance(btn, dict) and (btn.get("type") or "").upper() == "COPY_CODE":
                    return VALIDATOR_MAP.get("COUPON_CODE")

        # Fall back to category-based
        return VALIDATOR_MAP.get(cat)

    def _get_send_validator(self, template_type: str):
        """Pick the correct send validator for a template type."""
        ttype = (template_type or "").upper()
        return SEND_VALIDATOR_MAP.get(ttype)

    # ── Template operations ───────────────────────────────────────────

    async def submit_template(self, payload: dict) -> dict:
        """
        Submit a template to Meta for approval.

        POST /{waba_id}/message_templates

        Returns the Meta response with template ID on success.
        """
        url = f"{self._base}{self.waba_id}/message_templates"
        logger.info(f"Submitting template: name={payload.get('name')}, category={payload.get('category')}")

        data = await self._request("POST", url, json=payload)
        logger.info(f"Template submitted: id={data.get('id')}, status={data.get('status')}")
        return data

    async def list_templates(
        self,
        limit: int = 20,
        after: str | None = None,
        name: str | None = None,
        status: str | None = None,
        category: str | None = None,
    ) -> dict:
        """
        List message templates.

        GET /{waba_id}/message_templates

        Returns {data: [...], paging: {...}}
        """
        url = f"{self._base}{self.waba_id}/message_templates"
        params: dict[str, Any] = {
            "limit": limit,
            "fields": "name,status,category,language,components,quality_score,rejected_reason",
        }
        if after:
            params["after"] = after
        if name:
            params["name"] = name
        if status:
            params["status"] = status.upper()
        if category:
            params["category"] = category.upper()

        data = await self._request("GET", url, params=params)
        return data

    async def get_template(self, template_id: str) -> dict:
        """
        Get a single template by its Meta template ID.

        GET /{template_id}
        """
        url = f"{self._base}{template_id}"
        params = {
            "fields": "name,status,category,language,components,quality_score,rejected_reason",
        }
        data = await self._request("GET", url, params=params)
        return data

    async def delete_template(self, template_name: str) -> dict:
        """
        Delete a template by name.

        DELETE /{waba_id}/message_templates?name={name}
        """
        url = f"{self._base}{self.waba_id}/message_templates"
        params = {"name": template_name}

        logger.info(f"Deleting template: name={template_name}")
        data = await self._request("DELETE", url, params=params)
        logger.info(f"Template deleted: {template_name}")
        return data

    async def send_message(self, payload: dict) -> dict:
        """
        Send a template message.

        POST /{phone_number_id}/messages
        """
        url = f"{self._base}{self.phone_number_id}/messages"
        data = await self._request("POST", url, json=payload)
        return data

    async def upload_media(
        self,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
    ) -> str:
        """
        Upload media for template headers using the Resumable Upload API.

        Returns the file handle ID.
        """
        if not self.app_id:
            raise MetaAPIError("META_APP_ID is required for media uploads.")

        client = await self._get_client()

        # Step 1: Create upload session
        session_url = f"{self._base}{self.app_id}/uploads"
        session_resp = await client.post(
            session_url,
            data={
                "file_length": len(file_bytes),
                "file_type": mime_type,
                "file_name": filename,
            },
        )
        session_data = session_resp.json()
        if "error" in session_data:
            raise MetaAPIError(
                session_data["error"].get("message", "Upload session failed"),
                raw=session_data,
            )

        upload_session_id = session_data.get("id")
        if not upload_session_id:
            raise MetaAPIError("No upload session ID returned.")

        # Step 2: Upload file data
        upload_url = f"{self._base}{upload_session_id}"
        upload_resp = await client.post(
            upload_url,
            headers={
                "Authorization": f"OAuth {self.access_token}",
                "file_offset": "0",
            },
            content=file_bytes,
        )
        upload_data = upload_resp.json()
        if "error" in upload_data:
            raise MetaAPIError(
                upload_data["error"].get("message", "File upload failed"),
                raw=upload_data,
            )

        handle = upload_data.get("h")
        if not handle:
            raise MetaAPIError("No file handle returned from upload.")

        return handle

    # ── Validation helpers ────────────────────────────────────────────

    def validate_create_payload(
        self,
        payload: dict,
        category: str,
        template_type: str,
        is_lto: bool = False,
        buttons: list | None = None,
    ) -> list[dict]:
        """
        Validate a template creation payload.

        Returns a list of error dicts. Empty list = valid.
        """
        validator_cls = self._get_create_validator(category, template_type, is_lto, buttons)
        if not validator_cls:
            return []

        try:
            validator_cls(**copy.deepcopy(payload))
            return []
        except ValidationError as exc:
            return [
                {
                    "field": ".".join(str(loc) for loc in err.get("loc", [])),
                    "message": err.get("msg", ""),
                }
                for err in exc.errors()
            ]

    def validate_send_payload(self, template_type: str, payload: dict) -> list[dict]:
        """
        Validate a template send payload.

        Returns a list of error dicts. Empty list = valid.
        """
        validator_cls = self._get_send_validator(template_type)
        if not validator_cls:
            return []

        try:
            validator_cls(**copy.deepcopy(payload))
            return []
        except ValidationError as exc:
            return [
                {
                    "field": ".".join(str(loc) for loc in err.get("loc", [])),
                    "message": err.get("msg", ""),
                }
                for err in exc.errors()
            ]
