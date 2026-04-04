"""
Tests for MetaAPI client — uses mocked HTTP responses.
"""

import json

import httpx
import pytest

from whatsapp_mcp.meta_api import MetaAPI, MetaAPIError


@pytest.fixture
def api():
    return MetaAPI(
        access_token="test_token",
        waba_id="123456",
        phone_number_id="789012",
        app_id="app123",
        api_version="v21.0",
    )


class TestMetaAPIInit:
    def test_init(self, api):
        assert api.access_token == "test_token"
        assert api.waba_id == "123456"
        assert api.phone_number_id == "789012"
        assert api._base == "https://graph.facebook.com/v21.0/"

    def test_headers(self, api):
        assert api._headers["Authorization"] == "Bearer test_token"
        assert api._headers["Content-Type"] == "application/json"


class TestMetaAPIValidation:
    def test_validate_marketing_valid(self, api):
        payload = {
            "name": "test",
            "category": "MARKETING",
            "language": "en",
            "components": [{"type": "body", "text": "Hello"}],
        }
        errors = api.validate_create_payload(payload, "MARKETING", "TEXT")
        assert errors == []

    def test_validate_marketing_invalid(self, api):
        payload = {
            "name": "",
            "category": "MARKETING",
            "language": "en",
            "components": [{"type": "body", "text": "Hello"}],
        }
        errors = api.validate_create_payload(payload, "MARKETING", "TEXT")
        assert len(errors) > 0

    def test_validate_unknown_type_passes(self, api):
        """Unknown types should pass (no validator = no errors)."""
        payload = {"name": "test", "components": []}
        errors = api.validate_create_payload(payload, "UNKNOWN", "UNKNOWN")
        assert errors == []

    def test_validate_send_unknown_passes(self, api):
        errors = api.validate_send_payload("UNKNOWN", {})
        assert errors == []


class TestMetaAPIError:
    def test_error_with_code(self):
        err = MetaAPIError("Bad request", code=400, raw={"error": {}})
        assert err.code == 400
        assert str(err) == "Bad request"

    def test_error_without_code(self):
        err = MetaAPIError("Something failed")
        assert err.code is None
        assert err.raw == {}


class TestMetaAPIRequests:
    """Test API request methods with mocked transport."""

    @pytest.mark.asyncio
    async def test_submit_template(self, api):
        mock_response = {"id": "tmpl_123", "status": "PENDING"}

        async def mock_handler(request: httpx.Request):
            return httpx.Response(200, json=mock_response)

        api._client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))

        result = await api.submit_template({
            "name": "test",
            "category": "MARKETING",
            "language": "en",
            "components": [{"type": "body", "text": "Hello"}],
        })
        assert result["id"] == "tmpl_123"
        assert result["status"] == "PENDING"
        await api.close()

    @pytest.mark.asyncio
    async def test_list_templates(self, api):
        mock_response = {
            "data": [
                {"id": "1", "name": "hello", "status": "APPROVED"},
                {"id": "2", "name": "promo", "status": "PENDING"},
            ],
            "paging": {"cursors": {"after": "cursor123"}},
        }

        async def mock_handler(request: httpx.Request):
            return httpx.Response(200, json=mock_response)

        api._client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))

        result = await api.list_templates()
        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "hello"
        await api.close()

    @pytest.mark.asyncio
    async def test_get_template(self, api):
        mock_response = {
            "id": "tmpl_123",
            "name": "hello",
            "status": "APPROVED",
            "category": "MARKETING",
        }

        async def mock_handler(request: httpx.Request):
            return httpx.Response(200, json=mock_response)

        api._client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))

        result = await api.get_template("tmpl_123")
        assert result["name"] == "hello"
        assert result["status"] == "APPROVED"
        await api.close()

    @pytest.mark.asyncio
    async def test_delete_template(self, api):
        async def mock_handler(request: httpx.Request):
            return httpx.Response(200, json={"success": True})

        api._client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))

        result = await api.delete_template("hello_world")
        assert result["success"] is True
        await api.close()

    @pytest.mark.asyncio
    async def test_send_message(self, api):
        mock_response = {
            "messaging_product": "whatsapp",
            "messages": [{"id": "wamid.abc123"}],
        }

        async def mock_handler(request: httpx.Request):
            return httpx.Response(200, json=mock_response)

        api._client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))

        result = await api.send_message({
            "messaging_product": "whatsapp",
            "to": "+919876543210",
            "type": "template",
            "template": {"name": "hello", "language": {"code": "en"}},
        })
        assert result["messages"][0]["id"] == "wamid.abc123"
        await api.close()

    @pytest.mark.asyncio
    async def test_api_error_raises(self, api):
        async def mock_handler(request: httpx.Request):
            return httpx.Response(400, json={
                "error": {"message": "Invalid token", "code": 190},
            })

        api._client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))

        with pytest.raises(MetaAPIError) as exc_info:
            await api.submit_template({"name": "test"})
        assert exc_info.value.code == 190
        assert "Invalid token" in str(exc_info.value)
        await api.close()
