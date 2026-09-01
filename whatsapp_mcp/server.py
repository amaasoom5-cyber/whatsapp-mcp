"""
WhatsApp MCP Server — WATI edition.

Provides WhatsApp messaging tools through the WATI API.
"""

import json
import re

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from whatsapp_mcp.config import get_config, validate_config
from whatsapp_mcp.wati_api import WATIAPI, WATIAPIError

mcp = FastMCP(
    "WhatsApp MCP",
    instructions=(
        "Manage WhatsApp messages, contacts and approved WhatsApp "
        "templates through the WATI API."
    ),
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "whatsapp-mcp-zxaj.onrender.com",
            "whatsapp-mcp-zxaj.onrender.com:*",
            "localhost:*",
            "127.0.0.1:*",
        ],
        allowed_origins=[
            "https://whatsapp-mcp-zxaj.onrender.com",
            "https://whatsapp-mcp-zxaj.onrender.com:*",
            "http://localhost:*",
            "http://127.0.0.1:*",
        ],
    ),
)

_api: WATIAPI | None = None


def _get_api() -> WATIAPI:
    """Get or create the shared WATI API client."""
    global _api
    if _api is None:
        config = get_config()
        validate_config(config)
        _api = WATIAPI(
            api_token=config["wati_api_token"],
            api_endpoint=config["wati_api_endpoint"],
        )
    return _api


def _format_error(error: Exception) -> str:
    """Convert API exceptions to readable text."""
    if isinstance(error, WATIAPIError):
        message = str(error)
        if error.code:
            message = f"[WATI Error {error.code}] {message}"
        return message
    return str(error)


def _normalize_phone(phone: str) -> str:
    """
    Normalize a WhatsApp number.

    Example:
    +31 6 1234 5678 -> 31612345678
    """
    return re.sub(r"[\s\-\(\)+]", "", phone)


# ============================================================
# TEMPLATE TOOLS
# ============================================================


@mcp.tool()
async def list_templates(
    page_number: int = 1,
    page_size: int = 20,
    channel: str | None = None,
) -> str:
    """
    List approved/available WhatsApp templates in WATI.

    Args:
        page_number: Page number, starting at 1.
        page_size: Number of templates to return, maximum 100.
        channel: Optional WATI channel name or number.
    """
    try:
        api = _get_api()
        result = await api.list_templates(
            page_number=max(page_number, 1),
            page_size=min(max(page_size, 1), 100),
            channel=channel,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": _format_error(error),
            },
            indent=2,
        )


@mcp.tool()
async def get_template_detail(
    template_id: str,
) -> str:
    """
    Get a WhatsApp template from WATI by template ID.

    Args:
        template_id: WATI template ID.
    """
    try:
        api = _get_api()
        result = await api.get_template(template_id)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": _format_error(error),
            },
            indent=2,
        )


@mcp.tool()
async def send_template_message(
    to: str,
    template_name: str,
    parameters: list[dict] | None = None,
    broadcast_name: str = "MCP",
    channel: str | None = None,
) -> str:
    """
    Send an approved WhatsApp template through WATI.

    Args:
        to: Recipient number including country code.
        template_name: Exact WATI template name.
        parameters: Optional WATI template parameters.
        broadcast_name: Name used by WATI for this send.
        channel: Optional WATI channel name or number.
    """
    try:
        api = _get_api()
        phone = _normalize_phone(to)
        result = await api.send_template(
            phone_number=phone,
            template_name=template_name,
            parameters=parameters,
            broadcast_name=broadcast_name,
            channel=channel,
        )
        return json.dumps(
            {
                "success": True,
                "to": phone,
                "template_name": template_name,
                "wati_response": result,
            },
            indent=2,
            ensure_ascii=False,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": _format_error(error),
            },
            indent=2,
        )


# ============================================================
# CONVERSATION TOOLS
# ============================================================


@mcp.tool()
async def send_text_message(
    to: str,
    text: str,
) -> str:
    """
    Send a normal WhatsApp message to an ACTIVE WATI conversation.

    IMPORTANT:
    WhatsApp's 24-hour customer-service window applies.
    Outside an active conversation, use an approved template instead.

    Args:
        to: Recipient WhatsApp number including country code.
        text: Message to send.
    """
    try:
        if not text.strip():
            return json.dumps(
                {
                    "success": False,
                    "error": "Message text cannot be empty.",
                },
                indent=2,
            )

        api = _get_api()
        phone = _normalize_phone(to)
        result = await api.send_text_message(
            target=phone,
            text=text,
        )
        return json.dumps(
            {
                "success": True,
                "to": phone,
                "text": text,
                "wati_response": result,
            },
            indent=2,
            ensure_ascii=False,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": _format_error(error),
            },
            indent=2,
        )


@mcp.tool()
async def get_messages(
    target: str,
    page_number: int = 1,
    page_size: int = 20,
) -> str:
    """
    Get WhatsApp messages for a WATI conversation.

    target can normally be:
    - phone number
    - conversation ID
    - contact ID
    - channel:number

    Args:
        target: Conversation identifier.
        page_number: Page number starting at 1.
        page_size: Number of messages, maximum 100.
    """
    try:
        api = _get_api()
        result = await api.get_messages(
            target=target,
            page_number=max(page_number, 1),
            page_size=min(max(page_size, 1), 100),
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": _format_error(error),
            },
            indent=2,
        )


# ============================================================
# CONTACT TOOLS
# ============================================================


@mcp.tool()
async def get_contacts(
    page_number: int = 1,
    page_size: int = 100,
) -> str:
    """
    List contacts in the connected WATI account.

    Use this to discover which conversations exist, including people
    who messaged for the first time. Returns a compact list with name,
    phone number and when the contact was created or last updated.

    Args:
        page_number: Page number starting at 1.
        page_size: Number of contacts, maximum 100.
    """
    try:
        api = _get_api()
        result = await api.get_contacts(
            page_number=max(page_number, 1),
            page_size=min(max(page_size, 1), 100),
        )

        raw_contacts = []
        if isinstance(result, dict):
            raw_contacts = (
                result.get("contact_list")
                or result.get("contacts")
                or result.get("items")
                or []
            )

        contacts = []
        for entry in raw_contacts:
            if not isinstance(entry, dict):
                continue
            contacts.append(
                {
                    "name": (
                        entry.get("fullName")
                        or entry.get("full_name")
                        or entry.get("name")
                        or entry.get("wAid")
                        or entry.get("phone")
                    ),
                    "phone": (
                        entry.get("wAid")
                        or entry.get("wa_id")
                        or entry.get("phone")
                    ),
                    "status": (
                        entry.get("contactStatus")
                        or entry.get("contact_status")
                    ),
                    "source": entry.get("source"),
                    "created": entry.get("created"),
                    "last_updated": (
                        entry.get("lastUpdated")
                        or entry.get("last_updated")
                    ),
                }
            )

        link = {}
        if isinstance(result, dict):
            link = result.get("link") or {}

        return json.dumps(
            {
                "success": True,
                "contacts": contacts,
                "total": link.get("total", len(contacts)),
                "page_number": page_number,
                "page_size": page_size,
            },
            indent=2,
            ensure_ascii=False,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": _format_error(error),
            },
            indent=2,
        )


@mcp.tool()
async def get_contact(
    target: str,
) -> str:
    """
    Get one contact's full profile from WATI.

    Args:
        target: ContactId, phone number with country code,
            or a channel-scoped identifier (channel:phone).
    """
    try:
        api = _get_api()
        result = await api.get_contact(_normalize_phone(target))
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": _format_error(error),
            },
            indent=2,
        )


@mcp.tool()
async def get_contact_count() -> str:
    """
    Get the total number of contacts in the WATI account.

    Useful as a quick check for whether new contacts appeared.
    """
    try:
        api = _get_api()
        result = await api.get_contact_count()
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": _format_error(error),
            },
            indent=2,
        )


@mcp.tool()
async def add_contact(
    phone_number: str,
    name: str | None = None,
    custom_params: dict | None = None,
) -> str:
    """
    Create or update a contact in WATI.

    WRITES data to the WATI account — confirm the number and details
    with the user before calling.

    Args:
        phone_number: WhatsApp number including country code.
        name: Optional display name for the contact.
        custom_params: Optional custom attributes, for example
            {"lead_stage": "New Lead"}.
    """
    try:
        api = _get_api()
        phone = _normalize_phone(phone_number)
        result = await api.add_contact(
            phone_number=phone,
            name=name,
            custom_params=custom_params,
        )
        return json.dumps(
            {
                "success": True,
                "phone": phone,
                "name": name,
                "wati_response": result,
            },
            indent=2,
            ensure_ascii=False,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": _format_error(error),
            },
            indent=2,
        )


# ============================================================
# HEALTH / CONNECTION CHECK
# ============================================================


@mcp.tool()
async def test_wati_connection() -> str:
    """
    Test whether the configured WATI token and endpoint work.

    Makes a small template-list request.
    """
    try:
        api = _get_api()
        result = await api.list_templates(
            page_number=1,
            page_size=1,
        )
        return json.dumps(
            {
                "success": True,
                "message": "WATI connection is working.",
                "response": result,
            },
            indent=2,
            ensure_ascii=False,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "message": "WATI connection failed.",
                "error": _format_error(error),
            },
            indent=2,
        )
