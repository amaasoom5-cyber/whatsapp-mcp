"""
Tests for MCP server tools — validates tool registration and helpers.
"""

import json

import pytest

from whatsapp_mcp.server import (
    _build_template_payload,
    _normalize_components,
    _normalize_phone,
    mcp,
)


class TestHelpers:
    def test_normalize_phone_with_plus(self):
        assert _normalize_phone("+919876543210") == "+919876543210"

    def test_normalize_phone_without_plus(self):
        assert _normalize_phone("919876543210") == "+919876543210"

    def test_normalize_phone_with_spaces(self):
        assert _normalize_phone("+91 98765 43210") == "+919876543210"

    def test_normalize_phone_with_dashes(self):
        assert _normalize_phone("+91-9876-543210") == "+919876543210"

    def test_normalize_phone_with_parens(self):
        assert _normalize_phone("+1 (234) 567-8901") == "+12345678901"

    def test_normalize_components_lowercase(self):
        result = _normalize_components([
            {"type": "HEADER", "format": "TEXT", "text": "Hi"},
            {"type": "BODY", "text": "Hello"},
            {"type": "FOOTER", "text": "Bye"},
            {"type": "BUTTONS", "buttons": []},
        ])
        assert [c["type"] for c in result] == ["header", "body", "footer", "buttons"]

    def test_normalize_components_already_lowercase(self):
        result = _normalize_components([{"type": "body", "text": "Hello"}])
        assert result[0]["type"] == "body"

    def test_build_template_payload(self):
        payload = _build_template_payload(
            "test", "marketing", "en",
            [{"type": "BODY", "text": "Hello"}],
        )
        assert payload["name"] == "test"
        assert payload["category"] == "MARKETING"
        assert payload["language"] == "en"
        assert payload["components"][0]["type"] == "body"


class TestToolRegistration:
    def test_all_tools_registered(self):
        tools = list(mcp._tool_manager._tools.keys())
        expected = [
            "validate_template",
            "create_template",
            "list_templates",
            "get_template_detail",
            "check_template_status",
            "delete_template",
            "send_template_message",
            "send_bulk_template_messages",
        ]
        assert sorted(tools) == sorted(expected)

    def test_tool_count(self):
        assert len(mcp._tool_manager._tools) == 8
