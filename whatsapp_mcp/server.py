"""
WhatsApp MCP Server

Exposes WhatsApp Business API template management and messaging
as MCP tools for Claude, Cursor, VS Code Copilot, and other MCP clients.
"""

import json
import logging
import re
from typing import Any

from mcp.server.fastmcp import FastMCP

from whatsapp_mcp.config import get_config, validate_config
from whatsapp_mcp.meta_api import MetaAPI, MetaAPIError

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "WhatsApp MCP",
    instructions=(
        "Manage WhatsApp Business templates and send template messages "
        "via Meta Cloud API."
    ),
)

# ── Shared API client ────────────────────────────────────────────────

_api: MetaAPI | None = None


def _get_api() -> MetaAPI:
    """Get or create the shared MetaAPI client."""
    global _api
    if _api is None:
        config = get_config()
        validate_config(config)
        _api = MetaAPI(
            access_token=config["access_token"],
            waba_id=config["waba_id"],
            phone_number_id=config["phone_number_id"],
            app_id=config["app_id"],
            api_version=config["api_version"],
        )
    return _api


def _format_error(e: Exception) -> str:
    """Format an exception for user-friendly display."""
    if isinstance(e, MetaAPIError):
        msg = str(e)
        if e.code:
            msg = f"[Meta Error {e.code}] {msg}"
        return msg
    return str(e)


# ── Helper: build Meta payload from user-friendly input ──────────────


def _normalize_components(components: list[dict]) -> list[dict]:
    """Normalize component type fields to lowercase (Meta API format)."""
    normalized = []
    for comp in components:
        c = dict(comp)
        if "type" in c:
            c["type"] = c["type"].lower()
        normalized.append(c)
    return normalized


def _build_template_payload(
    name: str,
    category: str,
    language: str,
    components: list[dict],
) -> dict:
    """Build the Meta API payload for template creation."""
    payload: dict[str, Any] = {
        "name": name,
        "category": category.upper(),
        "language": language,
        "components": _normalize_components(components),
    }
    return payload


def _normalize_phone(phone: str) -> str:
    """Normalize a phone number: strip spaces/dashes, ensure leading +."""
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    return cleaned


# ═════════════════════════════════════════════════════════════════════
# TEMPLATE TOOLS (6)
# ═════════════════════════════════════════════════════════════════════


@mcp.tool()
async def validate_template(
    name: str,
    category: str,
    language: str,
    components: list[dict],
    template_type: str = "TEXT",
    is_lto: bool = False,
) -> str:
    """
    Validate a WhatsApp template against Meta's rules before submitting.

    Use this to check for errors before creating a template.

    Args:
        name: Template name (lowercase, underscores, starts with letter)
        category: MARKETING or UTILITY
        language: Language code (e.g. "en", "en_US", "hi")
        components: List of component dicts (HEADER, BODY, FOOTER, BUTTONS)
        template_type: TEXT, IMAGE, VIDEO, DOCUMENT, CAROUSEL, CATALOG, etc.
        is_lto: True if this is a Limited Time Offer template

    Returns:
        Validation result with any errors found.
    """
    errors = []

    # Basic name validation
    if not name:
        errors.append({"field": "name", "message": "Template name is required"})
    elif not re.match(r"^[a-z][a-z0-9_]*$", name):
        errors.append({
            "field": "name",
            "message": "Name must start with a letter, use only lowercase letters, numbers, and underscores",
        })
    elif len(name) > 512:
        errors.append({"field": "name", "message": "Name must be 512 characters or less"})

    if category.upper() not in ("MARKETING", "UTILITY"):
        errors.append({"field": "category", "message": "Category must be MARKETING or UTILITY"})

    if not components:
        errors.append({"field": "components", "message": "At least one component is required"})

    # Run Pydantic validator
    if not errors:
        payload = _build_template_payload(name, category, language, components)
        buttons = None
        for comp in components:
            if comp.get("type", "").upper() == "BUTTONS":
                buttons = comp.get("buttons", [])
                break

        api = _get_api()
        pydantic_errors = api.validate_create_payload(
            payload, category, template_type, is_lto, buttons
        )
        errors.extend(pydantic_errors)

    if errors:
        return json.dumps({
            "valid": False,
            "error_count": len(errors),
            "errors": errors,
        }, indent=2)

    return json.dumps({
        "valid": True,
        "message": "Template is valid and ready to submit.",
    }, indent=2)


@mcp.tool()
async def create_template(
    name: str,
    category: str,
    language: str,
    components: list[dict],
) -> str:
    """
    Create and submit a WhatsApp template to Meta for approval.

    The template will go through Meta's review process. Check status
    with check_template_status after submission.

    Args:
        name: Template name (lowercase, underscores, starts with letter, max 512)
        category: MARKETING or UTILITY
        language: Language code (e.g. "en", "en_US", "hi")
        components: List of component dicts. Each has a "type" (HEADER, BODY,
            FOOTER, BUTTONS) and type-specific fields. Example:
            [
                {"type": "HEADER", "format": "TEXT", "text": "Hello {{1}}",
                 "example": {"header_text": ["John"]}},
                {"type": "BODY", "text": "Your order {{1}} is {{2}}.",
                 "example": {"body_text": [["ORD-123", "confirmed"]]}},
                {"type": "FOOTER", "text": "Reply STOP to opt out"},
                {"type": "BUTTONS", "buttons": [
                    {"type": "QUICK_REPLY", "text": "Track Order"},
                    {"type": "URL", "text": "View Details",
                     "url": "https://example.com/order/{{1}}",
                     "example": ["https://example.com/order/123"]}
                ]}
            ]

    Returns:
        JSON with template ID and status on success, or error details.
    """
    try:
        api = _get_api()
        payload = _build_template_payload(name, category, language, components)
        result = await api.submit_template(payload)
        return json.dumps({
            "success": True,
            "template_id": result.get("id"),
            "status": result.get("status", "PENDING"),
            "message": f"Template '{name}' submitted for review.",
        }, indent=2)
    except MetaAPIError as e:
        return json.dumps({
            "success": False,
            "error": _format_error(e),
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": _format_error(e),
        }, indent=2)


@mcp.tool()
async def list_templates(
    limit: int = 20,
    after: str | None = None,
    name: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> str:
    """
    List WhatsApp message templates.

    Args:
        limit: Max templates to return (1-100, default 20)
        after: Pagination cursor for next page
        name: Filter by template name (exact match)
        status: Filter by status: APPROVED, PENDING, REJECTED, PAUSED, DISABLED
        category: Filter by category: MARKETING, UTILITY

    Returns:
        JSON with list of templates and pagination info.
    """
    try:
        api = _get_api()
        result = await api.list_templates(
            limit=min(max(limit, 1), 100),
            after=after,
            name=name,
            status=status,
            category=category,
        )

        templates = result.get("data", [])
        paging = result.get("paging", {})

        # Summarize for readability
        summary = []
        for t in templates:
            summary.append({
                "id": t.get("id"),
                "name": t.get("name"),
                "status": t.get("status"),
                "category": t.get("category"),
                "language": t.get("language"),
                "quality_score": t.get("quality_score"),
            })

        response: dict[str, Any] = {
            "count": len(summary),
            "templates": summary,
        }
        if paging.get("cursors", {}).get("after"):
            response["next_cursor"] = paging["cursors"]["after"]
            response["has_more"] = True

        return json.dumps(response, indent=2)

    except MetaAPIError as e:
        return json.dumps({"error": _format_error(e)}, indent=2)
    except Exception as e:
        return json.dumps({"error": _format_error(e)}, indent=2)


@mcp.tool()
async def get_template_detail(
    template_name: str | None = None,
    template_id: str | None = None,
) -> str:
    """
    Get full details of a WhatsApp template by name or ID.

    Provide either template_name or template_id (not both).

    Args:
        template_name: Template name to look up
        template_id: Meta template ID to look up directly

    Returns:
        JSON with full template details including components.
    """
    try:
        api = _get_api()

        if template_id:
            result = await api.get_template(template_id)
            return json.dumps(result, indent=2)

        if template_name:
            result = await api.list_templates(limit=100, name=template_name)
            templates = result.get("data", [])
            if not templates:
                return json.dumps({
                    "error": f"No template found with name '{template_name}'",
                }, indent=2)
            # Return all language variants
            if len(templates) == 1:
                return json.dumps(templates[0], indent=2)
            return json.dumps({
                "name": template_name,
                "variants": len(templates),
                "templates": templates,
            }, indent=2)

        return json.dumps({
            "error": "Provide either template_name or template_id.",
        }, indent=2)

    except MetaAPIError as e:
        return json.dumps({"error": _format_error(e)}, indent=2)
    except Exception as e:
        return json.dumps({"error": _format_error(e)}, indent=2)


@mcp.tool()
async def check_template_status(
    template_name: str | None = None,
    template_id: str | None = None,
) -> str:
    """
    Check the approval status of a WhatsApp template.

    Use this after creating a template to see if Meta approved or rejected it.

    Args:
        template_name: Template name to check
        template_id: Meta template ID to check directly

    Returns:
        JSON with current status (APPROVED, PENDING, REJECTED, etc.)
    """
    try:
        api = _get_api()

        if template_id:
            result = await api.get_template(template_id)
            return json.dumps({
                "name": result.get("name"),
                "status": result.get("status"),
                "quality_score": result.get("quality_score"),
                "rejected_reason": result.get("rejected_reason"),
            }, indent=2)

        if template_name:
            result = await api.list_templates(limit=100, name=template_name)
            templates = result.get("data", [])
            if not templates:
                return json.dumps({
                    "error": f"No template found with name '{template_name}'",
                }, indent=2)

            statuses = []
            for t in templates:
                statuses.append({
                    "id": t.get("id"),
                    "language": t.get("language"),
                    "status": t.get("status"),
                    "quality_score": t.get("quality_score"),
                    "rejected_reason": t.get("rejected_reason"),
                })

            if len(statuses) == 1:
                return json.dumps(statuses[0], indent=2)

            return json.dumps({
                "name": template_name,
                "statuses": statuses,
            }, indent=2)

        return json.dumps({
            "error": "Provide either template_name or template_id.",
        }, indent=2)

    except MetaAPIError as e:
        return json.dumps({"error": _format_error(e)}, indent=2)
    except Exception as e:
        return json.dumps({"error": _format_error(e)}, indent=2)


@mcp.tool()
async def delete_template(template_name: str) -> str:
    """
    Delete a WhatsApp template by name.

    WARNING: This permanently deletes ALL language variants of the template.

    Args:
        template_name: Name of the template to delete

    Returns:
        JSON confirming deletion.
    """
    try:
        api = _get_api()
        result = await api.delete_template(template_name)
        return json.dumps({
            "success": True,
            "message": f"Template '{template_name}' deleted.",
            "response": result,
        }, indent=2)
    except MetaAPIError as e:
        return json.dumps({
            "success": False,
            "error": _format_error(e),
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": _format_error(e),
        }, indent=2)


# ═════════════════════════════════════════════════════════════════════
# SENDING TOOLS (2)
# ═════════════════════════════════════════════════════════════════════


@mcp.tool()
async def send_template_message(
    to: str,
    template_name: str,
    language: str = "en",
    components: list[dict] | None = None,
) -> str:
    """
    Send an approved template message to a phone number.

    Args:
        to: Recipient phone number with country code (e.g. "+919876543210")
        template_name: Name of the approved template to send
        language: Language code matching the template (default "en")
        components: Optional list of component parameter dicts for dynamic
            values. Example for a template with header image and body params:
            [
                {"type": "header", "parameters": [
                    {"type": "image", "image": {"link": "https://example.com/img.jpg"}}
                ]},
                {"type": "body", "parameters": [
                    {"type": "text", "text": "John"},
                    {"type": "text", "text": "ORD-123"}
                ]}
            ]

    Returns:
        JSON with message ID on success.
    """
    try:
        api = _get_api()
        phone = _normalize_phone(to)

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
            },
        }
        if components:
            payload["template"]["components"] = components

        result = await api.send_message(payload)

        msg_id = None
        messages = result.get("messages", [])
        if messages:
            msg_id = messages[0].get("id")

        return json.dumps({
            "success": True,
            "message_id": msg_id,
            "to": phone,
            "template": template_name,
        }, indent=2)

    except MetaAPIError as e:
        return json.dumps({
            "success": False,
            "error": _format_error(e),
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": _format_error(e),
        }, indent=2)


@mcp.tool()
async def send_bulk_template_messages(
    to_list: list[str],
    template_name: str,
    language: str = "en",
    components: list[dict] | None = None,
) -> str:
    """
    Send an approved template message to multiple phone numbers.

    Messages are sent sequentially (one API call per recipient).
    Each result is tracked individually.

    Args:
        to_list: List of phone numbers with country code
        template_name: Name of the approved template
        language: Language code (default "en")
        components: Optional parameter components (same for all recipients)

    Returns:
        JSON with per-recipient results (successes and failures).
    """
    api = _get_api()
    results = []
    success_count = 0
    fail_count = 0

    for phone_raw in to_list:
        phone = _normalize_phone(phone_raw)
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language},
                },
            }
            if components:
                payload["template"]["components"] = components

            result = await api.send_message(payload)
            msg_id = None
            messages = result.get("messages", [])
            if messages:
                msg_id = messages[0].get("id")

            results.append({
                "to": phone,
                "success": True,
                "message_id": msg_id,
            })
            success_count += 1

        except MetaAPIError as e:
            results.append({
                "to": phone,
                "success": False,
                "error": _format_error(e),
            })
            fail_count += 1
        except Exception as e:
            results.append({
                "to": phone,
                "success": False,
                "error": str(e),
            })
            fail_count += 1

    return json.dumps({
        "total": len(to_list),
        "sent": success_count,
        "failed": fail_count,
        "results": results,
    }, indent=2)
