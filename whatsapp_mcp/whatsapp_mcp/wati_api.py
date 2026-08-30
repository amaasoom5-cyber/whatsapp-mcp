"""
WATI API client for WhatsApp.
"""

from typing import Any

import httpx


DEFAULT_TIMEOUT = 30.0


class WATIAPIError(Exception):
    """Raised when WATI returns an API error."""

    def __init__(
        self,
        message: str,
        code: int | None = None,
        raw: Any = None,
    ):
        self.code = code
        self.raw = raw
        super().__init__(message)


class WATIAPI:
    """Async client for the WATI WhatsApp API."""

    def __init__(
        self,
        api_token: str,
        api_endpoint: str,
    ):
        self.api_token = api_token.strip()
        self.api_endpoint = api_endpoint.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=DEFAULT_TIMEOUT,
                headers=self._headers,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        client = await self._get_client()

        url = f"{self.api_endpoint}{path}"

        response = await client.request(
            method,
            url,
            **kwargs,
        )

        try:
            data = response.json()
        except Exception:
            data = {
                "status_code": response.status_code,
                "text": response.text,
            }

        if response.is_error:
            message = "WATI API request failed"

            if isinstance(data, dict):
                message = (
                    data.get("message")
                    or data.get("error")
                    or data.get("detail")
                    or message
                )

            raise WATIAPIError(
                str(message),
                code=response.status_code,
                raw=data,
            )

        return data

    # ------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------

    async def list_templates(
        self,
        page_number: int = 1,
        page_size: int = 20,
        channel: str | None = None,
    ) -> Any:
        params = {
            "page_number": page_number,
            "page_size": page_size,
        }

        if channel:
            params["channel"] = channel

        return await self._request(
            "GET",
            "/api/ext/v3/messageTemplates",
            params=params,
        )

    async def get_template(
        self,
        template_id: str,
    ) -> Any:
        return await self._request(
            "GET",
            f"/api/ext/v3/messageTemplates/{template_id}",
        )

    async def send_template(
        self,
        phone_number: str,
        template_name: str,
        parameters: list[dict] | None = None,
        broadcast_name: str = "MCP",
        channel: str | None = None,
    ) -> Any:
        recipient: dict[str, Any] = {
            "phone_number": phone_number,
        }

        if parameters:
            recipient["parameters"] = parameters

        payload = {
            "channel": channel,
            "template_name": template_name,
            "broadcast_name": broadcast_name,
            "recipients": [recipient],
        }

        return await self._request(
            "POST",
            "/api/ext/v3/messageTemplates/send",
            json=payload,
        )

    # ------------------------------------------------------------
    # Conversations
    # ------------------------------------------------------------

    async def send_text_message(
        self,
        target: str,
        text: str,
    ) -> Any:
        payload = {
            "target": target,
            "text": text,
        }

        return await self._request(
            "POST",
            "/api/ext/v3/conversations/messages/text",
            json=payload,
        )
